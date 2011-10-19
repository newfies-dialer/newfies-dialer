import logging

from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie.utils import dict_strip_unicode_keys, trailing_slash
from tastypie.http import HttpCreated
from tastypie.exceptions import NotFound
from dialer_campaign.models import Campaign, Phonebook, Contact, CampaignSubscriber
from tastypie import fields
from dialer_campaign.function_def import user_attached_with_dialer_settings, \
    check_dialer_setting, dialer_setting_limit
from dialer_gateway.models import Gateway
from voip_app.models import VoipApp
import time


log = logging.getLogger(__name__)


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
        allowed_methods = ['get'] # Don't display or update User
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
        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        bundle = self.full_hydrate(bundle)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        bundle.obj.save()
        
        errors = {}
        try:
            # New phonebook
            new_phonebook = Phonebook.objects.create(user=request.user,
                                    name=bundle.obj.name + '-' + bundle.obj.campaign_code,
                                    description='Auto created Phonebook from API')
            bundle.obj.phonebook.add(new_phonebook)
            bundle.obj.save()
        except:
            #raise
            errors['duplicate_campaign_name'] = ["The Autogenerated Phonebook name duplicated - Internal Error!"]
            return errors


        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
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
        bundle.obj = self._meta.object_class()
        bundle = self.full_hydrate(bundle)
        
        phoneno_list = bundle.data.get('phoneno_list')
        phonebook_id = bundle.data.get('phonebook_id')
        phonenolist = list(phoneno_list.split(","))
        total_no = len(list(phonenolist))
        errors = {}
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
            errors['duplicate_nos'] = ["The contact duplicated (%s)!\n" % phoneno]
            pass

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
        obj = kwargs.pop('_obj', None)
        if not hasattr(obj, 'delete'):
            try:
                obj = self.obj_get(request, **kwargs)
            except:
                raise NotFound("A model instance matching the provided arguments could not be found.")

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
        except:
            raise NotFound("A model instance matching the provided arguments could not be found.")


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
        temp_url = request.META['PATH_INFO']
        temp_id = temp_url.split('/api/v1/campaignsubscriber/')[1]
        camp_id = temp_id.split('/')[0]
        #contact = temp_id.split('/')[1]

        from django.db import connection, transaction
        cursor = connection.cursor()

        campaign_id = int(camp_id)
        contact = ''

        if not campaign_id:
            resp = rc.BAD_REQUEST
            resp.write("No value for Campaign ID !")
            return resp

        if contact:
            if not isint(contact):
                resp = rc.BAD_REQUEST
                resp.write("Wrong value for contact !")
                return resp

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
        try:
            return self._meta.queryset.filter(contact__in=[result_string])._clone()
        except:
            return self._meta.queryset._clone()
    
    def obj_create(self, bundle, request=None, **kwargs):

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

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_update``.
        """
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
                raise NotFound("A model instance matching the provided arguments could not be found.")

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
            raise NotFound("A model instance matching the provided arguments could not be found.")

        return bundle


