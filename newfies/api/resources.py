import logging

from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseNotFound

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie.utils import dict_strip_unicode_keys, trailing_slash
from tastypie.http import HttpCreated, HttpNoContent, HttpNotFound, HttpBadRequest
from tastypie.exceptions import BadRequest, NotFound, ImmediateHttpResponse
from tastypie import http

from dialer_campaign.models import Campaign, Phonebook, Contact, CampaignSubscriber
from dialer_cdr.models import Callrequest, VoIPCall
from dialer_gateway.models import Gateway
from voip_app.models import VoipApp
#from common.custom_xml_emitter import *

from tastypie import fields
from dialer_campaign.function_def import user_attached_with_dialer_settings, \
    check_dialer_setting, dialer_setting_limit

from datetime import datetime
from random import choice, seed

import time
import uuid
import simplejson


try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
from django.utils.encoding import smart_unicode
from django.utils.xmlutils import SimplerXMLGenerator
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.conf import settings

seed()

logger = logging.getLogger('newfies.filelog')


def get_attribute(attrs, attr_name):
    """this is a helper to retrieve an attribute if it exists"""
    if attr_name in attrs:
        attr_value = attrs[attr_name]
    else:
        attr_value = None
    return attr_value


def get_value_if_none(x, value):
    """return value if x is None"""
    if x is None:
        return value
    return x


class VoipAppResource(ModelResource):
    class Meta:
        queryset = VoipApp.objects.all()
        resource_name = 'voipapp'


class GatewayResource(ModelResource):
    class Meta:
        queryset = Gateway.objects.all()
        resource_name = 'gateway'


