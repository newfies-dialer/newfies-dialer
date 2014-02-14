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
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div
from crispy_forms.bootstrap import FormActions


class ForgotForm(forms.Form):
    """Forgot password Form"""
    email = forms.EmailField(max_length=60, label=_('email').capitalize(), required=True)
    email.widget.attrs['class'] = 'form-control'

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Div(
                Div('email', css_class='col-md-4'),
                css_class='row'
            ),
            FormActions(Submit('submit', 'Reset my password'))
        )
        super(ForgotForm, self).__init__(*args, **kwargs)
