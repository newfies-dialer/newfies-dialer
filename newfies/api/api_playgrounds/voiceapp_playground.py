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


class VoiceAppAPIPlayground(APIPlayground):

    schema = {
        "title": _("voice application"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/voiceapp/",
                "description": _("this resource allows you to manage voice applications."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/voiceapp/",
                        "description": _("returns all voice applications.")
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/voiceapp/{voiceapp-id}/",
                        "description": _("returns a specific voice application.")
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/voiceapp/",
                        "description": _("create new voice application."),
                        "parameters": [{
                                           "name": "name",
                                           "type": "string"
                                       },
                                       {
                                           "name": "description",
                                           "type": "string"
                                       }]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/voiceapp/{voiceapp-id}/",
                        "description": _("update voiceapp"),
                        "parameters": [{
                                           "name": "name",
                                           "type": "string"
                                       },
                                       {
                                           "name": "description",
                                           "type": "string"
                                       }]
                    },
                    {
                        "method": "DELETE",
                        "url": "/api/v1/voiceapp/{voiceapp-id}/",
                        "description": _("delete voiceapp"),
                    }
                ]
            },
        ]
    }