class UserResource(ModelResource):
    class Meta:
        allowed_methods = ['get']
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'last_login', 'id']
        filtering = {
            'username': 'exact',
        }
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

        
class CampaignValidation(Validation):
    """
    Campaign Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}
        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        startingdate = bundle.data.get('startingdate')
        expirationdate = bundle.data.get('expirationdate')
        if request.method == 'POST':
            startingdate = get_value_if_none(startingdate, time.time())
            # expires in 7 days
            expirationdate = get_value_if_none(expirationdate, time.time() + 86400 * 7)

            bundle.data['startingdate'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                          time.gmtime(float(startingdate)))
            bundle.data['expirationdate'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.gmtime(float(expirationdate)))

        if request.method == 'PUT':
            if startingdate:
                bundle.data['startingdate'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.gmtime(float(startingdate)))
            if expirationdate:
                bundle.data['expirationdate'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                time.gmtime(float(expirationdate)))
        
        if user_attached_with_dialer_settings(request):
            errors['user_dialer_setting'] = ['Your settings are not \
                        configured properly, Please contact the administrator.']

        if check_dialer_setting(request, check_for="campaign"):
            errors['chk_campaign'] = ["You have too many campaigns. Max allowed %s" \
            % dialer_setting_limit(request, limit_for="campaign")]


        frequency = bundle.data.get('frequency')
        if frequency:
            if check_dialer_setting(request, check_for="frequency",
                                        field_value=int(frequency)):
                errors['chk_frequency'] = ["Maximum Frequency limit of %s exceeded." \
                % dialer_setting_limit(request, limit_for="frequency")]

        callmaxduration = bundle.data.get('callmaxduration')
        if callmaxduration:
            if check_dialer_setting(request,
                                    check_for="duration",
                                    field_value=int(callmaxduration)):
                errors['chk_duration'] = ["Maximum Duration limit of %s exceeded." \
                % dialer_setting_limit(request, limit_for="duration")]

        maxretry = bundle.data.get('maxretry')
        if maxretry:
            if check_dialer_setting(request,
                                    check_for="retry",
                                    field_value=int(maxretry)):
                errors['chk_duration'] = ["Maximum Retries limit of %s exceeded." \
                % dialer_setting_limit(request, limit_for="retry")]

        calltimeout = bundle.data.get('calltimeout')
        if calltimeout:
            if check_dialer_setting(request,
                                    check_for="timeout",
                                    field_value=int(calltimeout)):
                errors['chk_timeout'] = ["Maximum Timeout limit of %s exceeded." \
                % dialer_setting_limit(request, limit_for="timeout")]

        aleg_gateway_id = bundle.data.get('aleg_gateway')
        if aleg_gateway_id:
            try:
                aleg_gateway_id = Gateway.objects.get(id=aleg_gateway_id).id
                bundle.data['aleg_gateway'] = '/api/v1/gateway/%s/' % aleg_gateway_id
            except:
                errors['chk_gateway'] = ["The Gateway ID doesn't exist!"]

        voipapp_id = bundle.data.get('voipapp')
        if voipapp_id:
            try:
                voip_app_id = VoipApp.objects.get(id=voipapp_id).id
                bundle.data['voipapp'] = '/api/v1/voipapp/%s/' % voip_app_id
            except:
                errors['chk_voipapp'] = ["The VoipApp doesn't exist!"]

        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        if request.method=='POST':
            name_count = Campaign.objects.filter(name=bundle.data.get('name'),
                                                 user=request.user).count()
            if (name_count!=0):
                errors['chk_campaign_name'] = ["The Campaign name duplicated!"]

        return errors

    
class CampaignResource(ModelResource):
    """
    **Attributes**:

            * ``campaign_code`` - Autogenerate campaign code
            * ``name`` - Name of the Campaign
            * ``description`` - Short description of the Campaign
            * ``callerid`` - Caller ID
            * ``startingdate`` - Start date. Epoch Time, ie 1301414368
            * ``expirationdate`` - Expiry date. Epoch Time, ie 1301414368
            * ``daily_start_time`` - Daily start time, default '00:00:00'
            * ``daily_stop_time`` - Daily stop time, default '23:59:59'
            * ``monday`` - Set to 1 if you want to run this day of the week,\
            default '1'
            * ``tuesday`` - Set to 1 if you want to run this day of the week,\
            default '1'
            * ``wednesday`` - Set to 1 if you want to run this day of the week\
            , default '1'
            * ``thursday`` - Set to 1 if you want to run this day of the week,\
            default '1'
            * ``friday`` - Set to 1 if you want to run this day of the week,\
            default '1'
            * ``saturday`` - Set to 1 if you want to run this day of the week,\
            default '1'
            * ``sunday`` - Set to 1 if you want to run this day of the week,\
            default '1'

        **Campaign Settings**:

            * ``frequency`` - Defines the frequency, speed of the campaign.\
                              This is the number of calls per minute.
            * ``callmaxduration`` - Maximum call duration.
            * ``maxretry`` - Defines the max retries allowed per user.
            * ``intervalretry`` - Defines the time to wait between retries\
                                  in seconds
            * ``calltimeout`` - Defines the number of seconds to timeout on calls

        **Gateways**:

            * ``aleg_gateway`` - Defines the Gateway to use to call the\
                                 subscriber
            * ``voipapp`` - Defines the  application to use when the \
                            call is established on the A-Leg
            * ``extra_data`` - Defines the additional data to pass to the\
                                 application

    **Validation**:

        * CampaignValidation()
    
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "mycampaign", "description": "", "callerid": "1239876", "startingdate": "1301392136.0", "expirationdate": "1301332136.0", "frequency": "20", "callmaxduration": "50", "maxretry": "3", "intervalretry": "3000", "calltimeout": "45", "aleg_gateway": "1", "voipapp": "1", "extra_data": "2000"}' http://localhost:8000/api/v1/campaign/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/app/campaign/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/campaign/?format=json

        Response::

            {
               "meta":{
                  "limit":20,
                  "next":null,
                  "offset":0,
                  "previous":null,
                  "total_count":1
               },
               "objects":[
                  {
                     "callerid":"123987",
                     "callmaxduration":1800,
                     "calltimeout":45,
                     "campaign_code":"XIUER",
                     "created_date":"2011-06-15T00:49:16",
                     "daily_start_time":"00:00:00",
                     "daily_stop_time":"23:59:59",
                     "description":"",
                     "expirationdate":"2011-06-22T00:01:15",
                     "extra_data":"",
                     "frequency":10,
                     "friday":true,
                     "id":"1",
                     "intervalretry":3,
                     "maxretry":3,
                     "monday":true,
                     "name":"Default_Campaign",
                     "resource_uri":"/api/app/campaign/1/",
                     "saturday":true,
                     "startingdate":"2011-06-15T00:01:15",
                     "status":1,
                     "sunday":true,
                     "thursday":true,
                     "tuesday":true,
                     "updated_date":"2011-06-15T00:49:16",
                     "wednesday":true
                  }
               ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"name": "mylittlecampaign", "description": "", "callerid": "1239876", "startingdate": "1301392136.0", "expirationdate": "1301332136.0","frequency": "20", "callmaxduration": "50", "maxretry": "3", "intervalretry": "3000", "calltimeout": "60", "aleg_gateway": "1", "voipapp": "1", "extra_data": "2000" }' http://localhost:8000/api/v1/campaign/%campaign_id%/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us


    **Delete**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/campaign/%campaign_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/campaign/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    **Search**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/campaign/?name=mycampaign2

        Response::

            {
               "meta":{
                  "limit":20,
                  "next":null,
                  "offset":0,
                  "previous":null,
                  "total_count":1
               },
               "objects":[
                  {
                     "aleg_gateway":{

                        "created_date":"2011-06-15T00:28:52",
                        "description":"",
                        "id":"1",
                        "maximum_call":null,
                        "name":"Default_Gateway",
                     },
                     "callerid":"1239876",
                     "callmaxduration":50,
                     "calltimeout":45,
                     "campaign_code":"DJZVK",
                     "created_date":"2011-10-13T02:06:22",
                     "daily_start_time":"00:00:00",
                     "daily_stop_time":"23:59:59",
                     "description":"",
                     "expirationdate":"2011-03-28T17:08:56",
                     "extra_data":"2000",
                     "frequency":20,
                     "friday":true,
                     "id":"16",
                     "intervalretry":3000,
                     "maxretry":3,
                     "monday":true,
                     "name":"mycampaign2",
                     "resource_uri":"/api/v1/campaign/16/",
                     "saturday":true,
                     "startingdate":"2011-03-29T09:48:56",
                     "status":2,
                     "sunday":true,
                     "thursday":true,
                     "tuesday":true,
                     "updated_date":"2011-10-13T02:06:22",
                     "user":{
                        "id":"1",
                        "username":"areski"
                     },
                     "voipapp":{
                        "id":"1",
                        "name":"Default_VoIP_App",
                     },
                     "wednesday":true
                  }
               ]
            }
    """
    user = fields.ForeignKey(UserResource, 'user', full=True)
    aleg_gateway = fields.ForeignKey(GatewayResource, 'aleg_gateway', full=True)
    voipapp = fields.ForeignKey(VoipAppResource, 'voipapp', full=True)
    class Meta:
        queryset = Campaign.objects.all()
        resource_name = 'campaign'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = CampaignValidation()
        filtering = {
            'name': ALL,
            'status': ALL,
        }
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        logger.debug('Campaign API get called')

        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        bundle = self.full_hydrate(bundle)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        bundle.obj.save()

        try:
            # New phonebook
            new_phonebook = Phonebook.objects.create(user=request.user,
                                    name=bundle.obj.name + '-' + bundle.obj.campaign_code,
                                    description='Auto created Phonebook from API')
            bundle.obj.phonebook.add(new_phonebook)
            bundle.obj.save()
        except:
            #raise
            error_msg = 'The Autogenerated Phonebook name duplicated - Internal Error!'
            logger.error(error_msg)
            raise BadRequest(error_msg)

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        logger.debug('Campaign API : Result ok 200')
        return bundle


class PhonebookValidation(Validation):
    """Phonebook Validation Class"""
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']
            
        if request.method == 'POST':
            campaign_id = bundle.data.get('campaign_id')
            if campaign_id:
                try:
                    campaign = Campaign.objects.get(id=campaign_id)
                except:
                    errors['chk_campaign'] = ['The Campaign ID does not exist!']

        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        return errors


class PhonebookResource(ModelResource):
    """
    **Attributes**:

        * ``name`` - Name of the Phonebook
        * ``description`` - Short description of the Campaign
        * ``campaign_id`` - Campaign ID

    **Validation**:

        * PhonebookValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "mylittlephonebook", "description": "", "campaign_id": "1"}' http://localhost:8000/api/v1/phonebook/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/app/phonebook/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/phonebook/?format=json

        Response::

            {
               "meta":{
                  "limit":20,
                  "next":null,
                  "offset":0,
                  "previous":null,
                  "total_count":1
               },
               "objects":[
                  {
                     "created_date":"2011-04-08T07:55:05",
                     "description":"This is default phone book",
                     "id":"1",
                     "name":"Default_Phonebook",
                     "resource_uri":"/api/v1/phonebook/1/",
                     "updated_date":"2011-04-08T07:55:05",
                     "user":{                                                                      
                        "first_name":"",
                        "id":"1",
                        "last_login":"2011-10-11T01:03:42",
                        "last_name":"",
                        "resource_uri":"/api/v1/user/1/",
                        "username":"areski"
                     }
                  }
               ]
            }


    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"name": "myphonebook", "description": ""}' http://localhost:8000/api/v1/phonebook/%phonebook_id%/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us


    **Delete**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/phonebook/%phonebook_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/phonebook/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    **Search**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/phonebook/?name=myphonebook
    """
    user = fields.ForeignKey(UserResource, 'user', full=True)
    class Meta:
        queryset = Phonebook.objects.all()
        resource_name = 'phonebook'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = PhonebookValidation()
        filtering = {
            'name': ALL,
        }
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour


class BulkContactValidation(Validation):
    """BulkContact Validation Class"""
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']
            
        if check_dialer_setting(request, check_for="contact"):
            errors['contact_dialer_setting'] = ["You have too many contacts per campaign. \
                You are allowed a maximum of %s" % dialer_setting_limit(request, limit_for="contact")]

        phonebook_id = bundle.data.get('phonebook_id')
        if phonebook_id:
            try:
                obj_phonebook = Phonebook.objects.get(id=phonebook_id)
            except Phonebook.DoesNotExist:
                errors['phonebook_error'] = ["Phonebook is not selected!"]
        else:
            errors['phonebook_error'] = ["Phonebook is not selected!"]

        return errors

    
class BulkContactResource(ModelResource):
    """API to bulk create contacts

    **Attributes**

        * ``contact`` - contact number of the Subscriber
        * ``phonebook_id`` - the phonebook Id to which we want to add\
        the contact

    **Validation**:

        * BulkContactValidation()

    **CURL Usage**::

        curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"phonebook_id": "1", "phoneno_list" : "12345,54344"}' http://localhost:8000/api/v1/bulkcontact/

    **Response**::

        HTTP/1.0 201 CREATED
        Date: Thu, 13 Oct 2011 11:42:44 GMT
        Server: WSGIServer/0.1 Python/2.7.1+
        Vary: Accept-Language, Cookie
        Content-Type: text/html; charset=utf-8
        Location: http://localhost:8000/api/v1/bulkcontact/None/
        Content-Language: en-us
    """
    class Meta:
        queryset = Contact.objects.all()
        resource_name = 'bulkcontact'
        authorization = Authorization()
        authentication = BasicAuthentication()
        allowed_methods = ['post']
        validation = BulkContactValidation()
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        logger.debug('BulkContact API get called')

        bundle.obj = self._meta.object_class()
        bundle = self.full_hydrate(bundle)
        
        phoneno_list = bundle.data.get('phoneno_list')
        phonebook_id = bundle.data.get('phonebook_id')
        phonenolist = list(phoneno_list.split(","))
        total_no = len(list(phonenolist))

        try:
            obj_phonebook = Phonebook.objects.get(id=phonebook_id)
            new_contact_count = 0
            for phoneno in phonenolist:
                new_contact = Contact.objects.create(
                                        phonebook=obj_phonebook,
                                        contact=phoneno,)
                new_contact_count = new_contact_count + 1
                new_contact.save()
        except:
            error_msg = "The contact duplicated (%s)!\n" % phoneno
            logger.error(error_msg)
            raise BadRequest(error_msg)

        logger.debug('BulkContact API : result ok 200')
        return bundle



class CampaignDeleteCascadeResource(ModelResource):
    """

    **Attributes**:

        * ``campaign_id`` - Campaign ID

    **CURL Usage**::

        curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/campaign_delete_cascade/%campaign_id%/

    **Example Response**::

        HTTP/1.0 204 NO CONTENT
        Date: Wed, 18 May 2011 13:23:14 GMT
        Server: WSGIServer/0.1 Python/2.6.2
        Vary: Authorization
        Content-Length: 0
        Content-Type: text/plain
    """
    class Meta:
        queryset = Campaign.objects.all()
        resource_name = 'campaign_delete_cascade'
        authorization = Authorization()
        authentication = BasicAuthentication()
        list_allowed_methods = ['delete']
        detail_allowed_methods = ['delete']
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

    def obj_delete(self, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_delete``.

        Takes optional ``kwargs``, which are used to narrow the query to find
        the instance.
        """
        logger.debug('CampaignDeleteCascade API get called')

        obj = kwargs.pop('_obj', None)
        if not hasattr(obj, 'delete'):
            try:
                obj = self.obj_get(request, **kwargs)
            except:
                error_msg = "A model instance matching the provided arguments could not be found."
                logger.error(error_msg)
                raise NotFound(error_msg)

        #obj.delete()
        campaign_id = obj.id
        try:
            del_campaign = Campaign.objects.get(id=campaign_id)
            phonebook_count = del_campaign.phonebook.all().count()

            if phonebook_count == 0:
                del_campaign.delete()
            else: # phonebook_count > 0
                other_campaing_count = \
                Campaign.objects.filter(user=request.user,
                         phonebook__in=del_campaign.phonebook.all())\
                .exclude(id=campaign_id).count()

                if other_campaing_count == 0:
                    # delete phonebooks as well as contacts belong to it

                    # 1) delete all contacts which are belong to phonebook
                    contact_list = Contact.objects\
                    .filter(phonebook__in=del_campaign.phonebook.all())
                    total_contact = contact_list.count()
                    contact_list.delete()

                    # 2) delete phonebook
                    phonebook_list = Phonebook.objects\
                    .filter(id__in=del_campaign.phonebook.all())
                    total_phonebook = phonebook_list.count()
                    phonebook_list.delete()

                    # 3) delete campaign
                    del_campaign.delete()
                else:
                    del_campaign.delete()
                logger.debug('CampaignDeleteCascade API : result ok 200')
        except:
            error_msg = "A model instance matching the provided arguments could not be found."
            logger.error(error_msg)
            raise NotFound(error_msg)


