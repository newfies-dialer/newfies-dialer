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


class HangupCallAPIPlayground(APIPlayground):

    schema = {
        "title": _("Hangup Call API Playground"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/hangupcall/",
                "description": _("This resource allows you to manage hangup call."),
                "endpoints": [
                    {
                        "method": "POST",
                        "url": "/api/v1/hangupcall/",
                        "description": _("hangup call"),
                        "parameters": [{
                                           "name": "RequestUUID",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "e4fc2188-0af5-11e1-b64d-00231470a30c"
                                       },
                                       {
                                           "name": "HangupCause",
                                           "type": "string",
                                           "default": "SUBSCRIBER_ABSENT"
                                       },
                                       {
                                           "name": "From",
                                           "type": "string",
                                           "default": "800124545"
                                       },
                                       {
                                           "name": "To",
                                           "type": "string",
                                           "default": "34650111222"
                                       },
                                       ]
                    }
                ]
            },
        ]
    }
