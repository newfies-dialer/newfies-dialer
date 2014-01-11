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


class GATEWAY_STATUS(Choice):
    ACTIVE = 1, _('active').upper()
    INACTIVE = 0, _('inactive').upper()


class GATEWAY_PROTOCOL(Choice):
    SIP = 'SIP', _('SIP')
    LOCAL = 'LOCAL', _('LOCAL')
    GSM = 'GSM', _('GSM')
    SKINNY = 'SKINNY', _('SKINNY')
    JINGLE = 'JINGLE', _('JINGLE')
