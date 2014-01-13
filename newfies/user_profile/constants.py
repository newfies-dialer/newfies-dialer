#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.utils.translation import ugettext_lazy as _
from common.utils import Choice


class NOTIFICATION_NAME(Choice):
    campaign_started = 1, _('campaign started')
    campaign_paused = 2, _('campaign paused')
    campaign_aborted = 3, _('campaign aborted')
    campaign_stopped = 4, _('campaign stopped')
    campaign_limit_reached = 5, _('campaign limit reached')
    contact_limit_reached = 6, _('contact limit reached')
    dialer_setting_configuration = 7, _('dialer setting configuration')
    callrequest_not_found = 8, _('callrequest not found')
