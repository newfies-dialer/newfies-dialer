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
    ERROR = 3, _('error').upper()


class ALARM_RESULT(Choice):
    CONFIRMED = 1, _('confirmed').upper()
    CANCELLED = 2, _('cancelled').upper()
    RESCHEDULED = 3, _('rescheduled').upper()


class ALARM_METHOD(Choice):
    CALL = 1, _('call').upper()
    SMS = 2, _('sms').upper()
    EMAIL = 3, _('email').upper()


class ALARMREQUEST_STATUS(Choice):
    PENDING = 1, _("pending").capitalize()
    IN_PROCESS = 2, _("in_process").capitalize()
    FAILURE = 3, _("failure").capitalize()
    RETRY = 4, _("retry").capitalize()
    SUCCESS = 5, _("success").capitalize()


class CALENDAR_USER_COLUMN_NAME(Choice):
    name = _('name')
    email = _('email')
    calendar_setting = _('calendar setting')
    date = _('date')


class CALENDAR_COLUMN_NAME(Choice):
    name = _('name')
    slug = _('slug')
    user = _('calendar user')
    max_concurrent = _('max_concurrent')
    created_date = _('date')


class EVENT_COLUMN_NAME(Choice):
    start = _('start')
    end = _('end')
    title = _('title')
    end_recurring_period = _('end period')
    calendar = _('calendar')
    status = _('status')
    created_on = _('date')
