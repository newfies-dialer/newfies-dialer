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

from django.utils.translation import ugettext as _
from common.utils import Choice


class SMS_CAMPAIGN_STATUS(Choice):
    START = 1, 'START'
    PAUSE = 2, 'PAUSE'
    ABORT = 3, 'ABORT'
    END = 4, 'END'


class SMS_SUBSCRIBER_STATUS(Choice):
    PENDING = 1, _('pending').upper()
    PAUSE = 2, _('pause').upper()
    ABORT = 3, _('abort').upper()
    FAIL = 4, _('fail').upper()
    COMPLETE = 5, _('complete').upper()
    IN_PROCESS = 6, _('in process').upper()
    NOT_AUTHORIZED = 7, _('not authorized').upper()


class SMS_CAMPAIGN_COLUMN_NAME(Choice):
    key = _('key').title()
    name = _('name').title()
    start_date = _('start date').title()
    sms_gateway = _('SMS Gateway')
    totalcontact = _('total contact').title()
    status = _('status').title()
    action = _('action').title()

SMS_CAMPAIGN_STATUS_COLOR = {1: "green", 2: "blue", 3: "orange", 4: "red"}


class SMS_NOTIFICATION_NAME(Choice):
    sms_campaign_started = 9, _('SMS campaign started')
    sms_campaign_paused = 10, _('SMS campaign paused')
    sms_campaign_aborted = 11, _('SMS campaign aborted')
    sms_campaign_stopped = 12, _('SMS campaign stopped')
    sms_campaign_limit_reached = 13, _('SMS campaign limit reached')
    sms_contact_limit_reached = 14, _('SMS contact limit reached')
    sms_dialer_setting_configuration = 15, _('SMS dialer setting configuration')


class SMS_REPORT_COLUMN_NAME(Choice):
    send_date = _('send date').title()
    recipient_number = _('recipient').title()
    uuid = _('UUID')
    status = _('status').title()
    status_msg = _('status msg').title()
    gateway = _('gateway').title()


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
