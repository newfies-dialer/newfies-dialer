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


class BulkContactAPIPlayground(APIPlayground):

    schema = {
        "title": _("Bulk contact API Playground"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/bulkcontact/",
                "description": _("This resource allows you to create bulk contacts."),
                "endpoints": [
                    {
                        "method": "POST",
                        "url": "/api/v1/phonebook/",
                        "description": _("Creates new phonebook"),
                        "parameters": [{
                                           "name": "phonebook_id",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "phoneno_list",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "9898988776,9898669912",
                                       }]
                    }
                ]
            },
        ]
    }
