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
from dialer_gateway.models import Gateway


class GatewaySerializer(serializers.HyperlinkedModelSerializer):
    """
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

    class Meta:
        model = Gateway
