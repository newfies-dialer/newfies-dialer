#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import logging

from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.utils.encoding import smart_unicode
from django.utils.xmlutils import SimplerXMLGenerator
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import connection

from tastypie.resources import ModelResource, ALL
from tastypie.authentication import Authentication, BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie.exceptions import BadRequest, NotFound, ImmediateHttpResponse
from tastypie import http
from tastypie import fields

from dialer_cdr.tasks import init_callrequest
from dialer_campaign.models import Campaign, Phonebook, Contact, \
                        CampaignSubscriber
from dialer_campaign.function_def import user_attached_with_dialer_settings, \
    check_dialer_setting, dialer_setting_limit, user_dialer_setting
from dialer_cdr.models import Callrequest, VoIPCall
from dialer_gateway.models import Gateway
from voice_app.models import VoiceApp

from api.user_api import UserResource
from api.gateway_api import GatewayResource
from api.content_type_api import ContentTypeResource
from api.phonebook_api import PhonebookResource

from common_functions import search_tag_string
from settings_local import API_ALLOWED_IP, PLIVO_DEFAULT_DIALCALLBACK_URL
from datetime import datetime, timedelta
from random import seed
import urllib
import time
import uuid

seed()


#
#TODO: Split this files into different ones for each API


logger = logging.getLogger('newfies.filelog')

CDR_VARIABLES = ['plivo_request_uuid', 'plivo_answer_url', 'plivo_app',
                 'direction', 'endpoint_disposition', 'hangup_cause',
                 'hangup_cause_q850', 'duration', 'billsec', 'progresssec',
                 'answersec', 'waitsec', 'mduration', 'billmsec',
                 'progressmsec', 'answermsec', 'waitmsec',
                 'progress_mediamsec', 'call_uuid',
                 'origination_caller_id_number', 'caller_id',
                 'answer_epoch', 'answer_uepoch']


def get_contact(id):
    try:
        con_obj = Contact.objects.get(pk=id)
        return con_obj.contact
    except:
        return ''


class CustomJSONSerializer(Serializer):

    def from_json(self, content):
        decoded_content = urllib.unquote(content.decode("utf8"))
        #data = simplejson.loads(content)
        data = {}
        data['cdr'] = decoded_content[4:]
        return data


def create_voipcall(obj_callrequest, plivo_request_uuid, data, data_prefix='',
    leg='a', hangup_cause='', from_plivo='', to_plivo=''):
    """
    Common function to create CDR / VoIP Call

    **Attributes**:

        * data : list with call details data
        * obj_callrequest:  refer to the CallRequest object
        * plivo_request_uuid : cdr uuid

    """

    if 'answer_epoch' in data and data['answer_epoch']:
        try:
            cur_answer_epoch = int(data['answer_epoch'])
        except ValueError:
            raise
        starting_date = time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(cur_answer_epoch))
    else:
        starting_date = None

    if leg == 'a':
        #A-Leg
        leg_type = 1
        used_gateway = obj_callrequest.aleg_gateway
    else:
        #B-Leg
        leg_type = 2
        used_gateway = obj_callrequest.content_object.gateway

    #check the right variable for hangup cause
    data_hangup_cause = data["%s%s" % (data_prefix, 'hangup_cause')]
    if data_hangup_cause and data_hangup_cause != '':
        cdr_hangup_cause = data_hangup_cause
    else:
        cdr_hangup_cause = hangup_cause

    if cdr_hangup_cause == 'USER_BUSY':
        disposition = 'BUSY'
    else:
        disposition = data["%s%s" % \
                        (data_prefix, 'endpoint_disposition')] or ''

    logger.debug('Create CDR - request_uuid=%s ; leg=%d ; hangup_cause= %s' % \
                    (plivo_request_uuid, leg_type, cdr_hangup_cause))

    new_voipcall = VoIPCall(
                    user=obj_callrequest.user,
                    request_uuid=plivo_request_uuid,
                    leg_type=leg_type,
                    used_gateway=used_gateway,
                    callrequest=obj_callrequest,
                    callid=data["%s%s" % (data_prefix, 'call_uuid')] or '',
                    callerid=from_plivo,
                    phone_number=to_plivo,
                    dialcode=None,  # TODO
                    starting_date=starting_date,
                    duration=data["%s%s" % (data_prefix, 'duration')] or 0,
                    billsec=data["%s%s" % (data_prefix, 'billsec')] or 0,
                    progresssec=data["%s%s" % \
                                        (data_prefix, 'progresssec')] or 0,
                    answersec=data["%s%s" % (data_prefix, 'answersec')] or 0,
                    disposition=disposition,
                    hangup_cause=cdr_hangup_cause,
                    hangup_cause_q850=data["%s%s" % \
                                    (data_prefix, 'hangup_cause_q850')] or '',)

    new_voipcall.save()


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


