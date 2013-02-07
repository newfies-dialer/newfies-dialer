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


class CampaignDelCascadeAPIPlayground(APIPlayground):

    schema = {
        "title": _("Campaign Delete Cascade API Playground"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/campaign_delete_cascade/",
                "description": _("This resource allows you to delete campaign."),
                "endpoints": [
                    {
                        "method": "DELETE",
                        "url": "/api/v1/campaign_delete_cascade/{campaign-id}/",
                        "description": _("Delete campaign"),
                    }
                ]
            },
        ]
    }
