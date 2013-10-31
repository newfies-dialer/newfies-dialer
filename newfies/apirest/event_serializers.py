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
from appointment.models.events import Event


class EventSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "myrule", "frequency": "YEARLY", "params": "1"}' http://localhost:8000/rest-api/event/

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

                        "creator": "areski",
                        "url": "http://127.0.0.1:8000/rest-api/event/1/",
                        "start": "2013-10-31T07:51:11Z",
                        "end": "2013-10-31T07:51:11Z",
                        "title": "sample event",
                        "description": "",
                        "created_on": "2013-10-31T07:51:11Z",
                        "rule": "http://127.0.0.1:8000/rest-api/rule/1/",
                        "end_recurring_period": null,
                        "calendar": "http://127.0.0.1:8000/rest-api/calendar/1/",
                        "notify_count": 1,
                        "data": null,
                        "status": 1
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"name": "mylittle phonebook"}' http://localhost:8000/rest-api/event/%event-id%/

        Response::

            HTTP/1.0 200 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    creator = serializers.Field(source='creator')

    class Meta:
        model = Event

