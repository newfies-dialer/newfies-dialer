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


class ResultAggregateResourceAPIPlayground(APIPlayground):

    schema = {
        "title": "Survey Aggregate Result API Playground",
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/survey_aggregate_result/",
                "description": "This resource allows you to get survey aggregate result.",
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/survey_aggregate_result/{campaign-id}/",
                        "description": "Returns a result belong to campaign"
                    }
                ]
            }
        ]
    }
