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

from django.utils.translation import gettext as _
from common.utils import Choice


class SECTION_TYPE(Choice):
    VOICE_SECTION = 1, _('Voice section')
    MULTIPLE_CHOICE_SECTION = 2, _('Multiple choice question')
    RATING_SECTION = 3, _('Rating question')
    ENTER_NUMBER_SECTION = 4, _('Enter a number')
    RECORD_MSG_SECTION = 5, _('Record message')
    PATCH_THROUGH_SECTION = 6, _('Patch-through')
    HANGUP_SECTION = 7, _('Hangup')
