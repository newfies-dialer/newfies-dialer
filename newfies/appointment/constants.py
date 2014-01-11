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


class EVENT_STATUS(Choice):
    PENDING = 1, _('pending').upper()
    COMPLETED = 2, _('completed').upper()
    PAUSED = 3, _('paused').upper()


class ALARM_STATUS(Choice):
    PENDING = 1, _('pending').upper()
    IN_PROCESS = 2, _('in_process').upper()
    FAILURE = 3, _("failure").upper()
    RETRY = 4, _('retry').upper()
    SUCCESS = 5, _('success').upper()


class ALARM_RESULT(Choice):
    NORESULT = 0, _('no result').upper()
    CONFIRMED = 1, _('confirmed').upper()
    CANCELLED = 2, _('cancelled').upper()
    RESCHEDULED = 3, _('rescheduled').upper()


class ALARM_METHOD(Choice):
    CALL = 1, _('call').upper()
    SMS = 2, _('sms').upper()
    EMAIL = 3, _('email').upper()


class ALARMREQUEST_STATUS(Choice):
    PENDING = 1, _("pending").upper()
    IN_PROCESS = 2, _("in_process").upper()
    FAILURE = 3, _("failure").upper()
    RETRY = 4, _("retry").upper()
    SUCCESS = 5, _("success").upper()


class CALENDAR_SETTING_COLUMN_NAME(Choice):
    label = _('label')
    callerid = _('caller ID Number')
    caller_name = _('caller ID Name')
    call_timeout = _('call Timeout')
    survey = _('survey')
    aleg_gateway = _('A-leg Gateway')
    sms_gateway = _('SMS Gateway')


class CALENDAR_USER_COLUMN_NAME(Choice):
    name = _('name')
    email = _('email')
    calendar_setting = _('Calendar Setting')
    date = _('date')


class CALENDAR_COLUMN_NAME(Choice):
    name = _('name')
    user = _('calendar user')
    max_concurrent = _('max concurrent')
    created_date = _('date')


class EVENT_COLUMN_NAME(Choice):
    start = _('start')
    end = _('end')
    title = _('title')
    end_recurring_period = _('end period')
    calendar = _('calendar')
    status = _('status')
    created_on = _('date')


class ALARM_COLUMN_NAME(Choice):
    alarm_phonenumber = _('phone number')
    alarm_email = _('email')
    daily_start = _('daily start')
    daily_stop = _('daily stop')
    method = _('method')
    survey = _('survey')
    event = _('event')
    date_start_notice = _('start notice')
    status = _('status')
