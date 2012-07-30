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
from tastypie.exceptions import ImmediateHttpResponse, \
                                BadRequest
from tastypie import http

from dialer_cdr.models import Callrequest
from api.resources import CustomXmlEmitter, \
                          IpAddressAuthorization, \
                          IpAddressAuthentication,\
                          create_voipcall,\
                          CDR_VARIABLES

import logging
import urllib

logger = logging.getLogger('newfies.filelog')


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
        logger.debug('CDR API get called from IP %s' %\
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
                    logger.debug("%s not found!")

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

                error_msg = "Error, there is no callrequest for "\
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
            return self.create_response(request,\
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
