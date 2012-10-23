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


class SubscriberAPIPlayground(APIPlayground):

    schema = {
        "title": "Campaign API Playground",
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/subscriber/",
                "description": "This resource allows you to manage campaign subscriber.",
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/subscriber/",
                        "description": "Returns all campaign subscribers"
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/subscriber/",
                        "description": "Creates new campaign subscriber",
                        "parameters": [{
                                           "name": "contact",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "650784355"
                                       },
                                       {
                                           "name": "last_name",
                                           "type": "string",
                                           "default": "belaid"
                                       },
                                       {
                                           "name": "first_name",
                                           "type": "string",
                                           "default": "areski"
                                       },
                                       {
                                           "name": "email",
                                           "type": "string",
                                           "default": "areski@gmail.com"
                                       },
                                       {
                                           "name": "phonebook_id",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       ]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/subscriber/{campaign-id}/",
                        "description": "Update campaign subscriber",
                        "parameters": [{
                                           "name": "contact",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "650784355"
                                       },
                                       {
                                           "name": "last_name",
                                           "type": "string",
                                           "default": "belaid"
                                       },
                                       {
                                           "name": "first_name",
                                           "type": "string",
                                           "default": "areski"
                                       },
                                       {
                                           "name": "email",
                                           "type": "string",
                                           "default": "areski@gmail.com"
                                       },
                                       {
                                           "name": "phonebook_id",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       ]
                    }
                ]
            },
        ]
    }
