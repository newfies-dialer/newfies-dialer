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
from agent.models import Agent, AgentProfile
from appointment.function_def import get_calendar_user_id_list


class AgentProfileSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"level": "2", "position": "1"}' http://localhost:8000/rest-api/tier/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Location: http://localhost:8000/rest-api/tier/1/
            Allow: GET, POST, HEAD, OPTIONS

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/tier/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "manager": "manager",
                        "agent": "agent",
                        "queue": "Sample queue",
                        "url": "http://127.0.0.1:8000/rest-api/tier/1/",
                        "level": 1,
                        "position": 1,
                        "created_date": "2013-10-23T13:09:43.311Z",
                        "updated_date": "2013-10-23T13:09:43.311Z"
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"level": "2"}' http://localhost:8000/rest-api/tier/%dtier-id%/

        Response::

            HTTP/1.0 202 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    manager = serializers.Field(source='manager')

    class Meta:
        model = AgentProfile

    def get_fields(self, *args, **kwargs):
        """filter field"""
        fields = super(AgentProfileSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']
        calendar_user_list = get_calendar_user_id_list(request.user)
        fields['user'].queryset = Agent.objects.filter(is_staff=False, is_superuser=False).exclude(id__in=calendar_user_list)

        return fields