class CampaignSubscriberValidation(Validation):
    """CampaignSubscriber Validation Class"""
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']
            
        if check_dialer_setting(request, check_for="contact"):
            errors['contact_dialer_setting'] = ["You have too many contacts per campaign. \
                You are allowed a maximum of %s" % dialer_setting_limit(request, limit_for="contact")]

        if request.method=='POST':
            phonebook_id = bundle.data.get('phonebook_id')
            if phonebook_id:
                try:
                    obj_phonebook = Phonebook.objects.get(id=phonebook_id)
                except Phonebook.DoesNotExist:
                    errors['phonebook_error'] = ["Phonebook is not selected!"]
            else:
                errors['phonebook_error'] = ["Phonebook is not selected!"]

            contact_count = Contact.objects.filter(contact=bundle.data.get('contact')).count()
            if (contact_count!=0):
                errors['chk_contact_no'] = ["The Contact no is duplicated!"]
        
        return errors


class CampaignSubscriberResource(ModelResource):
    """
    **Attributes Details**:

        * ``contact`` - contact number of the Subscriber
        * ``last_name`` - last name of the Subscriber
        * ``first_name`` - first name of the Subscriber
        * ``email`` - email id of the Subscriber
        * ``description`` - Short description of the Subscriber
        * ``additional_vars`` - Additional settings for the Subscriber
        * ``phonebook_id`` - the phonebook Id to which we want to add\
        the Subscriber

    **Validation**:

        * CampaignSubscriberValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"contact": "650784355", "last_name": "belaid", "first_name": "areski", "email": "areski@gmail.com", "phonebook_id" : "1"}' http://localhost:8000/api/v1/campaignsubscriber/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Wed, 18 May 2011 13:23:14 GMT
            Server: WSGIServer/0.1 Python/2.6.2
            Vary: Authorization
            Content-Length: 0
            Content-Type: text/plain

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/campaignsubscriber/?format=json

                or

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/campaignsubscriber/%campaign_id%/?format=json

        Response:


    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"status": "2", "contact": "123546"}' http://localhost:8000/api/v1/campaignsubscriber/%campaign_id%/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    class Meta:
        queryset = CampaignSubscriber.objects.all()
        resource_name = 'campaignsubscriber'
        authorization = Authorization()
        authentication = BasicAuthentication()
        list_allowed_methods = ['get', 'post', 'put']
        detail_allowed_methods = ['get', 'post', 'put']
        validation = CampaignSubscriberValidation()
        filtering = {
            'contact': 'exact',
        }
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

    def get_object_list(self, request):
        """
        An ORM-specific implementation of ``get_object_list``.

        Returns a queryset that may have been limited by other overrides.
        """
        logger.debug('CampaignSubscriber GET API get called')

        temp_url = request.META['PATH_INFO']
        temp_id = temp_url.split('/api/v1/campaignsubscriber/')[1]
        camp_id = temp_id.split('/')[0]
        #contact = temp_id.split('/')[1]

        from django.db import connection, transaction
        cursor = connection.cursor()

        campaign_id = int(camp_id)
        contact = ''

        if not campaign_id:
            error_msg = "No value for Campaign ID !"
            logger.error(error_msg)
            raise BadRequest(error_msg)

        if contact:
            if not isint(contact):
                error_msg = "Wrong value for contact !"
                logger.error(error_msg)
                raise BadRequest(error_msg)

            sql_statement = 'SELECT contact_id, last_attempt, count_attempt,'\
                    'dialer_campaign_subscriber.status '\
                    'FROM dialer_campaign_subscriber '\
                    'LEFT JOIN dialer_callrequest ON '\
                    'campaign_subscriber_id=dialer_campaign_subscriber.id '\
                    'LEFT JOIN dialer_campaign ON '\
                    'dialer_callrequest.campaign_id=dialer_campaign.id '\
                    'WHERE dialer_campaign_subscriber.campaign_id = %s '\
                    'AND dialer_campaign_subscriber.duplicate_contact = "%s"'\
                    % (str(campaign_id), str(contact))

        else:
            sql_statement = 'SELECT contact_id, last_attempt, count_attempt,'\
                        'dialer_campaign_subscriber.status '\
                        'FROM dialer_campaign_subscriber '\
                        'LEFT JOIN dialer_callrequest ON '\
                        'campaign_subscriber_id=' \
                        'dialer_campaign_subscriber.id '\
                        'LEFT JOIN dialer_campaign ON '\
                        'dialer_callrequest.campaign_id=dialer_campaign.id '\
                        'WHERE dialer_campaign_subscriber.campaign_id' \
                        '= %s' % (str(campaign_id))

        cursor.execute(sql_statement)
        row = cursor.fetchall()

        result = []
        result_string = ''
        limit = list(row).__len__()
        i = 0
        for record in row:
            modrecord = {}
            modrecord['contact_id'] = record[0]
            modrecord['last_attempt'] = record[1]
            modrecord['count_attempt'] = record[2]
            modrecord['status'] = record[3]
            result.append(modrecord)
            if i == (limit - 1):
                result_string = str(result_string) + str(record[0])
            else:
                result_string = str(result_string) + str(record[0]) + ', '

        result_string = result_string
        #print self._meta.queryset.filter(contact__in=[result_string])
        logger.debug('CampaignSubscriber GET API : result ok 200')
        try:
            return self._meta.queryset.filter(contact__in=[result_string])._clone()
        except:
            return self._meta.queryset._clone()
    
    def obj_create(self, bundle, request=None, **kwargs):

        logger.debug('CampaignSubscriber POST API get called')

        phonebook_id = bundle.data.get('phonebook_id')
        obj_phonebook = Phonebook.objects.get(id=phonebook_id)
        
        #this method will also create a record into CampaignSubscriber
        #this is defined in signal post_save_add_contact
        new_contact = Contact.objects.create(
                                contact=bundle.data.get('contact'),
                                last_name=bundle.data.get('last_name'),
                                first_name=bundle.data.get('first_name'),
                                email=bundle.data.get('email'),
                                description=bundle.data.get('description'),
                                status=1, # default active
                                phonebook=obj_phonebook)

        logger.debug('CampaignSubscriber POST API : result ok 200')
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_update``.
        """
        logger.debug('CampaignSubscriber PUT API get called')

        if not bundle.obj or not bundle.obj.pk:
            # Attempt to hydrate data from kwargs before doing a lookup for the object.
            # This step is needed so certain values (like datetime) will pass model validation.
            try:
                bundle.obj = self.get_object_list(request).model()
                bundle.data.update(kwargs)
                bundle = self.full_hydrate(bundle)
                lookup_kwargs = kwargs.copy()
                lookup_kwargs.update(dict(
                    (k, getattr(bundle.obj, k))
                    for k in kwargs.keys()
                    if getattr(bundle.obj, k) is not None))
            except:
                # if there is trouble hydrating the data, fall back to just
                # using kwargs by itself (usually it only contains a "pk" key
                # and this will work fine.
                lookup_kwargs = kwargs
            try:
                bundle.obj = self.obj_get(request, **lookup_kwargs)
            except ObjectDoesNotExist:
                error_msg = "A model instance matching the provided arguments could not be found."
                logger.error(error_msg)
                raise NotFound(error_msg)

        bundle = self.full_hydrate(bundle)

        campaign_id = int(bundle.data.get('pk'))
        camaign_obj = Campaign.objects.get(id=campaign_id)
        try:
            campaignsubscriber = \
            CampaignSubscriber.objects.get(duplicate_contact=bundle.data.get('contact'),
                                           campaign=camaign_obj)
            campaignsubscriber.status = bundle.data.get('status')
            campaignsubscriber.save()
        except:
            error_msg = "A model instance matching the provided arguments could not be found."
            logger.error(error_msg)
            raise NotFound(error_msg)

        logger.debug('CampaignSubscriber PUT API : result ok 200')
        return bundle


