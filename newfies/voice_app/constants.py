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

from django.utils.translation import ugettext as _
from common.utils import Choice


class VOICEAPP_TYPE(Choice):
    DIAL = 1, _('DIAL')
    PLAYAUDIO = 2, _('PLAYAUDIO')
    CONFERENCE = 3, _('CONFERENCE')
    SPEAK = 4, _('SPEAK')


class VOICEAPP_COLUMN_NAME(Choice):
    name = _('name')
    description = _('description')
    type = _('type')
    gateway = _('gateway')
    data = _('data')
    tts_language = _('TTS Language')
    date = _('date')