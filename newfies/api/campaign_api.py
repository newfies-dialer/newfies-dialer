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

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from tastypie.resources import ModelResource, ALL
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie.exceptions import BadRequest
from tastypie import fields

from api.user_api import UserResource
from api.gateway_api import GatewayResource
from api.audiofile_api import AudioFileResource
from api.content_type_api import ContentTypeResource
from api.phonebook_api import PhonebookResource
from api.resources import get_value_if_none
from dialer_contact.models import Phonebook
from dialer_campaign.models import Campaign
from dialer_gateway.models import Gateway
from dialer_campaign.function_def import \
    user_attached_with_dialer_settings, check_dialer_setting, \
    dialer_setting_limit
from audiofield.models import AudioFile
import time
import logging

logger = logging.getLogger('newfies.filelog')


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
            # expires in 90 days
            expirationdate = get_value_if_none(expirationdate,
                time.time() + 86400 * 90)
            #Startdate and expirationdate are UTC -> convert to localtime
            startingdate = float(startingdate) - time.altzone
            expirationdate = float(expirationdate) - time.altzone

            bundle.data['startingdate'] = time.strftime('%Y-%m-%d %H:%M:%S',
                time.gmtime(startingdate))
            bundle.data['expirationdate'] = time.strftime('%Y-%m-%d %H:%M:%S',
                time.gmtime(expirationdate))

        if request.method == 'PUT':
            if startingdate:
                bundle.data['startingdate'] = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.gmtime(float(startingdate)))
            if expirationdate:
                bundle.data['expirationdate'] = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.gmtime(float(expirationdate)))

        if user_attached_with_dialer_settings(request):
            errors['user_dialer_setting'] = ['Your settings are not configured properly, Please contact the administrator.']

        if check_dialer_setting(request, check_for="campaign"):
            errors['chk_campaign'] = ["Too many campaigns. Max allowed %s"
                % dialer_setting_limit(request, limit_for="campaign")]

        frequency = bundle.data.get('frequency')
        if frequency:
            if check_dialer_setting(request, check_for="frequency", field_value=int(frequency)):
                errors['chk_frequency'] = ["Frequency limit of %s exceeded."
                    % dialer_setting_limit(request, limit_for="frequency")]

        callmaxduration = bundle.data.get('callmaxduration')
        if callmaxduration:
            if check_dialer_setting(request, check_for="duration", field_value=int(callmaxduration)):
                errors['chk_duration'] = ["Duration limit of %s exceeded."
                    % dialer_setting_limit(request, limit_for="duration")]

        maxretry = bundle.data.get('maxretry')
        if maxretry:
            if check_dialer_setting(request, check_for="retry", field_value=int(maxretry)):
                errors['chk_duration'] = ["Retries limit of %s exceeded."
                    % dialer_setting_limit(request, limit_for="retry")]

        calltimeout = bundle.data.get('calltimeout')
        if calltimeout:
            if check_dialer_setting(request, check_for="timeout", field_value=int(calltimeout)):
                errors['chk_timeout'] = ["Timeout limit of %s exceeded."
                    % dialer_setting_limit(request, limit_for="timeout")]

        aleg_gateway_id = bundle.data.get('aleg_gateway')
        if aleg_gateway_id:
            try:
                aleg_gateway_id = Gateway.objects.get(id=aleg_gateway_id).id
                bundle.data['aleg_gateway'] = '/api/v1/gateway/%s/' %\
                                              aleg_gateway_id
            except:
                errors['chk_gateway'] = ["The Gateway ID doesn't exist!"]

        content_type = bundle.data.get('content_type')
        if content_type == 'voiceapp_template' or content_type == 'survey_template':
            try:
                content_type_id = ContentType.objects\
                    .get(model=str(content_type)).id
                bundle.data['content_type'] = '/api/v1/contenttype/%s/' %\
                                              content_type_id
            except:
                errors['chk_content_type'] = ["The ContentType doesn't exist!"]
        else:
            errors['chk_content_type'] = ["Entered wrong option. Please enter 'voice_app' or 'survey' !"]

        object_id = bundle.data.get('object_id')
        if object_id:
                bundle.data['object_id'] = object_id
        else:
            errors['chk_object_id'] = ["App Object ID doesn't exist!"]

        try:            
            bundle.data['user'] = '/api/v1/user/%s/' % request.user.id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        if request.method == 'POST':
            name_count = Campaign.objects.filter(name=bundle.data.get('name'),
                user=request.user).count()
            if (name_count != 0):
                errors['chk_campaign_name'] = ["The Campaign name duplicated!"]

        # Voicemail setting is not enabled by default
        if settings.AMD:
            voicemail = bundle.data.get('voicemail')
            if voicemail:
                bundle.data['voicemail'] = voicemail
                amd_behavior = bundle.data.get('amd_behavior')
                audiofile_id = bundle.data.get('voicemail_audiofile')
                if audiofile_id:
                    try:
                        audiofile_id = AudioFile.objects.get(id=audiofile_id).id
                        bundle.data['voicemail_audiofile'] = '/api/v1/audiofile/%s/' %\
                                                             audiofile_id
                    except:
                        errors['voicemail_audiofile'] = ["The audiofile ID doesn't exist!"]
            else:
                errors['voicemail'] = ["voicemail not enabled!"]

        return errors


