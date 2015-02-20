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

from django.utils.translation import ugettext_lazy as _
from django_lets_go.utils import Choice


class EVENT_STATUS(Choice):
    PENDING = 1, _('PENDING')
    COMPLETED = 2, _('COMPLETED')
    PAUSED = 3, _('PAUSED')


class ALARM_STATUS(Choice):
    PENDING = 1, _('PENDING')
    IN_PROCESS = 2, _('IN_PROCESS')
    FAILURE = 3, _("FAILURE")
    RETRY = 4, _('RETRY')
    SUCCESS = 5, _('SUCCESS')


class ALARM_RESULT(Choice):
    NORESULT = 0, _('NO RESULT')
    CONFIRMED = 1, _('CONFIRMED')
    CANCELLED = 2, _('CANCELLED')
    RESCHEDULED = 3, _('RESCHEDULED')


class ALARM_METHOD(Choice):
    CALL = 1, _('CALL')
    SMS = 2, _('SMS')
    EMAIL = 3, _('EMAIL')


class ALARMREQUEST_STATUS(Choice):
    PENDING = 1, _("PENDING")
    IN_PROCESS = 2, _("IN PROCESS")
    FAILURE = 3, _("FAILURE")
    RETRY = 4, _("RETRY")
    SUCCESS = 5, _("SUCCESS")


CALENDAR_SETTING_COLUMN_NAME = {
    'label': _('label'),
    'callerid': _('caller ID Number'),
    'caller_name': _('caller ID Name'),
    'call_timeout': _('call Timeout'),
    'survey': _('survey'),
    'aleg_gateway': _('A-leg Gateway'),
    'sms_gateway': _('SMS Gateway')
}

CALENDAR_USER_COLUMN_NAME = {
    'name': _('name'),
    'email': _('email'),
    'calendar_setting': _('Calendar Setting'),
    'date': _('date')
}

CALENDAR_COLUMN_NAME = {
    'name': _('name'),
    'user': _('calendar user'),
    'max_concurrent': _('max concurrent'),
    'created_date': _('date')
}

EVENT_COLUMN_NAME = {
    'start': _('start'),
    'end': _('end'),
    'title': _('title'),
    'end_recurring_period': _('end period'),
    'calendar': _('calendar'),
    'status': _('status'),
    'created_on': _('date')
}

ALARM_COLUMN_NAME = {
    'alarm_phonenumber': _('phone number'),
    'alarm_email': _('email'),
    'daily_start': _('daily start'),
    'daily_stop': _('daily stop'),
    'method': _('method'),
    'survey': _('survey'),
    'event': _('event'),
    'date_start_notice': _('start notice'),
    'status': _('status')
}
