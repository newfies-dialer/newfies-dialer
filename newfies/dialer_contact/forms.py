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
from django.forms.widgets import NumberInput
from django.utils.translation import ugettext_lazy as _
from dialer_contact.models import Phonebook, Contact
from dialer_contact.constants import STATUS_CHOICE
from dialer_campaign.function_def import get_phonebook_list
from bootstrap3_datetime.widgets import DateTimePicker
from mod_utils.forms import SaveUserModelForm, common_submit_buttons
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.layout import Layout, Fieldset, Div


class AdminSearchForm(forms.Form):

    """General Search Form with From & To date para."""
    from_date = forms.CharField(label=_('from'), required=False, max_length=10)
    to_date = forms.CharField(label=_('to'), required=False, max_length=10)


class SearchForm(AdminSearchForm):

    """General Search Form with From & To date para."""
    from_date = forms.CharField(
        label=_('From'), required=False, max_length=10,
        widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}))
    to_date = forms.CharField(
        label=_('To'), required=False, max_length=10,
        widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}))


class FileImport(forms.Form):

    """General Form : CSV file upload"""
    csv_file = forms.FileField(
        label=_('Upload CSV file using the pipe "|" as the field delimiter, e.g. ' +
                '1234567890|surname|forename|email@somewhere.com|test-contact|1|' +
                'address|city|state|US|unit|{"age":"32","title":"doctor"}|'),
        required=True,
        error_messages={'required': 'please upload a CSV File'})

    def clean_csv_file(self):
        """Form Validation :  File extension Check"""
        filename = self.cleaned_data["csv_file"]
        file_exts = ["csv", "txt"]
        if str(filename).split(".")[1].lower() in file_exts:
            return filename
        else:
            raise forms.ValidationError(_(u'document types accepted: %s' % ' '.join(file_exts)))


class Contact_fileImport(FileImport):

    """Admin Form : Import CSV file with phonebook"""
    phonebook = forms.ChoiceField(label=_("Phonebook"), required=False, help_text=_("select phonebook"))

    def __init__(self, user, *args, **kwargs):
        super(Contact_fileImport, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Div(
                Div(Fieldset('', 'phonebook', 'csv_file')),
            ),
        )
        common_submit_buttons(self.helper.layout, 'import')

        # To get user's phonebook list
        if user:  # and not user.is_superuser
            self.fields['phonebook'].choices = get_phonebook_list(user)


class PhonebookForm(SaveUserModelForm):

    """Phonebook ModelForm"""
    class Meta:
        model = Phonebook
        fields = ['name', 'description']
        exclude = ('user',)
        widgets = {
            'description': Textarea(attrs={'cols': 26, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(PhonebookForm, self).__init__(*args, **kwargs)
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


def phonebook_list(user):
    """Return phonebook list of logged in user"""
    result_list = []
    result_list.append((0, '---'))
    for phonebook in Phonebook.objects.filter(user=user).order_by('id'):
        result_list.append((phonebook.id, phonebook.name))
    return result_list


class ContactForm(ModelForm):

    """Contact ModelForm"""

    class Meta:
        model = Contact
        fields = ['phonebook', 'contact', 'last_name', 'first_name', 'status', 'email', 'unit_number',
                  'address', 'city', 'state', 'country', 'description', 'additional_vars']
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        if self.instance.id:
            form_action = common_submit_buttons(default_action='update')
        else:
            form_action = common_submit_buttons(default_action='add')
        css_class = 'col-md-6'
        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    _('General'),
                    Div(
                        Div('phonebook', css_class=css_class),
                        Div('contact', css_class=css_class),
                        Div('last_name', css_class=css_class),
                        Div('first_name', css_class=css_class),
                        Div('status', css_class=css_class),
                        Div('email', css_class=css_class),
                        css_class='row'
                    ),
                    form_action,
                    css_class='well'
                ),
                Tab(
                    _('Advanced Data'),
                    Div(
                        Div('unit_number', css_class=css_class),
                        Div('address', css_class=css_class),
                        Div('city', css_class=css_class),
                        Div('state', css_class=css_class),
                        Div('country', css_class=css_class),
                        Div('description', css_class=css_class),
                        Div('additional_vars', css_class=css_class),
                        css_class='row'
                    ),
                    form_action,
                    css_class='well'
                ),
            ),
        )

        # To get user's phonebook list
        if user:
            self.fields['phonebook'].choices = phonebook_list(user)


class ContactSearchForm(forms.Form):

    """Search Form on Contact List"""
    contact_no = forms.CharField(label=_('Contact number'), required=False, widget=NumberInput())
    contact_name = forms.CharField(
        label=_('Contact Name'), required=False,
        widget=forms.TextInput(attrs={'size': 15}))
    phonebook = forms.ChoiceField(label=_('Phonebook'), required=False)
    contact_status = forms.TypedChoiceField(label=_('Status'), required=False, choices=list(STATUS_CHOICE),
                                            initial=STATUS_CHOICE.ALL)

    def __init__(self, user, *args, **kwargs):
        super(ContactSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        css_class = 'col-md-3'
        self.helper.layout = Layout(
            Div(
                Div('contact_no', css_class=css_class),
                Div('contact_name', css_class=css_class),
                Div('phonebook', css_class=css_class),
                Div('contact_status', css_class=css_class),
                css_class='row'
            ),
        )
        common_submit_buttons(self.helper.layout, 'search')

        if user:
            self.fields['phonebook'].choices = phonebook_list(user)
