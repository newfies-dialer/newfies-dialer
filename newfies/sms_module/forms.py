#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django import forms
from django.forms.util import ErrorList
from django.forms import ModelForm, Textarea
from django.utils.translation import ugettext_lazy as _

from dialer_campaign.function_def import user_dialer_setting
from dialer_contact.forms import SearchForm
from sms.models.message import MESSAGE_STATUSES
from models import SMSCampaign, get_unique_code
from function_def import field_list
from frontend.constants import SEARCH_TYPE
from bootstrap3_datetime.widgets import DateTimePicker


class SMSCampaignForm(ModelForm):
    """SMSCampaign ModelForm"""
    campaign_code = forms.CharField(widget=forms.HiddenInput)
    ds_user = forms.CharField(widget=forms.HiddenInput)

    #content_object = forms.ChoiceField(label=_("Application"),)

    class Meta:
        model = SMSCampaign
        fields = ['campaign_code', 'name', 'description',
                  'callerid', 'status', 'sms_gateway', 'phonebook',
                  'extra_data', 'text_message',
                  'frequency', 'maxretry', 'intervalretry',
                  'startingdate', 'expirationdate',
                  'daily_start_time', 'daily_stop_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday', 'ds_user']
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
            'extra_data': Textarea(attrs={'cols': 23, 'rows': 3}),
            'text_message': Textarea(attrs={'cols': 23, 'rows': 3}),
            'startingdate': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
            'expirationdate': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
        }

    def __init__(self, user, *args, **kwargs):
        super(SMSCampaignForm, self).__init__(*args, **kwargs)
        self.fields['campaign_code'].initial = get_unique_code(length=5)
        exclude_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                        'saturday', 'sunday',]

        for i in self.fields.keyOrder:
            if i not in exclude_list:
                self.fields[i].widget.attrs['class'] = "form-control"

        if user:
            self.fields['ds_user'].initial = user
            list_pb = []
            list_gw = []

            list_pb.append((0, '---'))
            pb_list = field_list("phonebook", user)
            for i in pb_list:
                list_pb.append((i[0], i[1]))
            self.fields['phonebook'].choices = list_pb

            list_gw.append((0, '---'))
            gw_list = field_list("gateway", user)
            for i in gw_list:
                list_gw.append((i[0], i[1]))
            self.fields['sms_gateway'].choices = list_gw

    def clean(self):
        cleaned_data = self.cleaned_data
        ds_user = cleaned_data.get("ds_user")
        frequency = cleaned_data.get('frequency')
        maxretry = cleaned_data.get('maxretry')

        sms_dialer_set = user_dialer_setting(ds_user)
        if sms_dialer_set:
            if frequency > sms_dialer_set.sms_max_frequency:
                msg = _('Maximum Frequency limit of %d exceeded.' % sms_dialer_set.sms_max_frequency)
                self._errors['frequency'] = ErrorList([msg])
                del self.cleaned_data['frequency']

            if maxretry > sms_dialer_set.sms_maxretry:
                msg = _('Maximum Retries limit of %d exceeded.' % sms_dialer_set.sms_maxretry)
                self._errors['maxretry'] = ErrorList([msg])
                del self.cleaned_data['maxretry']

        return cleaned_data


class SMSCampaignAdminForm(ModelForm):
    """Admin SMSCampaign ModelForm"""
    class Meta:
        model = SMSCampaign
        fields = ['campaign_code', 'name', 'description', 'user', 'status',
                  'callerid', 'startingdate', 'expirationdate', 'sms_gateway',
                  'text_message', 'phonebook',
                  'frequency', 'maxretry', 'intervalretry',
                  'daily_start_time', 'daily_stop_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday']

    def __init__(self, *args, **kwargs):
        super(SMSCampaignAdminForm, self).__init__(*args, **kwargs)
        self.fields['campaign_code'].widget.attrs['readonly'] = True
        self.fields['campaign_code'].initial = get_unique_code(length=5)


message_list = []
message_list.append(('all', _('all').upper()))
for i in MESSAGE_STATUSES:
    message_list.append((i[0], i[1]))


class SMSDashboardForm(forms.Form):
    """SMSDashboard Form"""
    smscampaign = forms.ChoiceField(label=_('sms campaign'), required=False)
    search_type = forms.ChoiceField(label=_('type'), required=False,
                                    initial=SEARCH_TYPE.D_Last_24_hours,
                                    choices=list(SEARCH_TYPE))

    def __init__(self, user, *args, **kwargs):
        super(SMSDashboardForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['smscampaign', 'search_type']
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        # To get user's running campaign list
        if user:
            camp_list = []
            #list.append((0, '---'))
            pb_list = field_list("smscampaign", user)
            for i in pb_list:
                camp_list.append((i[0], i[1]))
            self.fields['smscampaign'].choices = camp_list


class SMSSearchForm(SearchForm):
    """SMS Report Search Parameters"""
    status = forms.ChoiceField(label=_('status'), choices=message_list,
                               required=False)
    smscampaign = forms.ChoiceField(label=_('sms campaign'), required=False)

    def __init__(self, user, *args, **kwargs):
        super(SMSSearchForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'from_date', 'to_date', 'status', 'smscampaign'
        ]
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        if user:
            camp_list = []
            camp_list.append((0, '---'))
            pb_list = field_list("smscampaign", user)
            for i in pb_list:
                camp_list.append((int(i[0]), i[1]))
            self.fields['smscampaign'].choices = camp_list
