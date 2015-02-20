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
from dialer_cdr.constants import LEG_TYPE, VOIPCALL_AMD_STATUS
from mod_utils.function_def import get_status_value


@register.filter(name='leg_type_name')
def leg_type_name(value):
    """leg type

    >>> leg_type_name(1)
    u'A-Leg'

    >>> leg_type_name(2)
    u'B-Leg'

    >>> leg_type_name(0)
    ''
    """
    return get_status_value(value, LEG_TYPE)


@register.filter(name='amd_status_name')
def amd_status_name(value):
    """amd status name

    >>> amd_status_name(1)
    u'Person'

    >>> amd_status_name(2)
    u'Machine'

    >>> amd_status_name(0)
    ''
    """
    return get_status_value(value, VOIPCALL_AMD_STATUS)
