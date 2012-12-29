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


class SECTION_TYPE(Choice):
    PLAY_MESSAGE = 1, _('Play message')
    MULTI_CHOICE = 2, _('Multi-choice')
    RATING_SECTION = 3, _('Rating question')
    CAPTURE_DIGITS = 4, _('Capture digits')
    RECORD_MSG = 5, _('Record message')
    CALL_TRANSFER = 6, _('Call transfer')
    HANGUP_SECTION = 7, _('Hangup')


class SECTION_TYPE_NOTRANSFER(Choice):
    PLAY_MESSAGE = 1, _('Play message')
    MULTI_CHOICE = 2, _('Multi-choice')
    RATING_SECTION = 3, _('Rating question')
    CAPTURE_DIGITS = 4, _('Capture digits')
    RECORD_MSG = 5, _('Record message')
    #CALL_TRANSFER = 6, _('Call transfer')
    HANGUP_SECTION = 7, _('Hangup')


class SURVEY_COLUMN_NAME(Choice):
    name = _('Name')
    description = _('Description')
    date = _('Date')


class SURVEY_CALL_RESULT_NAME(Choice):
    date = _('Call-date ')
    destination  = _('Destination')
    duration = _('Duration')
    disposition = _('Disposition')
    result = _('Survey Result')