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
from sms.models import Gateway as SMSGateway


class SMSGatewaySerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "My_Gateway", "description": "", "addprefix": "", "removeprefix": "", "gateways": "user/,user", "gateway_codecs": "PCMA,PCMU", "gateway_timeouts": "10,10", "gateway_retries": "2,1"}' http://localhost:8000/rest-api/gateway/

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

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/gateway/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/gateway/%gateway-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/gateway/1/",
                        "name": "Default_Gateway",
                        "status": 1,
                        "description": "",
                        "addprefix": "",
                        "removeprefix": "",
                        "gateways": "user/,user",
                        "gateway_codecs": "PCMA,PCMU",
                        "gateway_timeouts": "10,10",
                        "gateway_retries": "2,1",
                        "originate_dial_string": "",
                        "secondused": null,
                        "created_date": "2011-06-15T00:28:52",
                        "updated_date": "2013-06-14T17:54:24.130",
                        "failover": null,
                        "addparameter": "",
                        "count_call": 1,
                        "count_in_use": null,
                        "maximum_call": null
                    }
                ]
            }
    """
    _default_view_name = '%(app_label)s-%(model_name)s-detail'

    class Meta:
        model = SMSGateway
