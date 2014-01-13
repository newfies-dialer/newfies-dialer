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

from django.template.defaultfilters import register
from callcenter.constants import STRATEGY


@register.filter(name='strategy_name')
def strategy_name(value):
    """strategy name"""
    if not value:
        return ''
    STATUS = dict(STRATEGY)
    try:
        status = STATUS[value].encode('utf-8')
    except:
        status = ''

    return str(status)
