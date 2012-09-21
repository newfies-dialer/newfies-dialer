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


class SECTION_TYPE(Choice):
    VOICE_SECTION = 1, u'Voice section'
    MULTIPLE_CHOICE_SECTION = 2, u'Multiple choice question'
    RATING_SECTION = 3, u'Rating question'
    ENTER_NUMBER_SECTION = 4, u'Enter a number'
    RECORD_MSG_SECTION = 5, u'Record message'
    PATCH_THROUGH_SECTION = 6, u'Patch-through'

