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
from voice_app.models import VoiceApp_template


def check_voiceapp_campaign(request, pk):
    """Running Voice app Campaign"""
    try:
        obj_campaign = Campaign.objects.get(id=pk,
                                            status=CAMPAIGN_STATUS.START,
                                            content_type__model='voiceapp_template')
        if obj_campaign:
            # Copy voiceapp
            voiceapp_template = VoiceApp_template.objects.filter(user=request.user)
            for voiceapp_temp in voiceapp_template:
                voiceapp_temp.copy_voiceapp_template(obj_campaign)
    except:
        pass

    return True
