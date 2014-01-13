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


class SEARCH_TYPE(Choice):
    A_Last_30_days = 1, _('last 30 days').capitalize()
    B_Last_7_days = 2, _('last 7 days').capitalize()
    C_Yesterday = 3, _('yesterday').capitalize()
    D_Last_24_hours = 4, _('last 24 hours').capitalize()
    E_Last_12_hours = 5, _('last 12 hours').capitalize()
    F_Last_6_hours = 6, _('last 6 hours').capitalize()
    G_Last_hour = 7, _('last hour').capitalize()


# Disposition color
COLOR_DISPOSITION = {
    'ANSWER': '#42CD2C',
    'NOANSWER': '#0A9289',
    'BUSY': '#4DBCE9',
    'CANCEL': '#E08022',
    'CONGESTION': '#AF0415',
    'FAILED': '#DE2213'
}
