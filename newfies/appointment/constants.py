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
    PENDING = 1, _('pending').upper()
    COMPLETED = 2, _('completed').upper()


class ALARM_STATUS(Choice):
    PENDING = 1, _('pending').upper()
    IN_PROCESS = 2, _('in_process').upper()
    COMPLETED = 3, _('completed').upper()


class ALARM_RESULT(Choice):
    CONFIRMED = 1, _('confirmed').upper()
    CANCELLED = 2, _('cancelled').upper()
    RESCHEDULED = 3, _('rescheduled').upper()


class ALARM_METHOD(Choice):
    CALL = 1, _('call').upper()
    SMS = 2, _('sms').upper()
    EMAIL = 3, _('email').upper()
