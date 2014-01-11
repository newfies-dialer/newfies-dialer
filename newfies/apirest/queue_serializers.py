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
from callcenter.models import Queue


class QueueSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "queue name"}' http://localhost:8000/rest-api/queue/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Location: http://localhost:8000/rest-api/queue/1/
            Allow: GET, POST, HEAD, OPTIONS

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/queue/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "manager": "manager",
                        "url": "http://127.0.0.1:8000/rest-api/queue/1/",
                        "name": "Sample queue",
                        "strategy": 5,
                        "moh_sound": "",
                        "record_template": "",
                        "time_base_score": "queue",
                        "tier_rules_apply": false,
                        "tier_rule_wait_second": 300,
                        "tier_rule_wait_multiply_level": true,
                        "tier_rule_no_agent_no_wait": false,
                        "discard_abandoned_after": 14400,
                        "abandoned_resume_allowed": true,
                        "max_wait_time": 0,
                        "max_wait_time_with_no_agent": 120,
                        "max_wait_time_with_no_agent_time_reached": 5,
                        "created_date": "2013-10-23T12:34:20.157Z",
                        "updated_date": "2013-10-23T12:34:20.157Z"
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"name": "change name"}' http://localhost:8000/rest-api/queue/%dqueue-id%/

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
        model = Queue
