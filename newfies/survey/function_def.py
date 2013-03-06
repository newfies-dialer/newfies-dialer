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

from dialer_campaign.models import Campaign
from survey.models import Survey_template


def copy_survey_template_campaign(user, pk):
    """
    Start Survey Campaign
    """
    obj_campaign = Campaign.objects.get(id=pk)
    if obj_campaign:
        # Copy survey
        survey_template = Survey_template.objects.get(user=user, pk=obj_campaign.object_id)
        survey_template.copy_survey_template(obj_campaign.id)

    return True
