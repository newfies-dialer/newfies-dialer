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

from django.template.defaultfilters import register
from django.conf import settings
import os.path


@register.filter(name='get_file_basename')
def get_file_basename(val):
    if val:
        file_url = settings.MEDIA_URL + str(val)
        return os.path.basename(file_url)
    return ''
