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
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django import forms
from django.forms.util import ErrorList
from django.forms import ModelForm, Textarea
from django.utils.translation import ugettext_lazy as _

from dialer_campaign.function_def import user_dialer_setting
from dialer_contact.forms import SearchForm, AdminSearchForm
from sms.models.message import MESSAGE_STATUSES
from mod_sms.models import SMSCampaign, get_unique_code
from frontend.constants import SEARCH_TYPE
from bootstrap3_datetime.widgets import DateTimePicker
from dialer_campaign.forms import get_phonebook_list,\
    campaign_status_list as sms_campaign_status_list

from mod_utils.forms import common_submit_buttons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Field, HTML
from crispy_forms.bootstrap import TabHolder, Tab


def get_smscampaign_list(user=None):
    """get list of smscampaign"""
    camp_list = []
    camp_list.append((0, _('ALL')))
    if user is None:
        pb_list = SMSCampaign.objects.all()
    else:
        pb_list = SMSCampaign.objects.filter(user=user)
    for i in pb_list:
        camp_list.append((i.id, i.name))
    return camp_list


class SMSCampaignForm(ModelForm):

    """SMSCampaign ModelForm"""
    campaign_code = forms.CharField(widget=forms.HiddenInput)
    # content_object = forms.ChoiceField(label=_("Application"),)

    class Meta:
        model = SMSCampaign
        # fields = ['campaign_code', 'name', 'callerid', 'sms_gateway',
        #          'phonebook', 'extra_data', 'text_message',
        #          'frequency', 'maxretry', 'intervalretry',
        #          'startingdate', 'expirationdate',
        #          'daily_start_time', 'daily_stop_time',
        #          'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
        #          'saturday', 'sunday']
        exclude = ('user', 'status', 'imported_phonebook', 'stoppeddate')
        widgets = {
            'extra_data': Textarea(attrs={'cols': 23, 'rows': 3}),
            'text_message': Textarea(attrs={'cols': 23, 'rows': 3}),
            'startingdate': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
            'expirationdate': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
        }

    def __init__(self, user, *args, **kwargs):
        super(SMSCampaignForm, self).__init__(*args, **kwargs)
        self.user = user
        self.helper = FormHelper()

        if self.instance.id:
            form_action = common_submit_buttons(default_action='update')
        else:
            form_action = common_submit_buttons(default_action='add')

        week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        week_days_html = """<div class="row"><div class="col-md-12 col-xs-6">"""

        for i in week_days:
            week_days_html += """
                <div class="col-md-3">
                    <div class="btn-group" data-toggle="buttons">
                        <label for="{{ form.%s.auto_id }}">{{ form.%s.label }}</label><br/>
                        <div class="make-switch switch-small">
                        {{ form.%s }}
                        </div>
                    </div>
                </div>
                """ % (i, i, i)

        week_days_html += """</div></div>"""
        css_class = 'col-md-6'
        self.helper.layout = Layout(
            Field('campaign_code'),
            TabHolder(
                Tab(_('General Settings'),
                    Div(
                        Div('name', css_class=css_class),
                        Div('callerid', css_class=css_class),
                        Div('sms_gateway', css_class=css_class),
                        Div('phonebook', css_class=css_class),
                        Div('extra_data', css_class=css_class),
                        Div('text_message', css_class=css_class),
                        css_class='row'
                ),
                    form_action,
                    css_class='well'
                ),
                Tab(_('Completion Settings'),
                    Div(
                        Div('frequency', css_class=css_class),
                        Div('maxretry', css_class=css_class),
                        Div('intervalretry', css_class=css_class),
                        css_class='row'
                ),
                    form_action,
                    css_class='well'
                ),
                Tab('schedule',
                    Div(
                        Div(HTML("""<label>%s<label>""" % (_('Week days'))), css_class="col-md-3"),
                        HTML(week_days_html),
                        HTML("""<div>&nbsp;</div>"""),
                        Div('startingdate', css_class=css_class),
                        Div('expirationdate', css_class=css_class),
                        Div('daily_start_time', css_class=css_class),
                        Div('daily_stop_time', css_class=css_class),
                        css_class='row'
                    ),
                    form_action,
                    css_class='well'
                    ),
            ),
        )

        self.fields['campaign_code'].initial = get_unique_code(length=5)
        if user:
            phonebook_list = get_phonebook_list(user)
            if not phonebook_list:
                phonebook_list = []
                phonebook_list.append(('', '---'))

            self.fields['phonebook'].choices = phonebook_list
            self.fields['phonebook'].initial = str(phonebook_list[0][0])

    def clean(self):
        cleaned_data = self.cleaned_data
        frequency = cleaned_data.get('frequency')
        maxretry = cleaned_data.get('maxretry')
        phonebook = cleaned_data.get('phonebook')

        if not phonebook:
            msg = _('you must select at least one phonebook')
            self._errors['phonebook'] = ErrorList([msg])
            del self.cleaned_data['phonebook']

        sms_dialer_set = user_dialer_setting(self.user)
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
                  'text_message', 'phonebook', 'frequency', 'maxretry',
                  'intervalretry', 'daily_start_time', 'daily_stop_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday']

    def __init__(self, *args, **kwargs):
        super(SMSCampaignAdminForm, self).__init__(*args, **kwargs)
        self.fields['campaign_code'].widget.attrs['readonly'] = True
        self.fields['campaign_code'].initial = get_unique_code(length=5)