def save_if_set(record, fproperty, value):
    """function to save a property if it has been set"""
    if value:
        record.__dict__[fproperty] = value


class IpAddressAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        if request.META['REMOTE_ADDR'] in API_ALLOWED_IP:
            return True
        else:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())
            return False


class IpAddressAuthentication(Authentication):
    def is_authorized(self, request, object=None):
        if request.META['REMOTE_ADDR'] in API_ALLOWED_IP:
            return True
        else:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())
            return False


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
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)

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
            else:
                # phonebook_count > 0
                other_campaing_count = \
                Campaign.objects.filter(user=request.user,
                         phonebook__in=del_campaign.phonebook.all())\
                .exclude(id=campaign_id).count()

                if other_campaing_count == 0:
                    # delete phonebooks as well as contacts belong to it

                    # 1) delete all contacts which are belong to phonebook
                    contact_list = Contact.objects\
                            .filter(phonebook__in=del_campaign.phonebook.all())
                    contact_list.delete()

                    # 2) delete phonebook
                    phonebook_list = Phonebook.objects\
                            .filter(id__in=del_campaign.phonebook.all())
                    phonebook_list.delete()

                    # 3) delete campaign
                    del_campaign.delete()
                else:
                    del_campaign.delete()
                logger.debug('CampaignDeleteCascade API : result ok 200')
        except:
            error_msg = "A model matching arguments not found."
            logger.error(error_msg)
            raise NotFound(error_msg)


class CampaignSubscriberValidation(Validation):
    """
    CampaignSubscriber Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}
        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        if check_dialer_setting(request, check_for="contact"):
            errors['contact_dialer_setting'] = ["You have too many contacts \
                per campaign. You are allowed a maximum of %s" % \
                dialer_setting_limit(request, limit_for="contact")]

        if request.method == 'POST':
            phonebook_id = bundle.data.get('phonebook_id')
            if phonebook_id:
                try:
                    Phonebook.objects.get(id=phonebook_id)
                except Phonebook.DoesNotExist:
                    errors['phonebook_error'] = ["Phonebook is not selected!"]
            else:
                errors['phonebook_error'] = ["Phonebook is not selected!"]

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
            Location: http://localhost:8000/api/v1/campaignsubscriber/1/
            Content-Type: text/plain

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/campaignsubscriber/?format=json

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
                     "count_attempt":1,
                     "created_date":"2012-01-17T03:58:49",
                     "duplicate_contact":"123456789",
                     "id":"1",
                     "last_attempt":"2012-01-17T15:28:37",
                     "resource_uri":"/api/v1/campaignsubscriber/1/",
                     "status":2,
                     "updated_date":"2012-02-07T02:22:19"
                  }
               ]
            }

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
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)

    def obj_create(self, bundle, request=None, **kwargs):
        """
        TODO: Add doc
        """
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
                                status=1,  # default active
                                phonebook=obj_phonebook)
        # Assign new contact object
        bundle.obj = new_contact

        # Insert the contact to the campaignsubscriber also for
        # each campaign using this phonebook

        campaign_obj = Campaign.objects.filter(
                            phonebook=obj_phonebook,
                            user=request.user)
        for camp_obj in campaign_obj:
            imported_phonebook = []
            if camp_obj.imported_phonebook:
                # for example:- camp_obj.imported_phonebook = 1,2,3
                # So convert imported_phonebook string into int list
                imported_phonebook = map(int,
                                        camp_obj.imported_phonebook.split(','))

            phonbook_list = camp_obj.phonebook\
                                    .values_list('id', flat=True)\
                                    .all()
            phonbook_list = map(int, phonbook_list)

            common_phonbook_list = []
            if phonbook_list:
                common_phonbook_list = list(set(imported_phonebook) & \
                                        set(phonbook_list))
                if common_phonbook_list:
                    contact_list = Contact.objects\
                            .filter(
                                phonebook__in=common_phonbook_list,
                                status=1)
                    for con_obj in contact_list:
                        try:
                            CampaignSubscriber.objects.create(
                                     contact=con_obj,
                                     duplicate_contact=con_obj.contact,
                                     status=1,  # START
                                     campaign=camp_obj)
                        except:
                            #TODO Catching duplicate error
                            pass

        logger.debug('CampaignSubscriber POST API : result ok 200')
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_update``.
        """
        logger.debug('CampaignSubscriber PUT API get called')

        temp_url = request.META['PATH_INFO']
        temp_id = temp_url.split('/api/v1/campaignsubscriber/')[1]
        campaign_id = temp_id.split('/')[0]

        campaign_obj = Campaign.objects.get(id=campaign_id)
        try:
            campaignsubscriber = CampaignSubscriber.objects\
                    .get(duplicate_contact=bundle.data.get('contact'),
                        campaign=campaign_obj)
            campaignsubscriber.status = bundle.data.get('status')
            campaignsubscriber.save()
        except:
            error_msg = "A model matching arguments could not be found."
            logger.error(error_msg)
            raise BadRequest(error_msg)

        logger.debug('CampaignSubscriber PUT API : result ok 200')
        return bundle


