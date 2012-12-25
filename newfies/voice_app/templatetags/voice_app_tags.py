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

from django.template.defaultfilters import register
from voice_app.constants import VOICEAPP_TYPE


@register.filter(name='voiceapp_type')
def voiceapp_type(value):
    """
    >>> voiceapp_type(1)
    'DIAL'
    """
    if not value:
        return ''
    TYPE = dict(VOICEAPP_TYPE)
    try:
        status = TYPE[value]
    except:
        status = ''

    return str(status)
