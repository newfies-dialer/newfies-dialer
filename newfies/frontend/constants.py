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


class SEARCH_TYPE(Choice):
    A_Last_30_days = 1, _('Last 30 days')
    B_Last_7_days = 2, _('Last 7 days')
    C_Yesterday = 3, _('Yesterday')
    D_Last_24_hours = 4, _('Last 24 hours')
    E_Last_12_hours = 5, _('Last 12 hours')
    F_Last_6_hours = 6, _('Last 6 hours')
    G_Last_hour = 7, _('Last hour')


# Disposition color
COLOR_DISPOSITION = {
    'ANSWER': '#8BEA00',
    'BUSY' : '#F40C27',
    'NOANSWER' : '#F40CD5',
    'CANCEL' : '#3216B0',
    'CONGESTION' : '#F9AA26',
    'CHANUNAVAIL' : '#7E8179',
    'DONTCALL' : '#5DD0C0',
    'TORTURE' : '#FFCE00',
    'INVALIDARGS' : '#9B5C00',
    'NOROUTE' : '#057D9F',
    'FORBIDDEN' : '#A61700'
}