class CallrequestValidation(Validation):
    """
    Callrequest Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        voipapp_id = bundle.data.get('voipapp')
        if voipapp_id:
            try:
                voip_app_id = VoipApp.objects.get(id=voipapp_id).id
                bundle.data['voipapp'] = '/api/v1/voipapp/%s/' % voip_app_id
            except:
                errors['chk_voipapp'] = ["The VoipApp doesn't exist!"]
                
        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        if request.method=='POST':
            rq_count = Callrequest.objects.filter(request_uuid=bundle.data.get('request_uuid')).count()
            if (rq_count!=0):
                errors['chk_request_uuid'] = ["The Request uuid duplicated!"]

        return errors


class CallrequestResource(ModelResource):
    """
    **Attributes**:

        * ``callrequest_id``- Callrequest Id
        * ``request_uuid`` -
        * ``call_time`` -
        * ``call_type`` -
        * ``timeout`` -
        * ``timelimit`` -
        * ``status`` -
        * ``campaign_subscriber`` -
        * ``campaign`` -
        * ``voipapp`` -
        * ``callerid`` -
        * ``phone_number`` -
        * ``extra_dial_string`` -
        * ``extra_data`` -
        * ``num_attempt`` -
        * ``last_attempt_time`` -
        * ``result`` -
        * ``hangup_cause`` -
        * ``last_attempt_time`` -

    **Validation**:

        * CallrequestValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"request_uuid": "2342jtdsf-00123", "call_time": "2011-10-20 12:21:22", "phone_number": "8792749823", "voipapp": "1","timeout": "30000", "callerid": "650784355", "call_type": "1"}' http://localhost:8000/api/v1/callrequest/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/app/campaign/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/callrequest/?format=json

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/callrequest/%callreq_id%/?format=json

        Response::

            {
               "meta":{
                  "limit":20,
                  "next":null,
                  "offset":0,
                  "previous":null,
                  "total_count":1
               },
               "objects":[
                  {
                     "call_time":"2011-10-20T12:21:22",
                     "call_type":1,
                     "callerid":"650784355",
                     "created_date":"2011-10-14T07:33:41",
                     "extra_data":"",
                     "extra_dial_string":"",
                     "hangup_cause":"",
                     "id":"1",
                     "last_attempt_time":null,
                     "num_attempt":0,
                     "phone_number":"8792749823",
                     "request_uuid":"2342jtdsf-00123",
                     "resource_uri":"/api/v1/callrequest/1/",
                     "result":"",
                     "status":1,
                     "timelimit":3600,
                     "timeout":30000,
                     "updated_date":"2011-10-14T07:33:41",
                     "user":{
                        "first_name":"",
                        "id":"1",
                        "last_login":"2011-10-11T01:03:42",
                        "last_name":"",
                        "resource_uri":"/api/v1/user/1/",
                        "username":"areski"
                     },
                     "voipapp":{
                        "created_date":"2011-04-08T08:00:09",
                        "data":"",
                        "description":"",
                        "id":"1",
                        "name":"Default_VoIP_App",
                        "resource_uri":"/api/v1/voipapp/1/",
                        "type":1,
                        "updated_date":"2011-10-14T07:33:41"
                     }
                  }
               ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"status": "5"}' http://localhost:8000/api/v1/callrequest/%callrequest_id%/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    user = fields.ForeignKey(UserResource, 'user', full=True)
    voipapp = fields.ForeignKey(VoipAppResource, 'voipapp', full=True)

    class Meta:
        queryset = Callrequest.objects.all()
        resource_name = 'callrequest'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = CallrequestValidation()
        list_allowed_methods = ['get', 'post', 'put']
        detail_allowed_methods = ['get', 'post', 'put']
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour


class AnswercallValidation(Validation):
    """
    Answercall Validation Class
    """
    def is_valid(self, request=None):
        errors = {}
        
        opt_ALegRequestUUID = request.POST.get('ALegRequestUUID')
        
        if not opt_ALegRequestUUID:
            errors['ALegRequestUUID'] = ["Wrong parameters - missing ALegRequestUUID!"]

        try:
            obj_callrequest = Callrequest.objects.get(request_uuid=opt_ALegRequestUUID)
            if not obj_callrequest.voipapp:
                errors['VoIP App'] = ['This Call Request is not attached to a VoIP App!']
        except:
            errors['ALegRequestUUID'] = ['Call Request cannot be found!']
                
        return errors

    
class CustomXmlEmitter():
    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                self._to_xml(xml, item)
        elif isinstance(data, dict):
            for key, value in data.iteritems():
                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key.split()[0])
        else:
            xml.characters(smart_unicode(data))

    def render(self, request, data):
        stream = StringIO.StringIO()
        xml = SimplerXMLGenerator(stream, "utf-8")
        xml.startDocument()
        xml.startElement("Response", {})
        self._to_xml(xml, data)
        xml.endElement("Response")
        xml.endDocument()
        return stream.getvalue()

