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


class CallrequestAPIPlayground(APIPlayground):

    schema = {
        "title": _("Callrequest API Playground"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/callrequest/",
                "description": _("This resource allows you to manage callrequest."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/callrequest/",
                        "description": _("Returns all callrequests")
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/callrequest/{callrequest-id}/",
                        "description": _("Returns a specific callrequest")
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/callrequest/",
                        "description": _("Creates new callrequest"),
                        "parameters": [{
                                           "name": "request_uuid",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "2342jtdsf-00123"
                                       },
                                       {
                                           "name": "call_time",
                                           "type": "string",
                                           "default": "2011-10-20 12:21:22"
                                       },
                                       {
                                           "name": "phone_number",
                                           "type": "string",
                                           "default": "8792749823"
                                       },
                                       {
                                           "name": "content_type",
                                           "type": "string",
                                           "default": "voiceapp_template"
                                       },
                                       {
                                           "name": "object_id",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       {
                                           "name": "timeout",
                                           "type": "string",
                                           "default": "2000"
                                       },
                                       {
                                           "name": "callerid",
                                           "type": "string",
                                           "default": "650784355"
                                       },
                                       {
                                           "name": "call_type",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       ]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/callrequest/{callrequest-id}/",
                        "description": _("Update callrequest"),
                        "parameters": [{
                                           "name": "request_uuid",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "2342jtdsf-00123"
                                       },
                                       {
                                           "name": "call_time",
                                           "type": "string",
                                           "default": "2011-10-20 12:21:22"
                                       },
                                       {
                                           "name": "phone_number",
                                           "type": "string",
                                           "default": "8792749823"
                                       },
                                       {
                                           "name": "content_type",
                                           "type": "string",
                                           "default": "voiceapp_template"
                                       },
                                       {
                                           "name": "object_id",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       {
                                           "name": "timeout",
                                           "type": "string",
                                           "default": "2000"
                                       },
                                       {
                                           "name": "callerid",
                                           "type": "string",
                                           "default": "650784355"
                                       },
                                       {
                                           "name": "call_type",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       ]
                    }
                ]
            },
        ]
    }
