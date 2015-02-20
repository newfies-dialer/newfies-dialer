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

from django.template.defaultfilters import register


@register.filter(name='contact_status')
def contact_status(value):
    """Contact status

    >>> contact_status(1)
    'ACTIVE'

    >>> contact_status(2)
    'INACTIVE'
    """
    return str('ACTIVE') if value == 1 else str('INACTIVE')
