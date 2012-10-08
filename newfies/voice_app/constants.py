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

from django.utils.translation import ugettext_lazy as _
from common.utils import Choice


class VOICEAPP_TYPE(Choice):
    DIAL = 1, u'DIAL'
    PLAYAUDIO = 2, u'PLAYAUDIO'
    CONFERENCE = 3, u'CONFERENCE'
    SPEAK = 4, u'SPEAK'
