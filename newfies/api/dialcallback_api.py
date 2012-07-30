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
from api.resources import CustomXmlEmitter, \
                          IpAddressAuthorization, \
                          IpAddressAuthentication, \
                          create_voipcall, \
                          CDR_VARIABLES

import logging

logger = logging.getLogger('newfies.filelog')


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
            errors['CallRequest'] = ["Call request not found - uuid:%s" %\
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

    def prepend_urls(self):
        """Prepend urls"""
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
