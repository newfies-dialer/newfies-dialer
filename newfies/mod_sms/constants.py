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
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.utils.translation import ugettext_lazy as _
from django_lets_go.utils import Choice


class SMS_CAMPAIGN_STATUS(Choice):
    START = 1, _('START')
    PAUSE = 2, _('PAUSE')
    ABORT = 3, _('ABORT')
    END = 4, _('END')

SMS_CAMPAIGN_STATUS_COLOR = {1: "green", 2: "blue", 3: "orange", 4: "red"}


class SMS_SUBSCRIBER_STATUS(Choice):
    PENDING = 1, _('PENDING')
    PAUSE = 2, _('PAUSE')
    ABORT = 3, _('ABORT')
    FAIL = 4, _('FAIL')
    COMPLETE = 5, _('COMPLETE')
    IN_PROCESS = 6, _('IN process')
    NOT_AUTHORIZED = 7, _('NOT authorized')


SMS_CAMPAIGN_COLUMN_NAME = {
    'key': _('key'),
    'name': _('name'),
    'start_date': _('start date'),
    'sms_gateway': _('SMS Gateway'),
    'totalcontact': _('total contact'),
    'status': _('status'),
    'action': _('action'),
}


class SMS_NOTIFICATION_NAME(Choice):
    sms_campaign_started = 9, _('SMS campaign started')
    sms_campaign_paused = 10, _('SMS campaign paused')
    sms_campaign_aborted = 11, _('SMS campaign aborted')
    sms_campaign_stopped = 12, _('SMS campaign stopped')
    sms_campaign_limit_reached = 13, _('SMS campaign limit reached')
    sms_contact_limit_reached = 14, _('SMS contact limit reached')
    sms_dialer_setting_configuration = 15, _('SMS dialer setting configuration')


SMS_REPORT_COLUMN_NAME = {
    'send_date': _('send date'),
    'recipient_number': _('recipient'),
    'uuid': _('UUID'),
    'status': _('status'),
    'status_msg': _('status msg'),
    'gateway': _('gateway'),
}


class SMS_MESSAGE_STATUS(Choice):
    UNSENT = 'Unsent'
    SENT = 'Sent'
    DELIVERED = 'Delivered'
    FAILED = 'Failed'
    NO_ROUTE = 'No_Route'
    UNAUTHORIZED = 'Unauthorized'


# SMS Disposition color
COLOR_SMS_DISPOSITION = {
    'UNSENT': '#4DBCE9',
    'SENT': '#0A9289',
    'DELIVERED': '#42CD2C',
    'FAILED': '#DE2213',
    'NO_ROUTE': '#AF0415',
    'UNAUTHORIZED': '#E08022'
}