class CampaignSubscriberPerCampaignResource(ModelResource):
    """
    **Attributes Details**:

        * ``contact_id`` - contact id
        * ``count_attempt`` - no of call attempt
        * ``last_attempt`` - last call attempt
        * ``status`` - call status

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/campaignsubscriber_per_campaign/%campaign_id%/?format=json
            or
            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/campaignsubscriber_per_campaign/%campaign_id%/%contact%/?format=json

        Response::

            [
               {
                  "contact_id":1,
                  "count_attempt":1,
                  "last_attempt":"2012-01-17T15:28:37",
                  "status":2,
                  "campaign_subscriber_id": 1,
                  "contact": "640234123"
               },
               {
                  "contact_id":2,
                  "count_attempt":1,
                  "last_attempt":"2012-02-06T17:00:38",
                  "status":1,
                  "campaign_subscriber_id": 2,
                  "contact": "640234000"
               }
            ]

    """
    class Meta:
        resource_name = 'campaignsubscriber_per_campaign'
        authorization = Authorization()
        authentication = BasicAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        # default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)

    def override_urls(self):
        """Override urls"""
        return [
            url(r'^(?P<resource_name>%s)/(.+)/$' % \
                self._meta.resource_name, self.wrap_view('read')),
        ]

    def read_response(self, request, data,
        response_class=HttpResponse, **response_kwargs):
        """To display API's result"""
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized,
                    content_type=desired_format, **response_kwargs)

    def read(self, request=None, **kwargs):
        """GET method of CampaignSubscriber API"""
        logger.debug('CampaignSubscriber GET API get called')
        auth_result = self._meta.authentication.is_authenticated(request)
        if not auth_result is True:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

        logger.debug('CampaignSubscriber GET API authorization called!')
        auth_result = self._meta.authorization.is_authorized(request, object)

        temp_url = request.META['PATH_INFO']
        temp_id = temp_url.split('/api/v1/campaignsubscriber_per_campaign/')[1]
        camp_id = temp_id.split('/')[0]
        try:
            contact = temp_id.split('/')[1]
        except:
            contact = False

        cursor = connection.cursor()

        try:
            campaign_id = int(camp_id)
        except:
            error_msg = "No value for Campaign ID !"
            logger.error(error_msg)
            raise BadRequest(error_msg)

        try:
            Campaign.objects.get(id=campaign_id)
        except:
            error_msg = "Campaign ID does not exists!"
            logger.error(error_msg)
            raise BadRequest(error_msg)

        if contact:
            try:
                int(contact)
            except ValueError:
                error_msg = "Wrong value for contact !"
                logger.error(error_msg)
                raise BadRequest(error_msg)

            sql_statement = 'SELECT DISTINCT contact_id, last_attempt, '\
                'count_attempt, dialer_campaign_subscriber.status,'\
                'dialer_campaign_subscriber.id '\
                'FROM dialer_campaign_subscriber '\
                'LEFT JOIN dialer_callrequest ON '\
                'campaign_subscriber_id=dialer_campaign_subscriber.id '\
                'LEFT JOIN dialer_campaign ON '\
                'dialer_callrequest.campaign_id=dialer_campaign.id '\
                'WHERE dialer_campaign_subscriber.campaign_id = %s '\
                'AND dialer_campaign_subscriber.duplicate_contact = "%s"'\
                % (str(campaign_id), str(contact))

        else:
            sql_statement = 'SELECT DISTINCT contact_id, last_attempt, '\
                'count_attempt, dialer_campaign_subscriber.status, '\
                'dialer_campaign_subscriber.id '\
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
        for record in row:
            modrecord = {}
            modrecord['contact_id'] = record[0]
            modrecord['last_attempt'] = record[1]
            modrecord['count_attempt'] = record[2]
            modrecord['status'] = record[3]
            modrecord['campaign_subscriber_id'] = record[4]
            modrecord['contact'] = get_contact(record[0])
            result.append(modrecord)

        logger.debug('CampaignSubscriber GET API : result ok 200')
        return self.read_response(request, result)


