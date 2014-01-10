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
from dialer_cdr.constants import LEG_TYPE, VOIPCALL_AMD_STATUS


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
    if not value:
        return ''
    TYPE = dict(LEG_TYPE)
    try:
        status = TYPE[value]
    except:
        status = ''

    return unicode(status)


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
    if not value:
        return ''
    TYPE = dict(VOIPCALL_AMD_STATUS)
    try:
        status = TYPE[value]
    except:
        status = ''

    return unicode(status)
