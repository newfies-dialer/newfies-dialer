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


class DialCallbackAPIPlayground(APIPlayground):

    schema = {
        "title": _("Dial Callback API Playground"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/dialcallback/",
                "description": _("This resource allows you to manage dial callback."),
                "endpoints": [
                    {
                        "method": "POST",
                        "url": "/api/v1/dialcallback/",
                        "description": _("Creates new campaign subscriber"),
                        "parameters": [{
                                           "name": "DialALegUUID",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "e4fc2188-0af5-11e1-b64d-00231470a30c"
                                       },
                                       {
                                           "name": "DialBLegUUID",
                                           "type": "string",
                                           "default": "e4fc2188-0af5-11e1-b64d-00231470a30c"
                                       },
                                       {
                                           "name": "DialBLegHangupCause",
                                           "type": "string",
                                           "default": "SUBSCRIBER_ABSENT"
                                       }
                                       ]
                    }
                ]
            },
        ]
    }
