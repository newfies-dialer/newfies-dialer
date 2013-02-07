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


class AnswerCallAPIPlayground(APIPlayground):

    schema = {
        "title": _("Answer Call API Playground"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/answercall/",
                "description": _("This resource allows you to manage answer call."),
                "endpoints": [
                    {
                        "method": "POST",
                        "url": "/api/v1/answercall/",
                        "description": _("hangup call"),
                        "parameters": [{
                                           "name": "ALegRequestUUID",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "48092924-856d-11e0-a586-0147ddac9d3e"
                                       },
                                       {
                                           "name": "CallUUID",
                                           "type": "string",
                                           "default": "48092924-856d-11e0-a586-0147ddac9d3e"
                                       },
                                      ]
                    }
                ]
            },
        ]
    }