class CallrequestValidation(Validation):
    """
    Callrequest Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        content_type = bundle.data.get('content_type')
        if content_type == 'voice_app' or content_type == 'survey':
            try:
                content_type_id = ContentType.objects\
                                    .get(app_label=str(content_type)).id
                bundle.data['content_type'] = '/api/v1/contenttype/%s/' \
                                                    % content_type_id
            except:
                errors['chk_content_type'] = ["The ContentType doesn't exist!"]
        else:
            errors['chk_content_type'] = ["Wrong option. \
                                            Enter 'voice_app' or 'survey' !"]

        object_id = bundle.data.get('object_id')
        if object_id:
            try:
                bundle.data['object_id'] = object_id
            except:
                errors['chk_object_id'] = ["App object Id doesn't exist!"]

        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        if request.method == 'POST':
            rq_count = Callrequest.objects\
                    .filter(request_uuid=bundle.data.get('request_uuid'))\
                    .count()
            if (rq_count != 0):
                errors['chk_request_uuid'] = ["The Request uuid duplicated!"]

        return errors


class CallrequestResource(ModelResource):
    """
    **Attributes**:

        * ``request_uuid`` - Unique id
        * ``call_time`` - Total call time
        * ``call_type`` - Call type
        * ``status`` - Call request status
        * ``callerid`` - Caller ID
        * ``callrequest_id``- Callrequest Id
        * ``timeout`` -
        * ``timelimit`` -
        * ``status`` -
        * ``campaign_subscriber`` -
        * ``campaign`` -
        * ``phone_number`` -
        * ``extra_dial_string`` -
        * ``extra_data`` -
        * ``num_attempt`` -
        * ``last_attempt_time`` -
        * ``result`` -
        * ``hangup_cause`` -
        * ``last_attempt_time`` -


    **Relationships**:

        * ``content_type`` - Defines the application (``voice_app`` or ``survey``) to use when the \
                             call is established on the A-Leg
        * ``object_id`` - Defines the object of content_type application

    **Validation**:

        * CallrequestValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"request_uuid": "2342jtdsf-00123", "call_time": "2011-10-20 12:21:22", "phone_number": "8792749823", "content_type":"voice_app", "object_id":1, "timeout": "30000", "callerid": "650784355", "call_type": "1"}' http://localhost:8000/api/v1/callrequest/

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
    content_type = fields.ForeignKey(ContentTypeResource,
                            'content_type', full=True)

    class Meta:
        queryset = Callrequest.objects.all()
        resource_name = 'callrequest'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = CallrequestValidation()
        list_allowed_methods = ['get', 'post', 'put']
        detail_allowed_methods = ['get', 'post', 'put']
        # default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)


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


