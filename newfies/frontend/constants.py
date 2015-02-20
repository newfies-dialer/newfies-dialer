#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.utils.translation import ugettext_lazy as _
from django_lets_go.utils import Choice


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
    'ANSWER': '#42CD2C',
    'NOANSWER': '#0A9289',
    'BUSY': '#4DBCE9',
    'CANCEL': '#E08022',
    'CONGESTION': '#AF0415',
    'FAILED': '#DE2213'
}