class CampaignResource(ModelResource):
    """
    **Attributes**:

            * ``campaign_code`` - Auto-generated campaign code
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

            # Voicemail setting is not enabled by default
            * ``voicemail`` - Enable Voicemail Detection
            * ``amd_behavior`` - Detection Behaviour
            * ``voicemail_audiofile`` - Foreign key relationship to the a AudioFile model.

        **Campaign Settings**:

            * ``frequency`` - Defines the frequency, speed of the campaign.\
                              This is the number of calls per minute.
            * ``callmaxduration`` - Maximum call duration.
            * ``maxretry`` - Defines the max retries allowed per user.
            * ``intervalretry`` - Defines the time to wait between retries\
                                  in seconds
            * ``completion_maxretry`` - Amount of retries until a contact is completed. Completed means that it reachs a point in the phone application marked as completed
            * ``intervalretry`` - Time delay in seconds before retrying contact for completion
            * ``calltimeout`` - Set seconds of call timeout

        **Gateways**:

            * ``aleg_gateway`` - Defines the Gateway to use to call the\
                                 subscriber
            * ``content_type`` - Defines the application (``voice_app_template`` \
                                or ``survey_template``) to use when the \
                                call is established on the A-Leg
            * ``object_id`` - Defines the object of content_type application
            * ``extra_data`` - Defines the additional data to pass to the\
                                application

    **Validation**:

        * CampaignValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "mycampaign", "description": "", "callerid": "1239876", "startingdate": "1301392136.0", "expirationdate": "1301332136.0", "frequency": "20", "callmaxduration": "50", "maxretry": "3", "intervalretry": "3000", "calltimeout": "45", "aleg_gateway": "1", "content_type": "voiceapp_template", "object_id" : "1", "extra_data": "2000", "phonebook_id": "1", "voicemail": "True", "amd_behavior": "1", "voicemail_audiofile": "1"}' http://localhost:8000/api/v1/campaign/

        Response::

            HTTP/1.0 200 OK
            Date: Thu, 08 Dec 2011 13:05:50 GMT
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
                     "completion_intervalretry":0,
                     "completion_maxretry":0,
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
                     "content_type":"/api/v1/contrib/contenttype/1/",
                     "object_id":1,
                     "wednesday":true
                  }
               ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"name": "mylittlecampaign", "description": "", "callerid": "1239876", "startingdate": "1301392136.0", "expirationdate": "1301332136.0","frequency": "20", "callmaxduration": "50", "maxretry": "3", "intervalretry": "3000", "calltimeout": "60", "aleg_gateway": "1", "content_type": "survey", "object_id" : "1", "extra_data": "2000" }' http://localhost:8000/api/v1/campaign/%campaign_id%/

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
                     "content_type":"/api/v1/contrib/contenttype/1/",
                     "object_id":1,
                     "wednesday":true
                  }
               ]
            }
    """
    user = fields.ForeignKey(UserResource, 'user', full=True)
    aleg_gateway = fields.ForeignKey(GatewayResource,
        'aleg_gateway', full=True)
    content_type = fields.ForeignKey(ContentTypeResource,
        'content_type')
    phonebook = fields.ToManyField(PhonebookResource,
        'phonebook', full=True, readonly=True)
    # Voicemail setting is not enabled by default
    voicemail_audiofile = fields.ForeignKey(AudioFileResource,
        'voicemail_audiofile', full=True)

    class Meta:
        queryset = Campaign.objects.all()
        resource_name = 'campaign'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = CampaignValidation()
        list_allowed_methods = ['post', 'get', 'put', 'delete']
        detail_allowed_methods = ['post', 'get', 'put', 'delete']
        filtering = {
            'name': ALL,
            'status': ALL,
        }
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)

    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        logger.debug('Campaign API get called')

        #Uncomment this, it seems to fix API for some users
        #self.is_valid(bundle, request)
        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        bundle = self.full_hydrate(bundle)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        bundle.obj.save()

        try:
            phonebook_obj = Phonebook.objects.get(
                pk=bundle.data['phonebook_id'])
            bundle.obj.phonebook.add(phonebook_obj)
            bundle.obj.save()
        except:
            # if phonebook_id doesn't exist, create new phonebook
            try:
                # New phonebook
                new_phonebook = Phonebook.objects.create(user=request.user,
                    name=bundle.obj.name + '-' + bundle.obj.campaign_code,
                    description='Auto created Phonebook from API')
                bundle.obj.phonebook.add(new_phonebook)
                bundle.obj.save()
            except:
                #raise
                error_msg = 'Auto-Created Phonebook Name duplicated!'
                logger.error(error_msg)
                raise BadRequest(error_msg)

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        logger.debug('Campaign API : Result ok 200')
        return bundle
