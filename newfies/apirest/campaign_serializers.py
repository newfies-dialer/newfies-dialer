# -*- coding: utf-8 -*-

#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from rest_framework import serializers
from dialer_campaign.models import Campaign
from dialer_campaign.function_def import (user_dialer_setting,
    check_dialer_setting, dialer_setting_limit)
from dialer_contact.models import Phonebook
from audiofield.models import AudioFile
from dnc.models import DNC
from sms.models import Gateway as SMS_Gateway
from user_profile.models import UserProfile


class CampaignSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "mycampaign", "description": "", "callerid": "1239876", "startingdate": "2013-06-13 13:13:33", "expirationdate": "2013-06-14 13:13:33", "frequency": "20", "callmaxduration": "50", "maxretry": "3", "intervalretry": "3000", "calltimeout": "45", "aleg_gateway": "/rest-api/gateway/1/", "sms_gateway": "/rest-api/sms-gateway/1/", "content_type": "/rest-api/content_type/49/", "object_id" : "1", "extra_data": "2000", "phonebook_id": "1", "voicemail": "True", "amd_behavior": "1", "voicemail_audiofile": "1", "dnc": "/rest-api/dnc/1/", "phonebook": "1"}' http://localhost:8000/rest-api/campaigns/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Allow: GET, POST, HEAD, OPTIONS

            {"id": 1, "campaign_code": "JDQBG", "name": "mycampaign1", "description": "", "callerid": "1239876", "phonebook": ["/rest-api/phonebook/1/", "/rest-api/phonebook/2/"], "startingdate": "2013-06-13T13:13:33", "expirationdate": "2013-06-14T13:13:33", "aleg_gateway": "http://localhost:8000/rest-api/gateway/1/", "user": "http://localhost:8000/rest-api/users/1/", "status": 2, "content_type": "http://localhost:8000/rest-api/content_type/49/", "object_id": 1, "extra_data": "2000", "dnc": null, "frequency": 20, "callmaxduration": 50, "maxretry": 3, "intervalretry": 3000, "calltimeout": 45, "daily_start_time": "00:00:00", "daily_stop_time": "23:59:59", "monday": true, "tuesday": true, "wednesday": true, "thursday": true, "friday": true, "saturday": true, "sunday": true, "completion_maxretry": 0, "completion_intervalretry": 900}


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/campaigns/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/campaigns/%campaign-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "id": 2,
                        "campaign_code": "BXTWX",
                        "name": "Sample survey campaign",
                        "description": "",
                        "callerid": "",
                        "phonebook": [
                            "http://127.0.0.1:8000/rest-api/phonebook/1/"
                        ],
                        "startingdate": "2011-12-27T14:35:46",
                        "expirationdate": "2011-12-28T14:35:46",
                        "aleg_gateway": "http://127.0.0.1:8000/rest-api/gateway/1/",
                        "user": "http://127.0.0.1:8000/rest-api/users/1/",
                        "status": 2,
                        "content_type": "http://127.0.0.1:8000/rest-api/content_type/49/",
                        "object_id": 1,
                        "extra_data": "",
                        "dnc": "http://127.0.0.1:8000/rest-api/dnc/1/",
                        "voicemail": false,
                        "amd_behavior": null,
                        "voicemail_audiofile": null,
                        "frequency": 10,
                        "callmaxduration": 1800,
                        "maxretry": 0,
                        "intervalretry": 300,
                        "calltimeout": 45,
                        "daily_start_time": "00:00:00",
                        "daily_stop_time": "23:59:59",
                        "monday": true,
                        "tuesday": true,
                        "wednesday": true,
                        "thursday": true,
                        "friday": true,
                        "saturday": true,
                        "sunday": true,
                        "completion_maxretry": 0,
                        "completion_intervalretry": 900
                    }
                ]
            }


    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"name": "mylittlecampaign243"}' http://localhost:8000/rest-api/campaigns/%campaign-id%/

        Response::

            HTTP/1.0 202 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

            {"id": 1, "campaign_code": "JDQBG", "name": "mylittlecampaign243", "description": "", "callerid": "1239876", "phonebook": ["http://localhost:8000/rest-api/phonebook/1/", "http://localhost:8000/rest-api/phonebook/2/"], "startingdate": "2013-06-13T13:13:33", "expirationdate": "2013-06-14T13:13:33", "aleg_gateway": "http://localhost:8000/rest-api/gateway/1/", "user": "http://localhost:8000/rest-api/users/1/", "status": 2, "content_type": "http://localhost:8000/rest-api/content_type/49/", "object_id": 1, "extra_data": "2000", "dnc": null, "frequency": 20, "callmaxduration": 50, "maxretry": 3, "intervalretry": 3000, "calltimeout": 45, "daily_start_time": "00:00:00", "daily_stop_time": "23:59:59", "monday": true, "tuesday": true, "wednesday": true, "thursday": true, "friday": true, "saturday": true, "sunday": true, "completion_maxretry": 0, "completion_intervalretry": 900}


    **Delete**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/rest-api/campaign/%campaign_id%/

        Response::

            {
                "data": "campaign deleted"
            }
    """
    user = serializers.Field(source='user')
    sms_gateway = serializers.HyperlinkedRelatedField(
        read_only=False, view_name='sms-gateway-detail')

    class Meta:
        model = Campaign
        fields = (
            'id', 'campaign_code', 'name', 'description', 'callerid',
            'phonebook', 'startingdate', 'expirationdate', 'aleg_gateway',
            'user', 'status', 'content_type', 'object_id', 'extra_data',
            'dnc', 'voicemail', 'amd_behavior', 'voicemail_audiofile',
            'frequency', 'callmaxduration', 'maxretry', 'intervalretry',
            'calltimeout', 'daily_start_time', 'daily_stop_time',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
            'saturday', 'sunday', 'completion_maxretry', 'sms_gateway',
            'completion_intervalretry',
            #'agent_script', 'lead_disposition', 'external_link'
        )

    def get_fields(self, *args, **kwargs):
        """filter content_type field"""
        fields = super(CampaignSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']

        if request.method != 'GET' and self.init_data is not None:
            phonebook = self.init_data.get('phonebook')
            if phonebook and phonebook.find('http://') == -1:
                try:
                    phonebook_id_list = phonebook.split(",")
                    m2m_phonebook = []
                    for i in phonebook_id_list:
                        try:
                            Phonebook.objects.get(pk=int(i), user=request.user)
                            m2m_phonebook.append('/rest-api/phonebook/%s/' % i)
                        except:
                            pass

                    if m2m_phonebook:
                        self.init_data['phonebook'] = m2m_phonebook
                    else:
                        self.init_data['phonebook'] = ''
                except:
                    self.init_data['phonebook'] = ''

        if request.method != 'GET':
            if not settings.AMD:
                del fields['voicemail']
                del fields['amd_behavior']
                del fields['voicemail_audiofile']
            else:
                fields['voicemail_audiofile'].queryset = AudioFile.objects.filter(user=request.user)

            fields['aleg_gateway'].queryset = UserProfile.objects.get(user=request.user).userprofile_gateway.all()
            fields['sms_gateway'].queryset = SMS_Gateway.objects.all()
            fields['dnc'].queryset = DNC.objects.filter(user=request.user)
            fields['phonebook'].queryset = Phonebook.objects.filter(user=request.user)

            if self.object and self.object.has_been_started:
                fields['content_type'].queryset = ContentType.objects.filter(model__in=["survey"])
            else:
                fields['content_type'].queryset = ContentType.objects.filter(model__in=["survey_template"])

        return fields

    def validate(self, attrs):
        """
        Validate campaign form
        """
        request = self.context['request']

        if request.method == 'POST':
            name_count = Campaign.objects.filter(name=attrs.get('name'),
                user=request.user).count()
            if name_count != 0:
                raise serializers.ValidationError("The Campaign name duplicated!")

        if not user_dialer_setting(request.user):
            raise serializers.ValidationError("Your settings are not configured properly, Please contact the administrator.")

        if check_dialer_setting(request, check_for="campaign"):
            raise serializers.ValidationError("Too many campaigns. Max allowed %s"
                    % dialer_setting_limit(request, limit_for="campaign"))

        frequency = attrs.get('frequency')
        if frequency:
            if check_dialer_setting(request, check_for="frequency", field_value=int(frequency)):
                raise serializers.ValidationError("Frequency limit of %s exceeded."
                    % dialer_setting_limit(request, limit_for="frequency"))

        callmaxduration = attrs.get('callmaxduration')
        if callmaxduration:
            if check_dialer_setting(request, check_for="duration", field_value=int(callmaxduration)):
                raise serializers.ValidationError("Duration limit of %s exceeded."
                    % dialer_setting_limit(request, limit_for="duration"))

        maxretry = attrs.get('maxretry')
        if maxretry:
            if check_dialer_setting(request, check_for="retry", field_value=int(maxretry)):
                raise serializers.ValidationError("Retries limit of %s exceeded."
                    % dialer_setting_limit(request, limit_for="retry"))

        calltimeout = attrs.get('calltimeout')
        if calltimeout:
            if check_dialer_setting(request, check_for="timeout", field_value=int(calltimeout)):
                raise serializers.ValidationError("Timeout limit of %s exceeded."
                    % dialer_setting_limit(request, limit_for="timeout"))

        return attrs
