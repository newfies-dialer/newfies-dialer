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
from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponse

from tastypie.resources import ModelResource
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie.exceptions import ImmediateHttpResponse
from tastypie import http

from dialer_cdr.models import Callrequest
from settings_local import PLIVO_DEFAULT_DIALCALLBACK_URL
from api.resources import CustomXmlEmitter, \
                          IpAddressAuthorization, \
                          IpAddressAuthentication
from common_functions import search_tag_string

import logging

logger = logging.getLogger('newfies.filelog')


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

            #TODO: If we update the Call to success here we should
            # not do it in hangup url
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
                    dial_command = 'Dial timeLimit="%s" ' \
                                   'callerId="%s" ' \
                                   'callbackUrl="%s"' % \
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

                        audiofile_url = domain + settings.MEDIA_URL +\
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

