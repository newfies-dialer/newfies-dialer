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


class SECTION_TYPE(Choice):
    PLAY_MESSAGE = 1, _('PLAY MESSAGE')
    MULTI_CHOICE = 2, _('MULTI-CHOICE')
    RATING_SECTION = 3, _('RATING QUESTION')
    CAPTURE_DIGITS = 4, _('CAPTURE DIGITS')
    RECORD_MSG = 5, _('RECORD MESSAGE')
    CALL_TRANSFER = 6, _('CALL TRANSFER')
    HANGUP_SECTION = 7, _('HANGUP')
    CONFERENCE = 8, _('CONFERENCE')
    DNC = 9, _('DNC')
    SMS = 10, _('SMS')


SURVEY_COLUMN_NAME = {
    'name': _('name'),
    'description': _('description'),
    'date': _('date')
}

SURVEY_CALL_RESULT_NAME = {
    'date': _('call-date '),
    'destination': _('destination'),
    'duration': _('duration'),
    'disposition': _('disposition'),
    'result': _('survey result')
}

SEALED_SURVEY_COLUMN_NAME = {
    'name': _('name'),
    'description': _('description'),
    'campaign': _('campaign'),
    'date': _('date')
}
