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
from rest_framework import serializers
from appointment.models.alarms import Alarm
from appointment.models.events import Event
from appointment.function_def import get_calendar_user_id_list
from survey.models import Survey


class AlarmSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"alarm_phonenumber": "1234567", "alarm_email": "xyz@gmail.com", "daily_start": "12:34:43", "daily_stop": "14:43:32", "method": "1", "survey": "http://127.0.0.1:8000/rest-api/sealed-survey/1/", "event": "http://127.0.0.1:8000/rest-api/event/1/", "result": "1"}' http://localhost:8000/rest-api/alarm/

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

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/alarm/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/alarm/%alarm-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "survey": null,
                        "mail_template": null,
                        "sms_template": null,
                        "event": "reminder_event: 2013-11-05 - 2013-11-30",
                        "url": "http://127.0.0.1:8000/rest-api/alarm/4/",
                        "daily_start": "12:13:33",
                        "daily_stop": "00:00:00",
                        "advance_notice": 0,
                        "maxretry": 0,
                        "retry_delay": 0,
                        "num_attempt": 0,
                        "method": 1,
                        "date_start_notice": "2013-11-05T06:43:47Z",
                        "status": 1,
                        "result": null,
                        "url_cancel": "",
                        "phonenumber_sms_failure": "",
                        "url_confirm": "",
                        "phonenumber_transfer": "",
                        "created_date": "2013-11-05T06:43:52.118Z"
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"alarm_phonenumber": "1234567", "alarm_email": "xyz@gmail.com", "daily_start": "12:34:43", "daily_stop": "14:43:32", "method": "1", "survey": "http://127.0.0.1:8000/rest-api/sealed-survey/1/", "event": "http://127.0.0.1:8000/rest-api/event/1/", "result": "1"}' http://localhost:8000/rest-api/alarm/%alarm-id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/rest-api/alarm/%alarm-id%/
    """
    class Meta:
        model = Alarm

    def get_fields(self, *args, **kwargs):
        """filter content_type field"""
        fields = super(AlarmSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']
        calendar_user_list = get_calendar_user_id_list(request.user)

        fields['event'].queryset = Event.objects.filter(calendar__user_id__in=calendar_user_list).order_by('id')
        fields['survey'].queryset = Survey.objects.filter(user=request.user)
        return fields
