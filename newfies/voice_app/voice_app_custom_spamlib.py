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

from voip_app.models import *
from dilla import spam
import string
import random
import decimal
import logging
import datetime


log = logging.getLogger('dilla')


@spam.strict_handler('voip_app.VoipApp.data')
def get_voip_app_data(field):
    return random.choice(string.ascii_letters)
