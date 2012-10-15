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
from django.conf.urls import include, patterns
from api.api_playgrounds.phonebook_playground import PhonebookAPIPlayground
from api.api_playgrounds.campaign_playground import CampaignAPIPlayground
from api.api_playgrounds.callrequest_playground import CallrequestAPIPlayground
from api.api_playgrounds.voiceapp_playground import VoiceAppAPIPlayground
from api.api_playgrounds.bulk_contact_playground import BulkContactAPIPlayground


urlpatterns = patterns('',

    (r'phonebook-api/', include(PhonebookAPIPlayground().urls)),
    (r'campaign-api/', include(CampaignAPIPlayground().urls)),
    (r'callrequest-api/', include(CallrequestAPIPlayground().urls)),
    (r'voiceapp-api/', include(VoiceAppAPIPlayground().urls)),
    (r'bulk-contact-api/', include(BulkContactAPIPlayground().urls)),
)
