# -*- coding: utf-8 -*-

#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.conf.urls.defaults import url
from django.http import HttpResponse
from tastypie.resources import ModelResource
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie.exceptions import ImmediateHttpResponse
from tastypie import http
from dialer_campaign.constants import SUBSCRIBER_STATUS
from dialer_cdr.constants import CALLREQUEST_STATUS, CALLREQUEST_TYPE
from dialer_cdr.models import Callrequest
from dialer_cdr.tasks import init_callrequest, check_retrycall_completion
from dialer_campaign.models import Subscriber
from dialer_campaign.function_def import user_dialer_setting
from api.resources import CustomXmlEmitter, \
    IpAddressAuthorization, IpAddressAuthentication, \
    create_voipcall, CDR_VARIABLES
import logging
from uuid import uuid1

logger = logging.getLogger('newfies.filelog')


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
            errors['CallRequest'] = ["CallRequest not found - uuid:%s" % opt_request_uuid]
        return errors


class HangupcallResource(ModelResource):
    """
    **Attributes**:

       * ``RequestUUID`` - RequestUUID
       * ``HangupCause`` - Hangup Cause

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data "RequestUUID=e4fc2188-0af5-11e1-b64d-00231470a30c&HangupCause=SUBSCRIBER_ABSENT&From=800124545&To=34650111222" http://localhost:8000/api/v1/hangupcall/

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
        """Override urls"""
        return [
            url(r'^(?P<resource_name>%s)/$' % self._meta.resource_name, self.wrap_view('create')),
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
            callrequest = Callrequest.objects.get(request_uuid=opt_request_uuid)

            try:
                obj_subscriber = Subscriber.objects.get(id=callrequest.subscriber.id)
                if opt_hangup_cause == 'NORMAL_CLEARING':
                    if obj_subscriber.status != SUBSCRIBER_STATUS.COMPLETED:
                        obj_subscriber.status = SUBSCRIBER_STATUS.SENT
                else:
                    obj_subscriber.status = SUBSCRIBER_STATUS.FAIL
                obj_subscriber.save()
            except:
                logger.debug('Hangupcall Error cannot find the Subscriber!')
                return False

            #Update Callrequest Status
            if opt_hangup_cause == 'NORMAL_CLEARING':
                callrequest.status = CALLREQUEST_STATUS.SUCCESS
            else:
                callrequest.status = CALLREQUEST_STATUS.FAILURE
            callrequest.hangup_cause = opt_hangup_cause
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

            #If the call failed we will check if we want to make a retry call
            if (opt_hangup_cause != 'NORMAL_CLEARING'
               and callrequest.call_type == CALLREQUEST_TYPE.ALLOW_RETRY):
                #Update to Retry Done
                callrequest.call_type = CALLREQUEST_TYPE.RETRY_DONE
                callrequest.save()

                dialer_set = user_dialer_setting(callrequest.user)
                #check if we are allowed to retry on failure
                if ((obj_subscriber.count_attempt - 1) >= callrequest.campaign.maxretry
                   or (obj_subscriber.count_attempt - 1) >= dialer_set.maxretry
                   or not callrequest.campaign.maxretry):
                    logger.error("Not allowed retry - Maxretry (%d)" %
                                 callrequest.campaign.maxretry)
                    #Check here if we should try for completion
                    check_retrycall_completion(callrequest)
                else:
                    #Allowed Retry

                    # TODO : Review Logic
                    # Create new callrequest, Assign parent_callrequest,
                    # Change callrequest_type & num_attempt
                    new_callrequest = Callrequest(
                        request_uuid=uuid1(),
                        parent_callrequest_id=callrequest.id,
                        call_type=CALLREQUEST_TYPE.ALLOW_RETRY,
                        num_attempt=callrequest.num_attempt + 1,
                        user=callrequest.user,
                        campaign_id=callrequest.campaign_id,
                        aleg_gateway_id=callrequest.aleg_gateway_id,
                        content_type=callrequest.content_type,
                        object_id=callrequest.object_id,
                        phone_number=callrequest.phone_number,
                        timelimit=callrequest.timelimit,
                        callerid=callrequest.callerid,
                        timeout=callrequest.timeout,
                        content_object=callrequest.content_object,
                        subscriber=callrequest.subscriber
                    )
                    new_callrequest.save()
                    #TODO: Check if it's a good practice
                    #implement a PID algorithm
                    second_towait = callrequest.campaign.intervalretry
                    logger.info("Init Retry CallRequest in  %d seconds" % second_towait)
                    init_callrequest.apply_async(
                        args=[new_callrequest.id, callrequest.campaign.id, callrequest.campaign.callmaxduration],
                        countdown=second_towait)
            else:
                #The Call is Answered
                logger.info("Check for completion call")

                #Check if we should relaunch a new call to achieve completion
                check_retrycall_completion(callrequest)

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