class AnswercallValidation(Validation):
    """
    Answercall Validation Class
    """
    def is_valid(self, request=None):
        errors = {}

        opt_ALegRequestUUID = request.POST.get('ALegRequestUUID')
        if not opt_ALegRequestUUID:
            errors['ALegRequestUUID'] = ["Wrong parameters - "\
                                        "missing ALegRequestUUID!"]

        opt_CallUUID = request.POST.get('CallUUID')
        if not opt_CallUUID:
            errors['CallUUID'] = ["Wrong parameters - missing CallUUID!"]

        try:
            obj_callrequest = Callrequest.objects.get(
                                            request_uuid=opt_ALegRequestUUID)
            if not obj_callrequest.content_type:
                errors['Attached App'] = ['Not attached to Voice App/Survey']
        except:
            errors['ALegRequestUUID'] = ['Call Request cannot be found!']

        return errors


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
                        <Number gateways="user/,user" gatewayTimeouts="30000">
                        </Number>
                    </Dial>
                </Response>
    """
    class Meta:
        resource_name = 'answercall'
        authorization = IpAddressAuthorization()
        authentication = IpAddressAuthentication()
        validation = AnswercallValidation()
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        # default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)

    def override_urls(self):
        """Override urls"""
        return [
            url(r'^(?P<resource_name>%s)/$' % \
                self._meta.resource_name, self.wrap_view('create')),
        ]

    def create_response(self, request, data,
        response_class=HttpResponse, **response_kwargs):
        """To display API's result"""
        desired_format = self.determine_format(request)
        serialized = data
        return response_class(content=serialized,
                        content_type=desired_format, **response_kwargs)

    def create(self, request=None, **kwargs):
        """POST method of Answercall API"""
        logger.debug('Answercall API authentication called!')
        auth_result = self._meta.authentication.is_authenticated(request)
        if not auth_result is True:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

        logger.debug('Answercall API authorization called!')
        auth_result = self._meta.authorization.is_authorized(request, object)

        logger.debug('Answercall API validation called!')
        errors = self._meta.validation.is_valid(request)

        if not errors:
            logger.debug('Answercall API get called!')

            opt_ALegRequestUUID = request.POST.get('ALegRequestUUID')
            opt_CallUUID = request.POST.get('CallUUID')

            #TODO: If we update the Call to success here we should not do it in hangup url
            obj_callrequest = Callrequest.objects\
                                    .get(request_uuid=opt_ALegRequestUUID)

            #TODO : use constant
            obj_callrequest.status = 8  # IN-PROGRESS
            obj_callrequest.aleg_uuid = opt_CallUUID
            obj_callrequest.save()

            # check if Voice App
            if obj_callrequest.content_object.__class__.__name__ != 'VoiceApp':
                object_list = []
                logger.error('Error with App type, not a VoiceApp!')
            else:
                data = obj_callrequest.content_object.data
                tts_language = obj_callrequest.content_object.tts_language

                extra_data = obj_callrequest.campaign.extra_data
                if extra_data and len(extra_data) > 1:
                    #check if we have a voice_app_data tag to replace
                    voice_app_data = search_tag_string(extra_data,
                                                        'voice_app_data')
                    if voice_app_data:
                        data = voice_app_data

                if obj_callrequest.content_object.type == 1:
                    #Dial
                    timelimit = obj_callrequest.timelimit
                    callerid = obj_callrequest.callerid
                    gatewaytimeouts = obj_callrequest.timeout
                    gateways = obj_callrequest.content_object.gateway.gateways
                    dial_command = 'Dial timeLimit="%s"'\
                                    '-callerId="%s"'\
                                    '-callbackUrl="%s"' % \
                                    (timelimit,
                                     callerid,
                                     PLIVO_DEFAULT_DIALCALLBACK_URL)
                    number_command = 'Number gateways="%s" ' \
                                     'gatewayTimeouts="%s"' % \
                                      (gateways, gatewaytimeouts)

                    object_list = [{dial_command: {number_command: data}}]
                    logger.debug('Dial command')

                elif obj_callrequest.content_object.type == 2:
                    #PlayAudio
                    object_list = [{'Play': data}]
                    logger.debug('PlayAudio')

                elif obj_callrequest.content_object.type == 3:
                    #Conference
                    object_list = [{'Conference': data}]
                    logger.debug('Conference')

                elif obj_callrequest.content_object.type == 4:
                    #Speak
                    if settings.TTS_ENGINE != 'ACAPELA':
                        object_list = [{'Speak': data}]
                        logger.debug('Speak')
                    else:
                        import acapela
                        DIRECTORY = settings.MEDIA_ROOT + '/tts/'
                        domain = Site.objects.get_current().domain
                        tts_acapela = acapela.Acapela(
                                        settings.TTS_ENGINE,
                                        settings.ACCOUNT_LOGIN,
                                        settings.APPLICATION_LOGIN,
                                        settings.APPLICATION_PASSWORD,
                                        settings.SERVICE_URL,
                                        settings.QUALITY,
                                        DIRECTORY)
                        tts_acapela.prepare(
                                        data,
                                        tts_language,
                                        settings.ACAPELA_GENDER,
                                        settings.ACAPELA_INTONATION)
                        output_filename = tts_acapela.run()

                        audiofile_url = domain + settings.MEDIA_URL + \
                                            'tts/' + output_filename
                        object_list = [{'Play': audiofile_url}]
                        logger.debug('PlayAudio-TTS')
                else:
                    logger.error('Error with Voice App type!')

            obj = CustomXmlEmitter()
            return self.create_response(request,
                    obj.render(request, object_list))

        else:
            logger.debug('ERROR : ' + str(errors))
            if len(errors):
                if request:
                    desired_format = self.determine_format(request)
                else:
                    desired_format = self._meta.default_format

                serialized = self.serialize(request, errors, desired_format)
                response = http.HttpBadRequest(content=serialized,
                                        content_type=desired_format)
                raise ImmediateHttpResponse(response=response)


class DialCallbackValidation(Validation):
    """
    DialCallback Validation Class
    """
    def is_valid(self, request=None):
        errors = {}

        opt_aleg_uuid = request.POST.get('DialALegUUID')
        if not opt_aleg_uuid:
            errors['DialALegUUID'] = ["Missing DialALegUUID!"]

        opt_request_uuid_bleg = request.POST.get('DialBLegUUID')
        if not opt_request_uuid_bleg:
            errors['DialBLegUUID'] = ["Missing DialBLegUUID!"]

        opt_dial_bleg_status = request.POST.get('DialBLegStatus')
        if not opt_dial_bleg_status:
            errors['DialBLegStatus'] = ["Missing DialBLegStatus!"]

        try:
            Callrequest.objects.get(aleg_uuid=opt_aleg_uuid)
        except:
            errors['CallRequest'] = ["Call request not found - uuid:%s" % \
                                        opt_request_uuid_bleg]
        return errors


