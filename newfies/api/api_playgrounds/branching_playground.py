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


class BranchingAPIPlayground(APIPlayground):

    schema = {
        "title": _("branching"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/branching/",
                "description": _("this resource allows you to manage branching."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/branching/",
                        "description": _("returns all branching")
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/branching/{branching-id}/",
                        "description": _("returns a specific branching")
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/branching/",
                        "description": _("create new branching"),
                        "parameters": [{
                                           "name": "keys",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "section",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "goto",
                                           "type": "string",
                                           "is_required": False,
                                           "default": "1"
                                       },
                                       ]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/branching/{branching-id}/",
                        "description": _("update branching"),
                        "parameters": [{
                                           "name": "keys",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "section",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "goto",
                                           "type": "string",
                                           "is_required": False,
                                           "default": "1"
                                       },
                                      ]
                    },
                    {
                        "method": "DELETE",
                        "url": "/api/v1/branching/{branching-id}/",
                        "description": _("delete branching"),
                        }
                ]
            },
            ]
    }
