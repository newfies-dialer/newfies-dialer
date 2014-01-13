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

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from user_profile.models import UserProfile
from django.contrib.auth.forms import PasswordChangeForm


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class UserChangeDetailForm(ModelForm):
    """A form used to change the detail of a user in the Customer UI."""
    email = forms.CharField(label=_('Email address'), required=True)

    class Meta:
        model = User
        fields = ["last_name", "first_name", "email"]

    def __init__(self, user, *args, **kwargs):
        super(UserChangeDetailForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        self.fields['last_name'].widget.attrs['ng-model'] = "user.last_name"
        self.fields['first_name'].widget.attrs['ng-model'] = "user.first_name"
        self.fields['email'].widget.attrs['ng-model'] = "user.email"


class UserChangeDetailExtendForm(ModelForm):
    """A form used to change the detail of a user in the Customer UI."""
    class Meta:
        model = UserProfile
        #fields = ["address", "city", "state", "country", "zip_code",
        #          "phone_no", "fax", "company_name", "company_website",
        #          "language", "note"]
        fields = ["address"]

    def __init__(self, user, *args, **kwargs):
        #self.user = user
        super(UserChangeDetailExtendForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class CheckPhoneNumberForm(forms.Form):
    """A form used to check the phone number in the Customer UI."""
    phone_number = forms.CharField(
        label=_('verify phone number'),
        required=True,
        help_text=_("verify if a phone number is authorized to call"))

    def __init__(self, *args, **kwargs):
        super(CheckPhoneNumberForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class UserProfileForm(ModelForm):

    class Meta:
        model = UserProfile
