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


class PhonebookAPIPlayground(APIPlayground):

    schema = {
        "title": _("phonebook"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/phonebook/",
                "description": _("this resource allows you to manage phonebooks."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/phonebook/",
                        "description": _("returns all phonebooks")
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/phonebook/{phonebook-id}/",
                        "description": _("returns a specific phonebook")
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/phonebook/",
                        "description": _("create new phonebook"),
                        "parameters": [
                            {
                                "name": "name",
                                "type": "string",
                                "is_required": True,
                                "default": "Sample Phonebook"
                            },
                            {
                                "name": "description",
                                "type": "string"
                            }
                        ]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/phonebook/{phonebook-id}/",
                        "description": _("update phonebook"),
                        "parameters": [
                            {
                                "name": "name",
                                "type": "string"
                            },
                            {
                                "name": "description",
                                "type": "string"
                            }
                        ]
                    },
                    {
                        "method": "DELETE",
                        "url": "/api/v1/phonebook/{phonebook-id}/",
                        "description": _("delete phonebook"),
                    }
                ]
            },
        ]
    }
