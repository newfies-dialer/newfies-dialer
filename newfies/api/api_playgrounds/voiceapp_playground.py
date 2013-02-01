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


class VoiceAppAPIPlayground(APIPlayground):

    schema = {
        "title": _("VoiceApp API Playground"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/voiceapp/",
                "description": _("This resource allows you to manage voiceapps."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/voiceapp/",
                        "description": _("Returns all voiceapps")
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/voiceapp/{voiceapp-id}/",
                        "description": _("Returns a specific voiceapp")
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/voiceapp/",
                        "description": _("Creates new voiceapp"),
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
                        "description": _("Update voiceapp"),
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
                        "description": _("Delete voiceapp"),
                    }
                ]
            },
        ]
    }