message_list = []
message_list.append(('all', _('ALL')))
for i in MESSAGE_STATUSES:
    message_list.append((i[0], i[1]))


class SMSDashboardForm(forms.Form):

    """SMSDashboard Form"""
    smscampaign = forms.ChoiceField(label=_('SMS Campaign'), required=False)
    search_type = forms.ChoiceField(label=_('type'), required=False, choices=list(SEARCH_TYPE),
                                    initial=SEARCH_TYPE.D_Last_24_hours)

    def __init__(self, user, *args, **kwargs):
        super(SMSDashboardForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_class = 'well form-inline text-right'
        self.helper.layout = Layout(
            Div(
                Div('smscampaign', css_class='form-group'),
                Div('search_type', css_class='form-group'),
                Div(Submit('submit', _('Search')), css_class='form-group'),
            ),
        )

        # To get user's running campaign list
        if user:
            campaign_list = SMSCampaign.objects.filter(user=user).order_by('-id')

            campaign_choices = [(0, _('Select campaign'))]
            for cp in campaign_list:
                campaign_choices.append((cp.id, unicode(cp.name)))

            self.fields['smscampaign'].choices = campaign_choices


class SMSSearchForm(SearchForm):

    """SMS Report Search Parameters"""
    status = forms.ChoiceField(label=_('status'), choices=message_list, required=False)
    smscampaign = forms.ChoiceField(label=_('SMS Campaign'), required=False)

    def __init__(self, user, *args, **kwargs):
        super(SMSSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        css_class = 'col-md-4'
        self.helper.layout = Layout(
            Div(
                Div('from_date', css_class=css_class),
                Div('to_date', css_class=css_class),
                Div('status', css_class=css_class),
                Div('smscampaign', css_class=css_class),
                css_class='row'
            ),
        )
        common_submit_buttons(self.helper.layout, 'search')
        if user:
            self.fields['smscampaign'].choices = get_smscampaign_list(user)


class AdminSMSSearchForm(AdminSearchForm):

    """SMS Report Search Parameters"""
    status = forms.ChoiceField(label=_('status'), choices=message_list,
                               required=False)
    smscampaign = forms.ChoiceField(label=_('SMS Campaign'), required=False)

    def __init__(self, *args, **kwargs):
        super(AdminSMSSearchForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'from_date', 'to_date', 'status', 'smscampaign'
        ]
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        self.fields['smscampaign'].choices = get_smscampaign_list()


class SMSCampaignSearchForm(forms.Form):
    phonebook_id = forms.ChoiceField(label=_("Phonebook"))
    status = forms.ChoiceField(label=_("Status"), choices=sms_campaign_status_list)

    def __init__(self, user, *args, **kwargs):
        super(SMSCampaignSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        css_class = 'col-md-3'
        self.helper.layout = Layout(
            Div(
                Div('phonebook_id', css_class=css_class),
                Div('status', css_class=css_class),
                css_class='row'
            ),
        )
        common_submit_buttons(self.helper.layout, 'search')
        if user:
            self.fields['phonebook_id'].choices = get_phonebook_list(user)


class DuplicateSMSCampaignForm(ModelForm):

    """DuplicateSMSCampaignForm ModelForm"""
    campaign_code = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = SMSCampaign
        fields = ['campaign_code', 'name', 'phonebook']

    def __init__(self, user, *args, **kwargs):
        super(DuplicateSMSCampaignForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        css_class = 'col-md-12'
        self.helper.layout = Layout(
            Field('campaign_code'),
            Div(
                Div('name', css_class=css_class),
                Div('phonebook', css_class=css_class),
                css_class='row'
            )
        )
        self.fields['campaign_code'].initial = get_unique_code(length=5)

        if user:
            self.fields['phonebook'].choices = get_phonebook_list(user)
