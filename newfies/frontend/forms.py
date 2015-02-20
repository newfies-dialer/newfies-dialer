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
from django.utils.translation import ugettext_lazy as _
from dialer_campaign.models import Campaign
from frontend.constants import SEARCH_TYPE
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML
from crispy_forms.bootstrap import FormActions


class LoginForm(forms.Form):

    """Client Login Form"""
    user = forms.CharField(max_length=30, label=_('username'), required=True)
    user.widget.attrs['placeholder'] = _('Username')
    password = forms.CharField(max_length=30, label=_('password'), required=True, widget=forms.PasswordInput())
    password.widget.attrs['placeholder'] = _('Password')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = '/login/'
        self.helper.form_show_labels = False
        self.helper.form_class = 'form-inline well'
        self.helper.layout = Layout(
            Div(
                Div('user', css_class='col-xs-3'),
                Div('password', css_class='col-xs-3'),
            ),
            FormActions(
                Submit('submit', 'Login'),
                HTML('<a class="btn btn-warning" href="/password_reset/">%s?</a>' % _('Forgot password')),
            ),
        )


class DashboardForm(forms.Form):

    """Dashboard Form"""
    campaign = forms.ChoiceField(label=_('campaign'), required=False)
    search_type = forms.ChoiceField(label=_('type'), required=False, choices=list(SEARCH_TYPE),
                                    initial=SEARCH_TYPE.D_Last_24_hours)

    def __init__(self, user, *args, **kwargs):
        super(DashboardForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_class = 'well form-inline text-right'
        self.helper.layout = Layout(
            Div(
                Div('campaign', css_class='form-group'),
                Div('search_type', css_class='form-group'),
                Div(Submit('submit', _('Search')), css_class='form-group'),
            ),
        )

        # To get user's running campaign list
        if user:
            campaign_choices = [(0, _('Select campaign'))]
            for cp in Campaign.objects.filter(user=user).order_by('-id'):
                campaign_choices.append((cp.id, unicode(cp.name)))

            self.fields['campaign'].choices = campaign_choices