class AnswercallResource(ModelResource):
    """
    **Attributes**:

        * ``RequestUUID`` - A unique identifier for the API request.

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data "ALegRequestUUID=48092924-856d-11e0-a586-0147ddac9d3e" http://localhost:8000/api/v1/answercall/

        Response::

            HTTP/1.0 200 OK
            Date: Tue, 01 Nov 2011 11:30:59 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: application/json
            Content-Language: en-us

            <?xml version="1.0" encoding="utf-8"?>
                <Response>
                    <Dial timeLimit="3600" callerId="650784355">
                        <Number gateways="user/,user" gatewayTimeouts="30000"></Number>
                    </Dial>
                </Response>
    """
    class Meta:
        resource_name = 'answercall'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = AnswercallValidation()
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

    def override_urls(self):

        return [
            url(r'^(?P<resource_name>%s)/$' % self._meta.resource_name, self.wrap_view('create')),
        ]

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        
        desired_format = self.determine_format(request)
        serialized = data #self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=desired_format, **response_kwargs)

    def create(self, request=None, **kwargs):

        errors = self._meta.validation.is_valid(request)
        
        if not errors:
            logger.debug('Answercall API get called!')

            opt_ALegRequestUUID = request.POST.get('ALegRequestUUID')

            #TODO: If we update the Call to success here we should not do it in hangup url
            obj_callrequest = Callrequest.objects.get(request_uuid=opt_ALegRequestUUID)
            
            #TODO : use constant
            Callrequest.status = 8 # IN-PROGRESS
            obj_callrequest.save()

            # get the VoIP application
            if obj_callrequest.voipapp.type == 1:
                #Dial
                timelimit = obj_callrequest.timelimit
                callerid = obj_callrequest.callerid
                gatewaytimeouts = obj_callrequest.timeout
                gateways = obj_callrequest.voipapp.gateway.gateways
                dial_command = 'Dial timeLimit="%s" callerId="%s"' % \
                                    (timelimit, callerid)
                number_command = 'Number gateways="%s" gatewayTimeouts="%s"' % \
                                    (gateways, gatewaytimeouts)

                object_list = [ {dial_command: {number_command: obj_callrequest.voipapp.data}, },]
                logger.debug('Diale command')

            elif obj_callrequest.voipapp.type == 2:
                #PlayAudio
                object_list = [ {'Play': obj_callrequest.voipapp.data},]
                logger.debug('PlayAudio')

            elif obj_callrequest.voipapp.type == 3:
                #Conference
                object_list = [ {'Conference': obj_callrequest.voipapp.data},]
                logger.debug('Conference')

            elif obj_callrequest.voipapp.type == 4:
                #Speak
                object_list = [ {'Speak': obj_callrequest.voipapp.data},]
                logger.debug('Speak')

            #return [ {'Speak': 'Hello World'}, {'Dial': {'Number': '1000'}, },]
            #return [ {'Speak': 'System error'},]

            #resp = rc.NOT_IMPLEMENTED
            logger.error('Error with VoIP App type!')

            obj = CustomXmlEmitter()
            #print obj.render(request, object_list)
            return self.create_response(request, obj.render(request, object_list))
        else:
            if len(errors):
                if request:
                    desired_format = self.determine_format(request)
                else:
                    desired_format = self._meta.default_format

                serialized = self.serialize(request, errors, desired_format)
                response = http.HttpBadRequest(content=serialized, content_type=desired_format)
                raise ImmediateHttpResponse(response=response)


