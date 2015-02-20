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

from django.utils.timezone import utc
from frontend.forms import SEARCH_TYPE
from dateutil.relativedelta import relativedelta
from datetime import datetime


def calculate_date(search_type):
    """calculate date"""
    end_date = datetime.utcnow().replace(tzinfo=utc)
    search_type = int(search_type)

    if search_type == SEARCH_TYPE.A_Last_30_days:
        # Last 30 days
        start_date = end_date + relativedelta(days=-30)
    elif search_type == SEARCH_TYPE.B_Last_7_days:
        # Last 7 days
        start_date = end_date + relativedelta(days=-7)
    elif search_type == SEARCH_TYPE.C_Yesterday:
        # Yesterday
        start_date = end_date + relativedelta(days=-1, hour=0, minute=0, second=0)
    elif search_type == SEARCH_TYPE.D_Last_24_hours:
        # Last 24 hours
        start_date = end_date + relativedelta(hours=-24)
    elif search_type == SEARCH_TYPE.E_Last_12_hours:
        # Last 12 hours
        start_date = end_date + relativedelta(hours=-12)
    elif search_type == SEARCH_TYPE.F_Last_6_hours:
        # Last 6 hours
        start_date = end_date + relativedelta(hours=-6)
    elif search_type == SEARCH_TYPE.G_Last_hour:
        # Last hour
        start_date = end_date + relativedelta(hours=-1)

    return start_date.replace(tzinfo=utc)
