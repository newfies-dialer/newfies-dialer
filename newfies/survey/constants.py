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

from django.utils.translation import ugettext as _
from common.utils import Choice


class SECTION_TYPE(Choice):
    PLAY_MESSAGE = 1, _('play message').capitalize()
    MULTI_CHOICE = 2, _('multi-choice').capitalize()
    RATING_SECTION = 3, _('rating question').capitalize()
    CAPTURE_DIGITS = 4, _('capture digits').capitalize()
    RECORD_MSG = 5, _('record message').capitalize()
    CALL_TRANSFER = 6, _('call transfer').capitalize()
    HANGUP_SECTION = 7, _('hangup').capitalize()
    CONFERENCE = 8, _('conference').capitalize()
    DNC = 9, _('DNC')
    SMS = 10, _('SMS')


class SURVEY_COLUMN_NAME(Choice):
    name = _('name')
    description = _('description')
    date = _('date')


class SURVEY_CALL_RESULT_NAME(Choice):
    date = _('call-date ')
    destination = _('destination')
    duration = _('duration')
    disposition = _('disposition')
    result = _('survey result')


class SEALED_SURVEY_COLUMN_NAME(Choice):
    name = _('name')
    description = _('description')
    campaign = _('campaign')
    date = _('date')
