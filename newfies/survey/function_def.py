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

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from audiofield.models import AudioFile


def field_list(name, user=None):
    """Return List of audio file names"""
    if name == "audiofile" and user is None:
        list = AudioFile.objects.all()

    if name == "audiofile" and user is not None:
        list = AudioFile.objects.filter(user=user)

    return ((l.id, l.name) for l in list)