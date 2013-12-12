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
from appointment.models.alarms import Alarm, AlarmRequest
from dialer_cdr.models import Callrequest
from appointment.function_def import get_calendar_user_id_list


class AlarmRequestSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"alarm": "http://localhost:8000/rest-api/alarm/1/", "date": "2013-12-12 12:45:33", "status": "1", "callrequest": "http://localhost:8000/rest-api/callrequest/1/"}' http://localhost:8000/rest-api/alarm-request/

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"alarm": "1", "date": "2013-12-12 12:45:33", "status": "1", "callrequest": "2"}' http://localhost:8000/rest-api/alarm-request/

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

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/alarm-request/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/alarm-request/%alarm-request-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "alarm": "4",
                        "url": "http://127.0.0.1:8000/rest-api/alarm-request/2/",
                        "date": "2013-11-05T06:30:00Z",
                        "status": 1,
                        "callstatus": 0,
                        "calltime": "2013-11-05T06:30:00Z",
                        "duration": 0,
                        "callrequest": null,
                        "created_date": "2013-11-05T06:46:18.635Z"
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"alarm": "http://localhost:8000/rest-api/alarm/1/", "date": "2013-12-12 12:45:33", "status": "1", "callrequest": "http://localhost:8000/rest-api/callrequest/1/"}' http://localhost:8000/rest-api/alarm-request/%alarm-request-id%/

        Response::

            HTTP/1.0 200 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """

    class Meta:
        model = AlarmRequest

    def get_fields(self, *args, **kwargs):
        """filter content_type field"""
        fields = super(AlarmRequestSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']
        calendar_user_list = get_calendar_user_id_list(request.user)
        if request.method != 'GET' and self.init_data is not None:
            callrequest = self.init_data.get('callrequest')
            if callrequest and callrequest.find('http://') == -1:
                try:
                    Callrequest.objects.get(pk=callrequest, campaign__user=request.user)
                    self.init_data['callrequest'] = '/rest-api/callrequest/%s/' % callrequest
                except:
                    self.init_data['callrequest'] = ''
                    pass

            alarm = self.init_data.get('alarm')
            if alarm and alarm.find('http://') == -1:
                try:
                    Alarm.objects.filter(pk=alarm, event__creator_id__in=calendar_user_list)
                    self.init_data['alarm'] = '/rest-api/alarm/%s/' % alarm
                except:
                    self.init_data['alarm'] = ''
                    pass

        fields['alarm'].queryset = Alarm.objects.filter(event__creator_id__in=calendar_user_list)
        fields['callrequest'].queryset = Callrequest.objects.filter(campaign__user=request.user)
        return fields

