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


class SUBSCRIBER_STATUS(Choice):
    PENDING = 1, _('PENDING')
    PAUSE = 2, _('PAUSE')
    ABORT = 3, _('ABORT')
    FAIL = 4, _('FAIL')
    SENT = 5, _('SENT')
    IN_PROCESS = 6, _('IN PROCESS')
    NOT_AUTHORIZED = 7, _('NOT AUTHORIZED')
    COMPLETED = 8, _('COMPLETED')


class SUBSCRIBER_STATUS_NAME(Choice):
    PENDING = 'PENDING', _('PENDING')
    PAUSE = 'PAUSE', _('PAUSE')
    ABORT = 'ABORT', _('ABORT')
    FAIL = 'FAIL', _('FAIL')
    SENT = 'SENT', _('SENT')
    IN_PROCESS = 'IN_PROCESS', _('IN_PROCESS')
    NOT_AUTHORIZED = 'NOT_AUTHORIZED', _('NOT_AUTHORIZED')
    COMPLETED = 'COMPLETED', _('COMPLETED')


class CAMPAIGN_STATUS(Choice):
    START = 1, _('START')
    PAUSE = 2, _('PAUSE')
    ABORT = 3, _('ABORT')
    END = 4, _('END')

CAMPAIGN_STATUS_COLOR = {1: "green", 2: "blue", 3: "orange", 4: "red"}


class CAMPAIGN_COLUMN_NAME(Choice):
    key = _('key')
    name = _('name')
    start_date = _('start date')
    type = _('type')
    app = _('app')
    contacts = _('contacts')
    status = _('status')


class AMD_BEHAVIOR(Choice):
    ALWAYS = 1, _('ALWAYS PLAY MESSAGE')
    HUMAN_ONLY = 2, _('PLAY MESSAGE TO HUMAN ONLY')
    VOICEMAIL_ONLY = 3, _('LEAVE MESSAGE TO VOICEMAIL ONLY')


class SUBSCRIBER_COLUMN_NAME(Choice):
    contact = _('contact')
    updated_date = _('date')
    count_attempt = _('attempts')
    completion_count_attempt = _('completion attempts')
    status = _('status')
    disposition = _('disposition')
    collected_data = _('response')
    agent = _('agent')
