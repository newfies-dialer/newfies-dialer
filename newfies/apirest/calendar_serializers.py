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
from appointment.models.calendars import Calendar
from appointment.models.users import CalendarUser
from appointment.function_def import get_calendar_user_id_list


class CalendarSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "mycalendar", "max_concurrent": "1", "user": "http://127.0.0.1:8000/rest-api/calendar-user/4/"}' http://localhost:8000/rest-api/calendar/

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

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/calendar/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/calendar/%calendar-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/calendar/1/",
                        "name": "calendar_I",
                        "user": "http://127.0.0.1:8000/rest-api/calendar-user/3/",
                        "max_concurrent": 0,
                        "created_date": "2013-12-02T07:48:21.136Z"
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"name": "mycalendar", "max_concurrent": "1", "user": "http://127.0.0.1:8000/rest-api/calendar-user/4/"}' http://localhost:8000/rest-api/calendar/%calendar-id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/rest-api/calendar/%calendar-id%/
    """

    class Meta:
        model = Calendar

    def get_fields(self, *args, **kwargs):
        """filter calendar user field"""
        fields = super(CalendarSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']
        calendar_user_list = get_calendar_user_id_list(request.user)
        fields['user'].queryset = CalendarUser.objects.filter(id__in=calendar_user_list).order_by('id')

        return fields
