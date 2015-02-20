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

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from user_profile.models import UserProfile
from django.contrib.auth.forms import PasswordChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset


class UserPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Fieldset('', 'old_password', 'new_password1', 'new_password2', css_class='col-md-4 col-xs-8')
        )


class UserChangeDetailForm(ModelForm):

    """A form used to change the detail of a user in the Customer UI."""
    email = forms.CharField(label=_('Email address'), required=True)

    class Meta:
        model = User
        fields = ["last_name", "first_name", "email"]

    def __init__(self, user, *args, **kwargs):
        super(UserChangeDetailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = False
        css_class = 'col-md-4'
        self.helper.layout = Layout(
            Div(
                Div('last_name', css_class=css_class),
                Div('first_name', css_class=css_class),
                Div('email', css_class=css_class),
            ),
        )

        self.fields['last_name'].widget.attrs['ng-model'] = "user.last_name"
        self.fields['first_name'].widget.attrs['ng-model'] = "user.first_name"
        self.fields['email'].widget.attrs['ng-model'] = "user.email"


class UserChangeDetailExtendForm(ModelForm):

    """A form used to change the detail of a user in the Customer UI."""
    class Meta:
        model = UserProfile
        fields = ["address", "city", "state", "country", "zip_code", "phone_no",
                  "fax", "company_name", "company_website", "language", "note"]

    def __init__(self, user, *args, **kwargs):
        super(UserChangeDetailExtendForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = False
        css_class = 'col-md-4'
        self.helper.layout = Layout(
            Div(
                Div('address', css_class=css_class),
                Div('city', css_class=css_class),
                Div('state', css_class=css_class),
                Div('country', css_class=css_class),
                Div('zip_code', css_class=css_class),
                Div('phone_no', css_class=css_class),
                Div('fax', css_class=css_class),
                Div('company_name', css_class=css_class),
                Div('company_website', css_class=css_class),
                Div('language', css_class=css_class),
                Div('note', css_class=css_class),
            ),
        )


class CheckPhoneNumberForm(forms.Form):

    """A form used to check the phone number in the Customer UI."""
    phone_number = forms.CharField(label=_('Verify phone number'), required=True,
                                   help_text=_("verify if a phone number is authorized to call"))

    def __init__(self, *args, **kwargs):
        super(CheckPhoneNumberForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Fieldset('', 'phone_number', css_class='col-md-4 col-xs-8'),
        )


class UserProfileForm(ModelForm):

    class Meta:
        model = UserProfile
