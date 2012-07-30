# -*- coding: utf-8 -*-

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

from django.conf.urls.defaults import url
from django.http import HttpResponse

from tastypie.resources import ModelResource
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie.exceptions import ImmediateHttpResponse
from tastypie import http

from dialer_cdr.models import Callrequest
from dialer_cdr.tasks import init_callrequest
from dialer_campaign.models import CampaignSubscriber
from dialer_campaign.function_def import user_dialer_setting
from api.resources import CustomXmlEmitter, \
                          IpAddressAuthorization, \
                          IpAddressAuthentication,\
                          create_voipcall,\
                          CDR_VARIABLES
from datetime import datetime, timedelta
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
            errors['CallRequest'] = ["CallRequest not found - uuid:%s" %\
                                     opt_request_uuid]
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
        """Override url"""
        return [
            url(r'^(?P<resource_name>%s)/$' %\
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
            if opt_hangup_cause != 'NORMAL_CLEARING'\
            and callrequest.call_type == 1:  # Allow retry
                #Update to Retry Done
                callrequest.call_type = 3
                callrequest.save()

                dialer_set = user_dialer_setting(callrequest.user)
                if callrequest.num_attempt >= callrequest.campaign.maxretry\
                or callrequest.num_attempt >= dialer_set.maxretry:
                    logger.error("Not allowed retry - Maxretry (%d)" %\
                                 callrequest.campaign.maxretry)
                else:
                    #Allowed Retry

                    # TODO : Review Logic
                    # Create new callrequest, Assign parent_callrequest,
                    # Change callrequest_type & num_attempt
                    new_callrequest = Callrequest(
                        request_uuid=uuid1(),
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
                    logger.info("Init Retry CallRequest at %s" %\
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
