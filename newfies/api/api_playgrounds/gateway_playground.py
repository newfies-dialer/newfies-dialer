#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django.utils.translation import gettext as _
from apiplayground import APIPlayground


class GatewayAPIPlayground(APIPlayground):

    schema = {
        "title": _("Gateway API Playground"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/gateway/",
                "description": _("This resource allows you to manage gateways."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/gateway/",
                        "description": _("Returns all gateways")
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/gateway/{gateway-id}/",
                        "description": _("Returns a specific gateway")
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/gateway/",
                        "description": _("Creates new gateway"),
                        "parameters": [{
                                           "name": "name",
                                           "type": "string",
                                           "default": "Gateway Name"
                                       },
                                       {
                                           "name": "description",
                                           "type": "string",
                                       },
                                       {
                                           "name": "addprefix",
                                           "type": "string",
                                           "default": "91"
                                       },
                                       {
                                           "name": "removeprefix",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "gateways",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "gateway_codecs",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "gateway_timeouts",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "gateway_retries",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "originate_dial_string",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "secondused",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "failover",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "addparameter",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "count_call",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "count_in_use",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "maximum_call",
                                           "type": "string",
                                           "default": ""
                                       },
                                       ]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/gateway/{gateway-id}/",
                        "description": _("Update gateway"),
                        "parameters": [{
                                           "name": "name",
                                           "type": "string"
                                       },
                                       {
                                           "name": "description",
                                           "type": "string"
                                       },
                                       {
                                           "name": "addprefix",
                                           "type": "string",
                                           "default": "91"
                                       },
                                       {
                                           "name": "removeprefix",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "gateways",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "gateway_codecs",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "gateway_timeouts",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "gateway_retries",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "originate_dial_string",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "secondused",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "failover",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "addparameter",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "count_call",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "count_in_use",
                                           "type": "string",
                                           "default": ""
                                       },
                                       {
                                           "name": "maximum_call",
                                           "type": "string",
                                           "default": ""
                                       },
                                       ]
                    },
                    {
                        "method": "DELETE",
                        "url": "/api/v1/gateway/{gateway-id}/",
                        "description": _("Delete gateway"),
                        }
                ]
            },
            ]
    }
