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

from django.contrib.auth.models import User
from dilla import spam
import random
import logging

log = logging.getLogger('dilla')


@spam.strict_handler('dialer_cdr.VoIPCall.duration')
def get_duration(record, field):
    return random.randint(1, 100)


@spam.strict_handler('dialer_cdr.VoIPCall.user')
def get_user(record, field):
    return User.objects.get(pk=1)
