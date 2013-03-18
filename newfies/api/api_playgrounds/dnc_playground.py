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
from django.utils.translation import gettext as _
from apiplayground import APIPlayground


class DNCAPIPlayground(APIPlayground):

    schema = {
        "title": _("dnc"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/dnc/",
                "description": _("this resource allows you to manage DNC list."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/dnc/",
                        "description": _("returns all dncs")
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/dnc/{dnc-id}/",
                        "description": _("returns a specific dnc")
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/dnc/",
                        "description": _("create new dnc"),
                        "parameters": [{
                                           "name": "name",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "Sample DNC"
                                       },]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/dnc/{dnc-id}/",
                        "description": _("update dnc"),
                        "parameters": [{
                                           "name": "name",
                                           "type": "string"
                                       }]
                    },
                    {
                        "method": "DELETE",
                        "url": "/api/v1/dnc/{dnc-id}/",
                        "description": _("delete dnc"),
                    }
                ]
            },
        ]
    }
