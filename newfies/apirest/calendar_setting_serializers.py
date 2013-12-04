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

from rest_framework import serializers
from appointment.models.users import CalendarSetting
from survey.models import Survey


class CalendarSettingSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"callerid": "mycalendar", "caller_name": "cid name", "call_timeout": "1", "survey": "1"}' http://localhost:8000/rest-api/calendar-settings/

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

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/calendar-settings/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/calendar-settings/%calendar-settings-id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"callerid": "32423423", "caller_name": "cid name", "call_timeout": "1", "survey": "1"}' http://localhost:8000/rest-api/calendar-settings/%calendar-settings-id%/

        Response::

            HTTP/1.0 200 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    user = serializers.Field(source='user')

    class Meta:
        model = CalendarSetting

    def get_fields(self, *args, **kwargs):
        """filter survey field"""
        fields = super(CalendarSettingSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']

        if request.method != 'GET' and self.init_data is not None:
            survey = self.init_data.get('survey')
            if survey and survey.find('http://') == -1:
                try:
                    Survey.objects.get(pk=int(survey), user=request.user)
                    self.init_data['survey'] = '/rest-api/sealed-survey/%s/' % survey
                except:
                    self.init_data['survey'] = ''
                    pass

        if request.method != 'GET':
            fields['survey'].queryset = Survey.objects.filter(user=request.user)

        return fields