class HangupcallValidation(Validation):
    """
    Hangupcall Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']
            
        opt_request_uuid = bundle.data.get('RequestUUID')
        if not opt_request_uuid:
            errors['RequestUUID'] = ["Wrong parameters - missing RequestUUID!"]

        opt_hangup_cause = bundle.data.get('HangupCause')
        if not opt_hangup_cause:
            errors['HangupCause'] = ["Wrong parameters - missing HangupCause!"]

        try:
            callrequest = Callrequest.objects.get(request_uuid=opt_request_uuid)
        except:
            errors['CallRequest'] = ["CallRequest not found!"]

        return errors


class HangupcallResource(ModelResource):
    """
    **Attributes**:

       * ``RequestUUID`` - RequestUUID
       * ``HangupCause`` - Hangup Cause

    **Validation**:

        * HangupcallValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"RequestUUID": "48092924-856d-11e0-a586-0147ddac9d3e", "HangupCause": "SUBSCRIBER_ABSENT"}' http://localhost:8000/api/v1/hangupcall/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/app/hangupcall/None/
            Content-Language: en-us
    """
    class Meta:
        queryset = Callrequest.objects.all()
        resource_name = 'hangupcall'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = HangupcallValidation()
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        logger.debug('Hangupcall API get called!')
        
        opt_request_uuid = bundle.data.get('RequestUUID')
        opt_hangup_cause = bundle.data.get('HangupCause')

        callrequest = Callrequest.objects.get(request_uuid=opt_request_uuid)
        # 2 / FAILURE ; 3 / RETRY ; 4 / SUCCESS
        if opt_hangup_cause=='NORMAL_CLEARING':
            callrequest.status = 4 # Success
        else:
            callrequest.status = 2 # Failure
        callrequest.hangup_cause = opt_hangup_cause
        callrequest.save()

        #TODO : Create CDR

        logger.debug('Hangupcall API : Result 200!')
        return bundle


class CdrValidation(Validation):
    """
    CDR Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']
            
        opt_cdr = bundle.data.get('cdr')
        if not opt_cdr:
            errors['CDR'] = ["Wrong parameters : missing cdr!"]

        return errors


