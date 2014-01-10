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
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList
from dnc.models import DNC, DNCContact
from common.common_forms import Exportfile
from dialer_contact.forms import FileImport


class DNCForm(ModelForm):
    """DNC ModelForm"""

    class Meta:
        model = DNC
        fields = ['name', 'description']
        exclude = ('user',)
        widgets = {
            'description': Textarea(attrs={'cols': 26, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(DNCForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class DNCContactSearchForm(forms.Form):
    """Search Form on Contact List"""
    phone_number = forms.CharField(label=_('phone number'), required=False)
    dnc = forms.ChoiceField(label=_('Do Not Call list').title(), required=False)

    def __init__(self, user, *args, **kwargs):
        super(DNCContactSearchForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        # To get user's dnc list
        if user:
            dnc_list_user = []
            dnc_list_user.append((0, '---'))
            dnc_list = DNC.objects.values_list('id', 'name').filter(user=user).order_by('-id')
            for i in dnc_list:
                dnc_list_user.append((i[0], i[1]))

            self.fields['dnc'].choices = dnc_list_user

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', None)
        try:
            int(phone_number)
        except:
            msg = _('Please enter a valid phone number')
            self._errors['phone_number'] = ErrorList([msg])
            del self.cleaned_data['phone_number']
        return phone_number


class DNCContactForm(ModelForm):
    """DNCContact ModelForm"""

    class Meta:
        model = DNCContact
        fields = ['dnc', 'phone_number']

    def __init__(self, user, *args, **kwargs):
        super(DNCContactForm, self).__init__(*args, **kwargs)
        # To get user's dnc list
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        if user:
            self.fields['dnc'].choices = DNC.objects.values_list('id', 'name')\
                .filter(user=user).order_by('id')

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
    dnc_list = DNC.objects.filter(user=user).order_by('id')
    result_list = []
    for dnc in dnc_list:
        contacts_in_dnc = dnc.dnc_contacts_count()
        nbcontact = " -> %d contact(s)" % (contacts_in_dnc)
        dnc_string = dnc.name + nbcontact
        result_list.append((dnc.id, dnc_string))
    return result_list


class DNCContact_fileImport(FileImport):
    """Admin Form : Import CSV file with DNC list"""
    dnc_list = forms.ChoiceField(label=_("DNC List"),
                                 required=True,
                                 help_text=_("select DNC list"))

    def __init__(self, user, *args, **kwargs):
        super(DNCContact_fileImport, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['dnc_list', 'csv_file']
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        # To get user's dnc_list list
        # and not user.is_superuser
        if user:
            self.fields['dnc_list'].choices = get_dnc_list(user)
            self.fields['csv_file'].label = _('upload CSV file')


class DNCContact_fileExport(Exportfile):
    """
    DNC Contact Export
    """
    dnc_list = forms.ChoiceField(label=_("DNC list"), required=True,
                                 help_text=_("select DNC list"))

    def __init__(self, user, *args, **kwargs):
        super(DNCContact_fileExport, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['dnc_list', 'export_to', ]
        self.fields['dnc_list'].widget.attrs['class'] = "form-control"
        # To get user's dnc_list list
        if user:  # and not user.is_superuser
            self.fields['dnc_list'].choices = get_dnc_list(user)
