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

from dialer_campaign.models import Campaign
from dialer_campaign.constants import CAMPAIGN_STATUS
from survey2.models import Survey_template, Survey, Section_template, Section, \
    Branching_template, Branching


def check_survey_campaign(request, pk):
    """Running Survey Campaign"""
    obj_campaign = Campaign.objects.get(id=pk,
                                        status=CAMPAIGN_STATUS.START,
                                        content_type__model='survey')
    if obj_campaign:
        # Copy survey
        obj = Survey.objects.create(user=request.user, campaign=obj_campaign)
        print obj
        # Copy Section
        # Copy Branching
    return True
