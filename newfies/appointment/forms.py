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
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import ugettext as _
from appointment.models.users import CalendarUserProfile, CalendarUser
from appointment.models.events import Event


class CalendarUserProfileForm(ModelForm):
    """CalendarUserProfileForm"""

    class Meta:
        model = CalendarUserProfile


class EventForm(ModelForm):
    """Admin Event ModelForm"""
    class Meta:
        model = Event
        exclude = ('parent_event', 'occ_count')


class CalendarUserNameChangeForm(UserChangeForm):
    """CalendarUserNameChangeForm is used to change CalendarUser username"""

    class Meta:
        model = CalendarUser
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super(CalendarUserNameChangeForm, self).__init__(*args, **kwargs)


class CalendarUserChangeDetailExtendForm(ModelForm):
    """A form used to change the detail of a CalendarUser in the manager UI."""
    class Meta:
        model = CalendarUserProfile
        exclude = ('manager', 'user')

    def __init__(self, user, *args, **kwargs):
        self.manager = user
        super(CalendarUserChangeDetailExtendForm, self).__init__(*args, **kwargs)