class CustomJSONSerializer(Serializer):
    
    def from_json(self, content):
        #data = simplejson.loads(content)
        data = {}
        data['cdr'] = content[4:]
        return data


class CdrResource(ModelResource):
    """
    **Attributes**:

        * ``cdr`` - XML string assigned from the Telephony engine

    **Validation**:

        * CdrValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data 'cdr=<?xml version="1.0"?><cdr><other></other><variables><plivo_request_uuid>af41ac8a-ede4-11e0-9cca-00231470a30c</plivo_request_uuid><duration>3</duration></variables><notvariables><plivo_request_uuid>TESTc</plivo_request_uuid><duration>5</duration></notvariables></cdr>' http://localhost:8000/api/v1/store_cdr/
                     
        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/store_cdr/None/
            Content-Language: en-us
    """
    class Meta:
        queryset = VoIPCall.objects.all()
        resource_name = 'store_cdr'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = CdrValidation()
        serializer = CustomJSONSerializer()
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        logger.debug('CDR API get called')
        
        opt_cdr = bundle.data.get('cdr')
        
        data = {}
        import xml.etree.ElementTree as ET
        tree = ET.fromstring(opt_cdr)

        #parse file
        #tree = ET.parse("/tmp/cdr.xml")
        lst = tree.find("variables")

        cdr_vars = ['plivo_request_uuid', 'plivo_answer_url', 'plivo_app',
                    'direction', 'endpoint_disposition', 'hangup_cause',
                    'hangup_cause_q850', 'duration', 'billsec', 'progresssec',
                    'answersec', 'waitsec', 'mduration', 'billmsec',
                    'progressmsec', 'answermsec', 'waitmsec',
                    'progress_mediamsec', 'call_uuid',
                    'origination_caller_id_number', 'caller_id',
                    'answer_epoch', 'answer_uepoch']

        for j in lst:
            if j.tag in cdr_vars:
                data[j.tag] = j.text

        for element in cdr_vars:
            if not data.has_key(element):
                data[element] = None

        if not 'plivo_request_uuid' in data or not data['plivo_request_uuid']:
            #CDR not related to plivo
            #TODO: Add tag for newfies in outbound call
            error_msg = 'CDR not related to Newfies/Plivo!'
            logger.error(error_msg)
            raise BadRequest(error_msg)

        #TODO : delay if not find callrequest
        try:
            obj_callrequest = Callrequest.objects.get(request_uuid=data['plivo_request_uuid'])
        except:
            # Send notification to admin
            from dialer_campaign.views import common_send_notification
            from django.contrib.auth.models import User
            recipient_list = User.objects.filter(is_superuser=1, is_active=1)
            # send to all admin user
            for recipient in recipient_list:
                # callrequest_not_found - notification id 8
                common_send_notification(request, 8, recipient)

            error_msg = "Error, there is no callrequest for this uuid %s " % data['plivo_request_uuid']
            logger.error(error_msg, extra={'stack': True})

            raise BadRequest(error_msg)

        if data.has_key('answer_epoch') and data['answer_epoch']:
            try:
                cur_answer_epoch = int(data['answer_epoch'])
            except ValueError:
                raise
            starting_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cur_answer_epoch))
        else:
            starting_date = None

        new_voipcall = VoIPCall(user = obj_callrequest.user,
                                request_uuid=data['plivo_request_uuid'],
                                used_gateway=None, #TODO
                                callrequest=obj_callrequest,
                                callid=data['call_uuid'] or '',
                                callerid=data['origination_caller_id_number'] or '',
                                phone_number=data['caller_id'] or '',
                                dialcode=None, #TODO
                                starting_date=starting_date,
                                duration=data['duration'] or 0,
                                billsec=data['billsec'] or 0,
                                progresssec=data['progresssec'] or 0,
                                answersec=data['answersec'] or 0,
                                disposition=data['endpoint_disposition'] or '',
                                hangup_cause=data['hangup_cause'] or '',
                                hangup_cause_q850=data['hangup_cause_q850'] or '',)

        new_voipcall.save()

        # List of HttpResponse : 
        # https://github.com/toastdriven/django-tastypie/blob/master/tastypie/http.py
        logger.debug('CDR API : Result 200')
        return bundle

