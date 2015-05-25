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

from django_lets_go.utils import Choice


class AGENT_STATUS(Choice):
    LOGGED_OUT = 1, 'logged out'
    AVAILABLE = 2, 'available'
    ON_DEMAND = 3, 'available (on demand)'
    ON_BREAK = 4, 'on break'


class AGENT_TYPE(Choice):
    CALLBACK = 1, 'callback'
    UUID_STANDBY = 2, 'uuid-standby'
