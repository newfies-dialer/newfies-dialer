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


class DNCContactAPIPlayground(APIPlayground):

    schema = {
        "title": _("dnc contact"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/dnc_contact/",
                "description": _("this resource allows you to manage DNC contacts."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/dnc_contact/",
                        "description": _("returns all dnc contacts")
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/dnc_contact/{dnc-contact-id}/",
                        "description": _("returns a specific dnc contact")
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/dnc_contact/",
                        "description": _("create new dnc contact"),
                        "parameters": [{
                                           "name": "phone_number",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "123456"
                                       },
                                       {
                                           "name": "dnc",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "/api/v1/dnc/1/"
                                       },]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/dnc_contact/{dnc-contact-id}/",
                        "description": _("update dnc contact"),
                        "parameters": [{
                                           "name": "phone_number",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "123456"
                                       },
                                       {
                                           "name": "dnc",
                                           "type": "string",
                                           "is_required": False,
                                           "default": "/api/v1/dnc/1/"
                                       }]
                    },
                    {
                        "method": "DELETE",
                        "url": "/api/v1/dnc_contact/{dnc-contact-id}/",
                        "description": _("delete dnc contact"),
                    }
                ]
            },
        ]
    }
