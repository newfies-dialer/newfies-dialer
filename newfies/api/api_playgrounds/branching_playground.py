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
from apiplayground import APIPlayground


class BranchingAPIPlayground(APIPlayground):

    schema = {
        "title": "Branching API Playground",
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/branching/",
                "description": "This resource allows you to manage branching.",
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/branching/",
                        "description": "Returns all branching"
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/branching/{branching-id}/",
                        "description": "Returns a specific branching"
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/branching/",
                        "description": "Creates new branching",
                        "parameters": [{
                                           "name": "keys",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "section",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       ]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/branching/{branching-id}/",
                        "description": "Update branching",
                        "parameters": [{
                                           "name": "keys",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "section",
                                           "type": "string",
                                           "default": "1"
                                       },
                                      ]
                    },
                    {
                        "method": "DELETE",
                        "url": "/api/v1/branching/{branching-id}/",
                        "description": "Delete branching",
                        }
                ]
            },
            ]
    }
