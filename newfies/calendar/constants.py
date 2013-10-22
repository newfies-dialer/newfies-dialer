#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.utils.translation import ugettext_lazy as _
from common.utils import Choice


class EVENT_STATUS(Choice):
    PENDING = 1, _('PENDING')
    COMPLETED = 2, _('COMPLETED')


class ALARM_STATUS(Choice):
    PENDING = 1, _('PENDING')
    IN_PROCESS = 2, _('IN_PROCESS')
    COMPLETED = 3, _('COMPLETED')


class ALARM_RESULT(Choice):
    CONFIRMED = 1, _('CONFIRMED')
    CANCELLED = 2, _('CANCELLED')
    RESCHEDULED = 3, _('RESCHEDULED')


class ALARM_METHOD(Choice):
    CALL = 1, _('CALL')
    SMS = 2, _('SMS')
    EMAIL = 3, _('EMAIL')
