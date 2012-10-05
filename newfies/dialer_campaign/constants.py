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

from common.utils import Choice


class CAMPAIGN_SUBSCRIBER_STATUS(Choice):
    PENDING = 1, u'PENDING'
    PAUSE = 2, u'PAUSE'
    ABORT = 3, u'ABORT'
    FAIL = 4, u'FAIL'
    COMPLETE = 5, u'COMPLETE'
    IN_PROCESS = 6, u'IN PROCESS'
    NOT_AUTHORIZED = 7, u'NOT AUTHORIZED'


class CAMPAIGN_STATUS(Choice):
    START = 1, u'START'
    PAUSE = 2, u'PAUSE'
    ABORT = 3, u'ABORT'
    END = 4, u'END'

CAMPAIGN_STATUS_COLOR = {1: "green", 2: "blue", 3: "orange", 4: "red"}
