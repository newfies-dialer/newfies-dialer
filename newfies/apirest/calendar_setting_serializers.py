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
from django.conf import settings
from rest_framework import serializers
from appointment.models.users import CalendarSetting
from survey.models import Survey
from audiofield.models import AudioFile
from user_profile.models import UserProfile


class CalendarSettingSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"label": "calendar_setting", "callerid": "123456", "caller_name": "xyz", "user": "http://127.0.0.1:8000/rest-api/user/2/", "survey": "http://127.0.0.1:8000/rest-api/sealed-survey/1/", "aleg_gateway": "http://127.0.0.1:8000/rest-api/gateway/1/", "sms_gateway": "http://127.0.0.1:8000/rest-api/sms-gateway/1/"}' http://localhost:8000/rest-api/calendar-setting/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Allow: GET, POST, HEAD, OPTIONS

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/calendar-setting/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/calendar-setting/%calendar-setting-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "user": "manager",
                        "url": "http://127.0.0.1:8000/rest-api/calendar-setting/1/",
                        "label": "cal_setting_label",
                        "callerid": "32423",
                        "caller_name": "cal_serting",
                        "call_timeout": 60,
                        "survey": "http://127.0.0.1:8000/rest-api/sealed-survey/1/",
                        "aleg_gateway": "http://127.0.0.1:8000/rest-api/gateway/1/",
                        "sms_gateway": "http://127.0.0.1:8000/rest-api/gateway/1/",
                        "voicemail": false,
                        "amd_behavior": null,
                        "voicemail_audiofile": null,
                        "created_date": "2013-12-02T07:20:54.490Z",
                        "updated_date": "2013-12-02T12:18:52.385Z"
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"label": "calendar_setting", "callerid": "123456", "caller_name": "xyz", "user": "http://127.0.0.1:8000/rest-api/user/2/", "survey": "http://127.0.0.1:8000/rest-api/sealed-survey/1/", "aleg_gateway": "http://127.0.0.1:8000/rest-api/gateway/1/", "sms_gateway": "http://127.0.0.1:8000/rest-api/sms-gateway/1/"}' http://localhost:8000/rest-api/calendar-setting/%calendar-setting-id%/

        Response::

            HTTP/1.0 200 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    **Delete**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/rest-api/calendar-setting/%calendar-setting-id%/
    """
    user = serializers.Field(source='user')
    sms_gateway = serializers.HyperlinkedRelatedField(
        read_only=False, view_name='sms-gateway-detail')

    class Meta:
        model = CalendarSetting

    def get_fields(self, *args, **kwargs):
        """filter survey field"""
        fields = super(CalendarSettingSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']

        if request.method != 'GET':
            fields['survey'].queryset = Survey.objects.filter(user=request.user)

        fields['aleg_gateway'].queryset = UserProfile.objects.get(user=request.user).userprofile_gateway.all()
        if settings.AMD:
            fields['voicemail_audiofile'].queryset = AudioFile.objects.filter(user=request.user)

        return fields
