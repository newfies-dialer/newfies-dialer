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


class SubscriberPerCampaignAPIPlayground(APIPlayground):

    schema = {
        "title": "Campaign API Playground",
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/subscriber_per_campaign/",
                "description": "This resource allows you to manage campaign subscriber per campaign.",
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/subscriber_per_campaign/{campaign-id}/",
                        "description": "Returns campaign subscribers per campaign"
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/subscriber_per_campaign/{campaign-id}/{contact}/",
                        "description": "Returns specific campaign subscribers per campaign"
                    },
                ]
            },
        ]
    }
