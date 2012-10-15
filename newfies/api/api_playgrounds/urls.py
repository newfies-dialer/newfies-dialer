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
from api.api_playgrounds.campaign_delete_cascade_playground import CampaignDelCascadeAPIPlayground
from api.api_playgrounds.campaign_subscriber_playground import CampaignSubscriberAPIPlayground


urlpatterns = patterns('',
    (r'explorer/phonebook/', include(PhonebookAPIPlayground().urls)),
    (r'explorer/campaign/', include(CampaignAPIPlayground().urls)),
    (r'explorer/callrequest/', include(CallrequestAPIPlayground().urls)),
    (r'explorer/voiceapp/', include(VoiceAppAPIPlayground().urls)),
    (r'explorer/bulk-contact/', include(BulkContactAPIPlayground().urls)),
    (r'explorer/campaign-delete-cascade/', include(CampaignDelCascadeAPIPlayground().urls)),
    (r'explorer/campaign-subscriber/', include(CampaignSubscriberAPIPlayground().urls)),
)
