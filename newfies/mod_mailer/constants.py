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


class MAILSPOOLER_TYPE(Choice):
    PENDING = 1, _('PENDING')
    SENT = 2, _('SENT')
    FAILURE = 3, _('FAILURE')
    IN_PROCESS = 4, _('IN_PROCESS')
