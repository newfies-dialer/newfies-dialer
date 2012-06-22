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
from api.user_api import UserResource

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
