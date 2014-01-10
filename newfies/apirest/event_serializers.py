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
from appointment.models.events import Event
from appointment.models.users import CalendarUser
from appointment.function_def import get_calendar_user_id_list


class EventSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"title": "event_title", "start": "2013-12-10 12:34:43", "end": "2013-12-15 14:43:32", "creator": "http://127.0.0.1:8000/rest-api/calendar-user/4/", "end_recurring_period": "2013-12-27 12:23:34", "calendar": "http://127.0.0.1:8000/rest-api/calendar/1/", "status": "1"}' http://localhost:8000/rest-api/event/

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

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/event/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/event/%event-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {

                        "url": "http://127.0.0.1:8000/rest-api/event/1/",
                        "title": "cal-event",
                        "description": "",
                        "start": "2013-12-02T07:48:27Z",
                        "end": "2013-12-02T08:48:27Z",
                        "creator": "http://127.0.0.1:8000/rest-api/calendar-user/3/",
                        "created_on": "2013-12-02T07:48:27Z",
                        "end_recurring_period": "2014-01-02T07:48:27Z",
                        "rule": null,
                        "calendar": "http://127.0.0.1:8000/rest-api/calendar/1/",
                        "notify_count": 0,
                        "status": 1,
                        "data": null,
                        "parent_event": null,
                        "occ_count": 0
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"title": "event_title", "start": "2013-12-10 12:34:43", "end": "2013-12-15 14:43:32", "creator": "http://127.0.0.1:8000/rest-api/calendar-user/4/", "end_recurring_period": "2013-12-27 12:23:34", "calendar": "http://127.0.0.1:8000/rest-api/calendar/1/", "status": "1"}' http://localhost:8000/rest-api/event/%event-id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/rest-api/event/%event-id%/

    **update_last_child_status**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"status": "1"}' http://localhost:8000/rest-api/event/%event-id%/update_last_child_status/

        Response::

            {"status": "event status has been updated"}


    **get_list_child**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/event/%event-id%/get_list_child/

        Response::

            {
                "url": "http://localhost:8000/rest-api/event/2/",
                "start": "2013-12-24 08:55:13+00:00",
                "end": "2013-12-31 09:55:13+00:00",
                "description": "",
                "title": "test-child-event"
            }
    """

    class Meta:
        model = Event

    def get_fields(self, *args, **kwargs):
        """filter content_type field"""
        fields = super(EventSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']
        calendar_user_list = get_calendar_user_id_list(request.user)

        fields['creator'].queryset = CalendarUser.objects.filter(id__in=calendar_user_list).order_by('id')
        fields['calendar'].queryset = Calendar.objects.filter(user_id__in=calendar_user_list).order_by('id')
        fields['parent_event'].queryset = Event.objects.filter(calendar__user_id__in=calendar_user_list).order_by('id')

        return fields
