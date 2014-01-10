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
from appointment.models.users import CalendarUser


class CalendarUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"username": "caluser2", "password": "caluser2", "email": "xyz@gmail.com"}' http://localhost:8000/rest-api/calendar-user/

        Response::

            HTTP/1.0 201 CREATED
            Date: Mon, 16 Dec 2013 11:00:39 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Language: en
            Content-Type: application/json; charset=utf-8
            Location: http://localhost:8000/rest-api/calendar-user/5/
            Allow: GET, POST, HEAD, OPTIONS

            {"url": "http://localhost:8000/rest-api/calendar-user/5/", "username": "caluser2", "password": "pbkdf2_sha256$12000$RKQtziT23qoz$WiVneuVVTbi2NjSmLCmuXeQTEMoHYnqAaC0/nUUaNtM=", "last_name": "", "first_name": "", "email": "xyz@gmail.com", "groups": []}

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/calendar-user/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/calendar-user/%calendar-user-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/calendar-user/3/",
                        "username": "agent",
                        "last_name": "",
                        "first_name": "",
                        "email": "",
                        "groups": []
                    }
                ]
            }

    **Delete**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/rest-api/calendar-user/%calendar-user-id%/
    """

    class Meta:
        model = CalendarUser
        fields = ('username', 'password', 'last_name', 'first_name', 'email')
