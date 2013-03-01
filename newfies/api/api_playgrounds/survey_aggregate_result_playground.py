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


class ResultAggregateResourceAPIPlayground(APIPlayground):

    schema = {
        "title": _("survey aggregate result"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/survey_aggregate_result/",
                "description": _("this resource allows you to get survey aggregate result."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/survey_aggregate_result/{campaign-id}/",
                        "description": _("returns a result belong to campaign")
                    }
                ]
            }
        ]
    }