class DialCallbackResource(ModelResource):
    """
    **Attributes**:

       * ``DialALegUUID`` - UUID ALeg
       * ``DialBLegUUID`` - UUID BLeg
       * ``DialBLegHangupCause`` - Hangup Cause

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data "DialALegUUID=e4fc2188-0af5-11e1-b64d-00231470a30c&DialBLegUUID=e4fc2188-0af5-11e1-b64d-00231470a30c&DialBLegHangupCause=SUBSCRIBER_ABSENT" http://localhost:8000/api/v1/dialcallback/

        Response::

            HTTP/1.0 200 OK
            Date: Tue, 01 Nov 2011 12:04:35 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: application/json
            Content-Language: en-us

            <?xml version="1.0" encoding="utf-8"?>
                <Response>
                </Response>
    """
    class Meta:
        resource_name = 'dialcallback'
        authorization = IpAddressAuthorization()
        authentication = IpAddressAuthentication()
        validation = DialCallbackValidation()
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        # throttle : default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000,
                                timeframe=3600)

    def override_urls(self):
        """Override url"""
        return [
            url(r'^(?P<resource_name>%s)/$' % \
                self._meta.resource_name, self.wrap_view('create')),
        ]

    def create_response(self, request, data,
        response_class=HttpResponse, **response_kwargs):
        """To display API's result"""
        desired_format = self.determine_format(request)
        serialized = data
        return response_class(content=serialized,
                            content_type=desired_format, **response_kwargs)

    def create(self, request=None, **kwargs):
        """POST method of DialCallback API"""
        logger.debug('DialCallback API authentication called!')
        auth_result = self._meta.authentication.is_authenticated(request)
        if not auth_result is True:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

        logger.debug('DialCallback API authorization called!')
        auth_result = self._meta.authorization.is_authorized(request, object)

        logger.debug('DialCallback API validation called!')
        errors = self._meta.validation.is_valid(request)

        if not errors:
            logger.debug('DialCallback API get called!')
            opt_aleg_uuid = request.POST.get('DialALegUUID')
            opt_dial_bleg_uuid = request.POST.get('DialBLegUUID')
            opt_dial_bleg_status = request.POST.get('DialBLegStatus')
            #We are just analyzing the hangup
            if opt_dial_bleg_status != 'hangup':
                object_list = [{'result': 'OK - Bleg status is not Hangup'}]
                logger.debug('DialCallback API : Result 200!')
                obj = CustomXmlEmitter()
                return self.create_response(
                                request,
                                obj.render(request, object_list))
            callrequest = Callrequest.objects.get(aleg_uuid=opt_aleg_uuid)
            data = {}
            for element in CDR_VARIABLES:
                if not request.POST.get('variable_%s' % element):
                    data[element] = None
                else:
                    data[element] = request.POST.get('variable_%s' % element)

            from_plivo = request.POST.get('From')
            to_plivo = request.POST.get('To')

            create_voipcall(obj_callrequest=callrequest,
                                plivo_request_uuid=callrequest.request_uuid,
                                data=data,
                                data_prefix='',
                                leg='b',
                                from_plivo=from_plivo,
                                to_plivo=to_plivo)
            object_list = [{'result': 'OK'}]
            logger.debug('DialCallback API : Result 200!')
            obj = CustomXmlEmitter()

            return self.create_response(request,
                        obj.render(request, object_list))
        else:
            if len(errors):
                if request:
                    desired_format = self.determine_format(request)
                else:
                    desired_format = self._meta.default_format

                serialized = self.serialize(request, errors, desired_format)
                response = http.HttpBadRequest(
                                content=serialized,
                                content_type=desired_format)
                raise ImmediateHttpResponse(response=response)


class HangupcallValidation(Validation):
    """
    Hangupcall Validation Class
    """
    def is_valid(self, request=None):
        errors = {}

        opt_request_uuid = request.POST.get('RequestUUID')
        if not opt_request_uuid:
            errors['RequestUUID'] = ["Wrong parameters - missing RequestUUID!"]

        opt_hangup_cause = request.POST.get('HangupCause')
        if not opt_hangup_cause:
            errors['HangupCause'] = ["Wrong parameters - missing HangupCause!"]

        #for var_name in CDR_VARIABLES:
        #    if not request.POST.get("variable_%s" % var_name):
        #        errors[var_name] = ["Wrong parameters - miss %s!" % var_name]
        try:
            Callrequest.objects.get(request_uuid=opt_request_uuid)
        except:
            errors['CallRequest'] = ["CallRequest not found - uuid:%s" % \
                                opt_request_uuid]
        return errors


