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


class StoreCdrAPIPlayground(APIPlayground):

    schema = {
        "title": _("store cdr"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/store_cdr/",
                "description": _("this resource allows you to manage store cdr."),
                "endpoints": [
                    {
                        "method": "POST",
                        "url": "/api/v1/store_cdr/",
                        "description": _("Store cdr"),
                        "parameters": [{
                                           "name": "cdr",
                                           "type": "string",
                                           "is_required": True,
                                           "default": '<?xml version="1.0"?><cdr><other></other><variables><plivo_request_uuid>af41ac8a-ede4-11e0-9cca-00231470a30c</plivo_request_uuid><duration>3</duration></variables><notvariables><plivo_request_uuid>TESTc</plivo_request_uuid><duration>5</duration></notvariables></cdr>'
                                       }]
                    }
                ]
            },
        ]
    }
