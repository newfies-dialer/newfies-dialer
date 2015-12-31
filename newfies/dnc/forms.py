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
from django.forms import ModelForm, Textarea
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList
from dnc.models import DNC, DNCContact
from dialer_contact.forms import FileImport
from mod_utils.forms import Exportfile

# from django.core.urlresolvers import reverse
from mod_utils.forms import SaveUserModelForm, common_submit_buttons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, HTML


class DNCListForm(SaveUserModelForm):

    """DNC List Form"""

    class Meta:
        model = DNC
        fields = ['name', 'description']
        exclude = ('user',)
        widgets = {
            'description': Textarea(attrs={'cols': 26, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(DNCListForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Div(
                Div(Fieldset('', 'name', 'description', css_class='col-md-6')),
            ),
        )
        if self.instance.id:
            common_submit_buttons(self.helper.layout, 'update')
        else:
            common_submit_buttons(self.helper.layout)


class DNCContactSearchForm(forms.Form):

    """Search Form on Contact List"""
    phone_number = forms.IntegerField(label=_('Phone Number'), required=False)
    dnc = forms.ChoiceField(label=_('Do Not Call list'), required=False)

    def __init__(self, user, *args, **kwargs):
        super(DNCContactSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Div(
                Div('phone_number', css_class='col-md-4'),
                Div('dnc', css_class='col-md-4'),
                css_class='row'
            ),
        )
        common_submit_buttons(self.helper.layout, 'search')
        # To get user's dnc list
        if user:
            dnc_list_user = []
            dnc_list_user.append((0, '---'))
            for i in DNC.objects.values_list('id', 'name').filter(user=user).order_by('-id'):
                dnc_list_user.append((i[0], i[1]))

            self.fields['dnc'].choices = dnc_list_user


class DNCContactForm(ModelForm):

    """DNCContact ModelForm"""

    class Meta:
        model = DNCContact
        fields = ['dnc', 'phone_number']

    def __init__(self, user, *args, **kwargs):
        super(DNCContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Div(
                Div(Fieldset('', 'dnc', 'phone_number', css_class='col-md-6')),
            ),
        )
        if user:
            self.fields['dnc'].choices = DNC.objects.values_list('id', 'name').filter(user=user).order_by('id')

        if self.instance.id:
            common_submit_buttons(self.helper.layout, 'update')
        else:
            common_submit_buttons(self.helper.layout)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', None)
        try:
            int(phone_number)
        except:
            msg = _('Please enter a valid phone number')
            self._errors['phone_number'] = ErrorList([msg])
            del self.cleaned_data['phone_number']
        return phone_number


def get_dnc_list(user):
    """get dnc list for ``dnc_list`` field which is used by DNCContact_fileImport
    & DNCContact_fileExport
    """
    result_list = []
    for dnc in DNC.objects.filter(user=user).order_by('id'):
        contacts_in_dnc = dnc.dnc_contacts_count()
        nbcontact = " -> %d contact(s)" % (contacts_in_dnc)
        dnc_string = dnc.name + nbcontact
        result_list.append((dnc.id, dnc_string))
    return result_list


class DNCContact_fileImport(FileImport):

    """Admin Form : Import CSV file with DNC list"""
    dnc_list = forms.ChoiceField(label=_("DNC List"), required=True, help_text=_("select DNC list"))

    def __init__(self, user, *args, **kwargs):
        super(DNCContact_fileImport, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Div(
                Div(Fieldset('', 'dnc_list', 'csv_file', css_class='col-md-6')),
            ),
        )
        common_submit_buttons(self.helper.layout, 'import')

        # To get user's dnc_list list
        # and not user.is_superuser
        if user:
            self.fields['dnc_list'].choices = get_dnc_list(user)
            self.fields['csv_file'].label = _('Upload CSV file')


class DNCContact_fileExport(Exportfile):

    """
    DNC Contact Export
    """
    dnc_list = forms.ChoiceField(label=_("DNC list"), required=True, help_text=_("select DNC list"))

    def __init__(self, user, *args, **kwargs):
        super(DNCContact_fileExport, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Div(
                Div(Fieldset('', 'dnc_list', css_class='col-md-6')),
                css_class='row'
            ),
            Div(
                Div(HTML("""
                    <b>Export to: </b>
                    <div class="btn-group" data-toggle="buttons">
                        {% for choice in form.export_to.field.choices %}
                        <label class="btn btn-default">
                            <input name='{{ form.export_to.name }}' type='radio' value='{{ choice.0 }}'/> {{ choice.1 }}
                        </label>
                        {% endfor %}
                    </div>
                   """), css_class='col-md-6'),
                css_class='row'
            ),
        )
        common_submit_buttons(self.helper.layout, 'add')

        # To get user's dnc_list list
        if user:  # and not user.is_superuser
            self.fields['dnc_list'].choices = get_dnc_list(user)