class HangupcallResource(ModelResource):
    """
    **Attributes**:

       * ``RequestUUID`` - RequestUUID
       * ``HangupCause`` - Hangup Cause

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data "RequestUUID=e4fc2188-0af5-11e1-b64d-00231470a30c&HangupCause=SUBSCRIBER_ABSENT" http://localhost:8000/api/v1/hangupcall/

        Response::

            HTTP/1.0 200 OK
            Date: Tue, 01 Nov 2011 12:04:35 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: application/json
            Content-Language: en-us

            <?xml version="1.0" encoding="utf-8"?>
                <Response>
                </Response>
    """
    class Meta:
        resource_name = 'hangupcall'
        authorization = IpAddressAuthorization()
        authentication = IpAddressAuthentication()
        validation = HangupcallValidation()
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        # throttle : default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000,
                                timeframe=3600)

    def override_urls(self):
        """Override url"""
        return [
            url(r'^(?P<resource_name>%s)/$' % \
                self._meta.resource_name, self.wrap_view('create')),
        ]

    def create_response(self, request, data,
        response_class=HttpResponse, **response_kwargs):
        """To display API's result"""
        desired_format = self.determine_format(request)
        serialized = data
        return response_class(content=serialized,
            content_type=desired_format, **response_kwargs)

    def create(self, request=None, **kwargs):
        """POST method of Hangupcall API"""
        logger.debug('Hangupcall API authentication called!')
        auth_result = self._meta.authentication.is_authenticated(request)
        if not auth_result is True:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())
        auth_result = self._meta.authorization.is_authorized(request, object)
        errors = self._meta.validation.is_valid(request)
        if not errors:
            opt_request_uuid = request.POST.get('RequestUUID')
            opt_hangup_cause = request.POST.get('HangupCause')
            try:
                callrequest = Callrequest.objects.get(
                                            request_uuid=opt_request_uuid)
            except:
                logger.debug('Hangupcall Error cannot find the Callrequest!')
            try:
                obj_subscriber = CampaignSubscriber.objects.get(
                                    id=callrequest.campaign_subscriber.id)
                if opt_hangup_cause == 'NORMAL_CLEARING':
                    obj_subscriber.status = 5  # Complete
                else:
                    obj_subscriber.status = 4  # Fail
                obj_subscriber.save()
            except:
                logger.debug('Hangupcall Error cannot find the '
                                            'Campaignsubscriber!')

            # 2 / FAILURE ; 3 / RETRY ; 4 / SUCCESS
            if opt_hangup_cause == 'NORMAL_CLEARING':
                callrequest.status = 4  # Success
            else:
                callrequest.status = 2  # Failure
            callrequest.hangup_cause = opt_hangup_cause
            #save callrequest & campaignsubscriber
            callrequest.save()
            data = {}
            for element in CDR_VARIABLES:
                if not request.POST.get('variable_%s' % element):
                    data[element] = None
                else:
                    data[element] = request.POST.get('variable_%s' % element)
            from_plivo = request.POST.get('From')
            to_plivo = request.POST.get('To')

            create_voipcall(obj_callrequest=callrequest,
                            plivo_request_uuid=opt_request_uuid,
                            data=data,
                            data_prefix='',
                            leg='a',
                            hangup_cause=opt_hangup_cause,
                            from_plivo=from_plivo,
                            to_plivo=to_plivo)
            object_list = [{'result': 'OK'}]
            logger.debug('Hangupcall API : Result 200!')
            obj = CustomXmlEmitter()

            #We will manage the retry directly from the API
            if opt_hangup_cause != 'NORMAL_CLEARING' \
                and callrequest.call_type == 1:  # Allow retry
                #Update to Retry Done
                callrequest.call_type = 3
                callrequest.save()

                dialer_set = user_dialer_setting(callrequest.user)
                if callrequest.num_attempt >= callrequest.campaign.maxretry \
                    or callrequest.num_attempt >= dialer_set.maxretry:
                    logger.error("Not allowed retry - Maxretry (%d)" % \
                                            callrequest.campaign.maxretry)
                else:
                    #Allowed Retry

                    # TODO : Review Logic
                    # Create new callrequest, Assign parent_callrequest,
                    # Change callrequest_type & num_attempt
                    new_callrequest = Callrequest(
                                request_uuid=uuid.uuid1(),
                                parent_callrequest_id=callrequest.id,
                                call_type=1,
                                num_attempt=callrequest.num_attempt + 1,
                                user=callrequest.user,
                                campaign_id=callrequest.campaign_id,
                                aleg_gateway_id=callrequest.aleg_gateway_id,
                                content_type=callrequest.content_type,
                                object_id=callrequest.object_id,
                                phone_number=callrequest.phone_number)
                    new_callrequest.save()
                    #Todo Check if it's a good practice
                    #implement a PID algorithm
                    second_towait = callrequest.campaign.intervalretry
                    launch_date = datetime.now() + \
                                        timedelta(seconds=second_towait)
                    logger.info("Init Retry CallRequest at %s" % \
                                (launch_date.strftime("%b %d %Y %I:%M:%S")))
                    init_callrequest.apply_async(
                            args=[new_callrequest.id, callrequest.campaign.id],
                            eta=launch_date)

            return self.create_response(request,
                        obj.render(request, object_list))
        else:
            if len(errors):
                if request:
                    desired_format = self.determine_format(request)
                else:
                    desired_format = self._meta.default_format

                serialized = self.serialize(request, errors, desired_format)
                response = http.HttpBadRequest(
                                    content=serialized,
                                    content_type=desired_format)
                raise ImmediateHttpResponse(response=response)


