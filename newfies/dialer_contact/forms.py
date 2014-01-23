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
from django.forms import ModelForm, Textarea
from django.forms.widgets import NumberInput
from django.utils.translation import ugettext_lazy as _
from dialer_contact.models import Phonebook, Contact
from dialer_contact.constants import STATUS_CHOICE
from dialer_campaign.function_def import get_phonebook_list
#from dialer_contact.constants import CHOICE_TYPE
from bootstrap3_datetime.widgets import DateTimePicker


class AdminSearchForm(forms.Form):
    """General Search Form with From & To date para."""
    from_date = forms.CharField(label=_('from'), required=False, max_length=10)
    to_date = forms.CharField(label=_('to'), required=False, max_length=10)


class SearchForm(AdminSearchForm):
    """General Search Form with From & To date para."""
    from_date = forms.CharField(label=_('from'), required=False, max_length=10,
                                widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                                               "pickTime": False}))
    to_date = forms.CharField(label=_('to'), required=False, max_length=10,
                              widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                                             "pickTime": False}))


class FileImport(forms.Form):
    """General Form : CSV file upload"""
    csv_file = forms.FileField(label=_('upload CSV file using the pipe "|" as the field delimiter, e.g. 1234567890|surname|forename|email@somewhere.com|test-contact|1|address|city|state|US|unit|{"age":"32","title":"doctor"}|'),
            required=True, error_messages={'required': 'please upload a CSV File'})

    def clean_csv_file(self):
        """Form Validation :  File extension Check"""
        filename = self.cleaned_data["csv_file"]
        file_exts = ["csv", "txt"]
        if str(filename).split(".")[1].lower() in file_exts:
            return filename
        else:
            raise forms.ValidationError(_(u'document types accepted: %s' %
                                          ' '.join(file_exts)))


class Contact_fileImport(FileImport):
    """Admin Form : Import CSV file with phonebook"""
    phonebook = forms.ChoiceField(label=_("phonebook"),
                                  required=False,
                                  help_text=_("select phonebook"))

    def __init__(self, user, *args, **kwargs):
        super(Contact_fileImport, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['phonebook', 'csv_file']
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        # To get user's phonebook list
        if user:  # and not user.is_superuser
            self.fields['phonebook'].choices = get_phonebook_list(user)


class PhonebookForm(ModelForm):
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
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


def phonebook_list(user):
    """Return phonebook list of logged in user"""
    phonebook_list = Phonebook.objects.filter(user=user).order_by('id')
    result_list = []
    result_list.append((0, '---'))
    for phonebook in phonebook_list:
        result_list.append((phonebook.id, phonebook.name))
    return result_list


class ContactForm(ModelForm):
    """Contact ModelForm"""

    class Meta:
        model = Contact
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'phonebook', 'contact', 'last_name', 'first_name', 'status', 'email',
            'unit_number', 'address', 'city', 'state', 'country',
            'description', 'additional_vars'
        ]

        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"

        # To get user's phonebook list
        if user:
            self.fields['phonebook'].choices = phonebook_list(user)


class ContactSearchForm(forms.Form):
    """Search Form on Contact List"""
    contact_no = forms.CharField(label=_('contact number'), required=False,
                                 widget=NumberInput())
    # contact_no_type = forms.ChoiceField(label='', required=False, initial=1,
    #                                     choices=list(CHOICE_TYPE), widget=forms.RadioSelect)
    contact_name = forms.CharField(label=_('contact name'), required=False,
                                   widget=forms.TextInput(attrs={'size': 15}))
    phonebook = forms.ChoiceField(label=_('phonebook'), required=False)
    contact_status = forms.TypedChoiceField(label=_('status'), required=False,
                                            choices=list(STATUS_CHOICE),
                                            initial=STATUS_CHOICE.ALL)

    def __init__(self, user, *args, **kwargs):
        super(ContactSearchForm, self).__init__(*args, **kwargs)
        change_field_list = [
            'contact_no', 'contact_name', 'phonebook', 'contact_status'
        ]
        for i in change_field_list:
            self.fields[i].widget.attrs['class'] = "form-control"

        if user:
            self.fields['phonebook'].choices = phonebook_list(user)
