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

from django.utils.translation import ugettext_lazy as _
from common.utils import Choice


class NOTIFICATION_NAME(Choice):
    campaign_started = 1, u'campaign_started'
    campaign_paused = 2, u'campaign_paused'
    campaign_aborted = 3, u'campaign_aborted'
    campaign_stopped = 4, u'campaign_stopped'
    campaign_limit_reached = 5, u'campaign_limit_reached'
    contact_limit_reached = 6, u'contact_limit_reached'
    dialer_setting_configuration = 7, u'dialer_setting_configuration'
    callrequest_not_found = 8, u'callrequest_not_found'
