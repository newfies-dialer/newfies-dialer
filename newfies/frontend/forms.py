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
from django import forms
from django.utils.translation import ugettext_lazy as _
from dialer_campaign.models import Campaign
from frontend.constants import SEARCH_TYPE


class LoginForm(forms.Form):
    """Client Login Form"""
    user = forms.CharField(max_length=30,
        label=_('username'), required=True)
    user.widget.attrs['class'] = 'input-small'
    user.widget.attrs['placeholder'] = 'Username'
    password = forms.CharField(max_length=30, label=_('password'),
        required=True, widget=forms.PasswordInput())
    password.widget.attrs['class'] = 'input-small'
    password.widget.attrs['placeholder'] = 'Password'


class DashboardForm(forms.Form):
    """Dashboard Form"""
    campaign = forms.ChoiceField(label=_('campaign'), required=False)
    search_type = forms.ChoiceField(label=_('type'), required=False,
        initial=SEARCH_TYPE.D_Last_24_hours,
        choices=list(SEARCH_TYPE))

    def __init__(self, user, *args, **kwargs):
        super(DashboardForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['campaign', 'search_type']
        # To get user's running campaign list
        if user:
            campaign_list = Campaign.objects.values_list('id', 'name')\
                .filter(user=user).order_by('-id')
            self.fields['campaign'].choices = campaign_list
