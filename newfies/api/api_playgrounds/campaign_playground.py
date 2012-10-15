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


class CampaignAPIPlayground(APIPlayground):

    schema = {
        "title": "Campaign API Playground",
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/campaign/",
                "description": "This resource allows you to manage campaign.",
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/campaign/",
                        "description": "Returns all campaigns"
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/campaign/{campaign-id}/",
                        "description": "Returns a specific campaign"
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/campaign/",
                        "description": "Creates new campaign",
                        "parameters": [{
                                           "name": "name",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "Sample Campaign"
                                       },
                                       {
                                           "name": "description",
                                           "type": "string"
                                       },
                                       {
                                           "name": "callerid",
                                           "type": "string"
                                       },
                                       {
                                           "name": "startingdate",
                                           "type": "string",
                                           "default": "1301392136.0"
                                       },
                                       {
                                           "name": "expirationdate",
                                           "type": "string",
                                           "default": "1301332136.0"
                                       },
                                       {
                                           "name": "frequency",
                                           "type": "string",
                                           "default": "20"
                                       },
                                       {
                                           "name": "callmaxduration",
                                           "type": "string",
                                           "default": "50"
                                       },
                                       {
                                           "name": "maxretry",
                                           "type": "string",
                                           "default": "3"
                                       },
                                       {
                                           "name": "intervalretry",
                                           "type": "string",
                                           "default": "3000"
                                       },
                                       {
                                           "name": "calltimeout",
                                           "type": "string",
                                           "default": "45"
                                       },
                                       {
                                           "name": "aleg_gateway",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       {
                                           "name": "content_type",
                                           "type": "string",
                                           "default": "voiceapp_template"
                                       },
                                       {
                                           "name": "object_id",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       {
                                           "name": "extra_data",
                                           "type": "string",
                                           "default": "2000"
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
                        "url": "/api/v1/campaign/{campaign-id}/",
                        "description": "Update campaign",
                        "parameters": [{
                                           "name": "name",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "Sample Campaign"
                                       },
                                       {
                                           "name": "description",
                                           "type": "string"
                                       },
                                       {
                                           "name": "callerid",
                                           "type": "string"
                                       },
                                       {
                                           "name": "startingdate",
                                           "type": "string",
                                           "default": "1301392136.0"
                                       },
                                       {
                                           "name": "expirationdate",
                                           "type": "string",
                                           "default": "1301332136.0"
                                       },
                                       {
                                           "name": "frequency",
                                           "type": "string",
                                           "default": "20"
                                       },
                                       {
                                           "name": "callmaxduration",
                                           "type": "string",
                                           "default": "50"
                                       },
                                       {
                                           "name": "maxretry",
                                           "type": "string",
                                           "default": "3"
                                       },
                                       {
                                           "name": "intervalretry",
                                           "type": "string",
                                           "default": "3000"
                                       },
                                       {
                                           "name": "calltimeout",
                                           "type": "string",
                                           "default": "45"
                                       },
                                       {
                                           "name": "aleg_gateway",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       {
                                           "name": "content_type",
                                           "type": "string",
                                           "default": "voiceapp_template"
                                       },
                                       {
                                           "name": "object_id",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       {
                                           "name": "extra_data",
                                           "type": "string",
                                           "default": "2000"
                                       },
                                       {
                                           "name": "phonebook_id",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       ]
                    },
                    {
                        "method": "DELETE",
                        "url": "/api/v1/campaign/{campaign-id}/",
                        "description": "Delete campaign",
                    }
                ]
            },
        ]
    }
