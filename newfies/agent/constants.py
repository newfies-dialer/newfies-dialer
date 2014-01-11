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


class AGENT_COLUMN_NAME(Choice):
    name = _('name')
    contact = _('contact')
    status = _('status')
    date = _('date')


class AGENT_STATUS(Choice):
    LOGGED_OUT = 1, 'logged out'
    AVAILABLE = 2, 'available'
    ON_DEMAND = 3, 'available (on demand)'
    ON_BREAK = 4, 'on break'


class AGENT_TYPE(Choice):
    CALLBACK = 1, 'callback'
    UUID_STANDBY = 2, 'uuid-standby'
