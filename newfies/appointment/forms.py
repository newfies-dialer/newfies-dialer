#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django.forms import ModelForm
#from django.contrib.auth.forms import UserChangeForm
#from django.utils.translation import ugettext as _
from appointment.models.users import CalendarUserProfile


class CalendarUserProfileForm(ModelForm):
    """CalendarUserProfileForm"""

    class Meta:
        model = CalendarUserProfile