class CdrValidation(Validation):
    """
    CDR Validation Class
    """
    def is_valid(self, request=None):
        errors = {}
        opt_cdr = request.POST.get('cdr')
        if not opt_cdr:
            errors['CDR'] = ["Wrong parameters - missing CDR!"]
        return errors


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
        resource_name = 'store_cdr'
        authorization = IpAddressAuthorization()
        authentication = IpAddressAuthentication()
        validation = CdrValidation()
        #serializer = CustomJSONSerializer()
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        # throttle : default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)

    def override_urls(self):
        """Override url"""
        return [
            url(r'^(?P<resource_name>%s)/$' % \
                    self._meta.resource_name, self.wrap_view('create')),
        ]

    def create_response(self, request, data,
        response_class=HttpResponse, **response_kwargs):
        """To display API's result"""
        desired_format = self.determine_format(request)
        serialized = data  # self.serialize(request, data, desired_format)
        return response_class(content=serialized,
                            content_type=desired_format, **response_kwargs)

    def create(self, request=None, **kwargs):
        """POST method of CDR_Store API"""
        logger.debug('CDR API authentication called!')
        auth_result = self._meta.authentication.is_authenticated(request)
        if not auth_result is True:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

        logger.debug('CDR API authorization called!')
        auth_result = self._meta.authorization.is_authorized(request, object)

        errors = self._meta.validation.is_valid(request)
        logger.debug('CDR API get called from IP %s' % \
                request.META.get('REMOTE_ADDR'))
        if not errors:

            opt_cdr = request.POST.get('cdr')
            #XML parsing doesn't work if you urldecode first
            #decoded_cdr = urllib.unquote(opt_cdr.decode("utf8"))
            decoded_cdr = opt_cdr
            data = {}
            try:
                import xml.etree.ElementTree as ET
                tree = ET.fromstring(decoded_cdr)
                lst = tree.find("variables")
            except:
                logger.debug('Error parse XML')
                raise

            for j in lst:
                if j.tag in CDR_VARIABLES:
                    data[j.tag] = urllib.unquote(j.text.decode("utf8"))
            for element in CDR_VARIABLES:
                if element in data:
                    data[element] = None
                else:
                    logger.debug("%s :> %s" % (element, data[element]))

            #TODO: Add tag for newfies in outbound call
            if not 'plivo_request_uuid' in data \
                or not data['plivo_request_uuid']:
                # CDR not related to plivo
                error_msg = 'CDR not related to Newfies/Plivo!'
                logger.error(error_msg)
                raise BadRequest(error_msg)

            #TODO : delay if not find callrequest
            try:
                # plivo add "a_" in front of the uuid
                # for the aleg so we remove the "a_"
                if data['plivo_request_uuid'][1:2] == 'a_':
                    plivo_request_uuid = data['plivo_request_uuid'][2:]
                else:
                    plivo_request_uuid = data['plivo_request_uuid']
                obj_callrequest = Callrequest.objects.get(
                                        request_uuid=plivo_request_uuid)
            except:
                # Send notification to admin
                from dialer_campaign.views import common_send_notification
                from django.contrib.auth.models import User
                recipient_list = User.objects.filter(
                                    is_superuser=1,
                                    is_active=1)
                # send to all admin user
                for recipient in recipient_list:
                    # callrequest_not_found - notification id 8
                    common_send_notification(request, 8, recipient)

                error_msg = "Error, there is no callrequest for " \
                            "this uuid %s " % data['plivo_request_uuid']
                logger.error(error_msg, extra={'stack': True})

                raise BadRequest(error_msg)

            # CREATE CDR - VOIP CALL
            create_voipcall(
                        obj_callrequest,
                        plivo_request_uuid,
                        data,
                        data_prefix='',
                        leg='a')

            # List of HttpResponse :
            # https://github.com/toastdriven/django-tastypie/blob/master/tastypie/http.py
            logger.debug('CDR API : Result 200')

            object_list = [{'result': 'OK'}]
            obj = CustomXmlEmitter()
            return self.create_response(request, \
                            obj.render(request, object_list))

        else:
            if len(errors):
                if request:
                    desired_format = self.determine_format(request)
                else:
                    desired_format = self._meta.default_format

                serialized = self.serialize(request, errors, desired_format)
                response = http.HttpBadRequest(
                                    content=serialized,
                                    content_type=desired_format)
                raise ImmediateHttpResponse(response=response)
