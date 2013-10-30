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
from appointment.models.users import CalendarUser


class CalendarUserSerializer(serializers.HyperlinkedModelSerializer):
    """
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
    """
    class Meta:
        model = CalendarUser
        fields = ('url', 'username', 'last_name', 'first_name', 'email', 'groups')
