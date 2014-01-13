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

from django.utils.timezone import utc
from frontend.forms import SEARCH_TYPE
from dateutil.relativedelta import relativedelta
from datetime import datetime


def calculate_date(search_type):
    """calculate date"""
    end_date = datetime.today().replace(tzinfo=utc)
    search_type = int(search_type)

    # Last 30 days
    if search_type == SEARCH_TYPE.A_Last_30_days:
        start_date = end_date + relativedelta(days=-int(30))

    # Last 7 days
    if search_type == SEARCH_TYPE.B_Last_7_days:
        start_date = end_date + relativedelta(days=-int(7))

    # Yesterday
    if search_type == SEARCH_TYPE.C_Yesterday:
        start_date = end_date + relativedelta(days=-int(1),
            hour=0, minute=0, second=0)

    # Last 24 hours
    if search_type == SEARCH_TYPE.D_Last_24_hours:
        start_date = end_date + relativedelta(hours=-int(24))

    # Last 12 hours
    if search_type == SEARCH_TYPE.E_Last_12_hours:
        start_date = end_date + relativedelta(hours=-int(12))

    # Last 6 hours
    if search_type == SEARCH_TYPE.F_Last_6_hours:
        start_date = end_date + relativedelta(hours=-int(6))

    # Last hour
    if search_type == SEARCH_TYPE.G_Last_hour:
        start_date = end_date + relativedelta(hours=-int(1))

    return start_date.replace(tzinfo=utc)
