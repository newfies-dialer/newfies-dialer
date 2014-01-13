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
from django.conf import settings
from django.forms.util import ErrorList
from django.contrib.auth.models import User
from django.forms import ModelForm, Textarea
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from dialer_campaign.models import Campaign, Subscriber
from dialer_campaign.constants import CAMPAIGN_STATUS, SUBSCRIBER_STATUS
from dialer_campaign.function_def import user_dialer_setting, get_phonebook_list
from dialer_contact.forms import SearchForm
#from agent.function_def import agent_list
#from agent.models import AgentProfile, Agent
from user_profile.models import UserProfile
from common.common_functions import get_unique_code
from dnc.models import DNC
from bootstrap3_datetime.widgets import DateTimePicker


def get_object_choices(available_objects):
    """Function is used to get object_choices for
    ``content_object`` field in campaign form"""
    object_choices = []
    for obj in available_objects:
        type_id = ContentType.objects.get_for_model(obj.__class__).id
        obj_id = obj.id
        # form_value - e.g."type:12-id:3"
        form_value = "type:%s-id:%s" % (type_id, obj_id)
        display_text = '%s : %s' % (str(ContentType.objects.get_for_model(obj.__class__)), str(obj))
        object_choices.append([form_value, display_text])

    return object_choices


class CampaignForm(ModelForm):
    """Campaign ModelForm"""
    campaign_code = forms.CharField(widget=forms.HiddenInput)
    ds_user = forms.CharField(widget=forms.HiddenInput)

    content_object = forms.ChoiceField(label=_("application"), )

    selected_phonebook = forms.CharField(widget=forms.HiddenInput,
                                         required=False)
    selected_content_object = forms.CharField(widget=forms.HiddenInput,
                                              required=False)

    class Meta:
        model = Campaign
        fields = ['campaign_code', 'name',
                  'callerid', 'caller_name', 'aleg_gateway', 'sms_gateway',
                  'content_object', # 'content_type', 'object_id'
                  'extra_data', 'dnc', 'description', 'phonebook',
                  'frequency', 'callmaxduration', 'maxretry',
                  'intervalretry', 'calltimeout',
                  'completion_maxretry', 'completion_intervalretry',
                  'startingdate', 'expirationdate',
                  'daily_start_time', 'daily_stop_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday', 'ds_user',
                  'selected_phonebook', 'selected_content_object',
                  'voicemail', 'amd_behavior', 'voicemail_audiofile',
                  'agent_script', 'lead_disposition', 'external_link'
                  ]
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
            'agent_script': Textarea(attrs={'cols': 23, 'rows': 3}),
            'lead_disposition': Textarea(attrs={'cols': 23, 'rows': 3}),
            'external_link': Textarea(attrs={'cols': 23, 'rows': 3}),
            'startingdate': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
            'expirationdate': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
        }

    def __init__(self, user, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['campaign_code'].initial = get_unique_code(length=5)
        exclude_list = ['voicemail', 'monday', 'tuesday', 'wednesday',
                        'thursday', 'friday', 'saturday', 'sunday']

        for i in self.fields.keyOrder:
            if i not in exclude_list:
                self.fields[i].widget.attrs['class'] = "form-control"

        if user:
            self.fields['ds_user'].initial = user
            list_gw = []
            dnc_list = []
            phonebook_list = get_phonebook_list(user)
            self.fields['phonebook'].choices = phonebook_list
            self.fields['phonebook'].initial = str(phonebook_list[0][0])

            list = UserProfile.objects.get(user=user).userprofile_gateway.all()
            gw_list = ((l.id, l.name) for l in list)

            dnc_list.append(('', '---'))
            list = DNC.objects.values_list('id', 'name').filter(user=user).order_by('id')
            for l in list:
                dnc_list.append((l[0], l[1]))
            self.fields['dnc'].choices = dnc_list

            for i in gw_list:
                list_gw.append((i[0], i[1]))
            self.fields['aleg_gateway'].choices = list_gw

            if instance.has_been_duplicated:
                from survey.models import Survey
                available_objects = Survey.objects.filter(user=user, campaign=instance)
                object_choices = get_object_choices(available_objects)
                self.fields['content_object'].widget.attrs['readonly'] = True
            else:
                from survey.models import Survey_template
                available_objects = Survey_template.objects.filter(user=user)
                object_choices = get_object_choices(available_objects)

            self.fields['content_object'].choices = object_choices

            # Voicemail setting is not enabled by default
            if settings.AMD:
                from survey.forms import get_audiofile_list
                self.fields['voicemail_audiofile'].choices = get_audiofile_list(user)

        # if campaign is running
        if instance.status == CAMPAIGN_STATUS.START:
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['caller_name'].widget.attrs['readonly'] = True
            self.fields['callerid'].widget.attrs['readonly'] = True
            self.fields['extra_data'].widget.attrs['readonly'] = True
            self.fields['phonebook'].widget.attrs['disabled'] = 'disabled'
            self.fields['lead_disposition'].widget.attrs['readonly'] = True

            selected_phonebook = ''
            if instance.phonebook.all():
                selected_phonebook = \
                    ",".join(["%s" % (i.id) for i in instance.phonebook.all()])
            self.fields['selected_phonebook'].initial = selected_phonebook

            self.fields['content_object'].widget.attrs['disabled'] = 'disabled'
            self.fields['content_object'].required = False
            self.fields['selected_content_object'].initial = "type:%s-id:%s" \
                % (instance.content_type.id, instance.object_id)

    def clean(self):
        cleaned_data = self.cleaned_data
        ds_user = cleaned_data.get("ds_user")
        frequency = cleaned_data.get('frequency')
        callmaxduration = cleaned_data.get('callmaxduration')
        maxretry = cleaned_data.get('maxretry')
        calltimeout = cleaned_data.get('calltimeout')
        phonebook = cleaned_data.get('phonebook')

        if not phonebook:
            msg = _('you must select at least one phonebook')
            self._errors['phonebook'] = ErrorList([msg])
            del self.cleaned_data['phonebook']

        dialer_set = user_dialer_setting(User.objects.get(username=ds_user))
        if dialer_set:
            if frequency > dialer_set.max_frequency:
                msg = _('maximum frequency limit of %d exceeded.' % dialer_set.max_frequency)
                self._errors['frequency'] = ErrorList([msg])
                del self.cleaned_data['frequency']

            if callmaxduration > dialer_set.callmaxduration:
                msg = _('maximum duration limit of %d exceeded.' % dialer_set.callmaxduration)
                self._errors['callmaxduration'] = ErrorList([msg])
                del self.cleaned_data['callmaxduration']

            if maxretry > dialer_set.maxretry:
                msg = _('maximum retries limit of %d exceeded.' % dialer_set.maxretry)
                self._errors['maxretry'] = ErrorList([msg])
                del self.cleaned_data['maxretry']

            if calltimeout > dialer_set.max_calltimeout:
                msg = _('maximum timeout limit of %d exceeded.' % dialer_set.max_calltimeout)
                self._errors['calltimeout'] = ErrorList([msg])
                del self.cleaned_data['calltimeout']

        return cleaned_data


class DuplicateCampaignForm(ModelForm):
    """DuplicateCampaignForm ModelForm"""
    campaign_code = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Campaign
        fields = ['campaign_code', 'name', 'phonebook']

    def __init__(self, user, *args, **kwargs):
        super(DuplicateCampaignForm, self).__init__(*args, **kwargs)
        self.fields['campaign_code'].initial = get_unique_code(length=5)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        if user:
            phonebook_list = get_phonebook_list(user)
            self.fields['phonebook'].choices = phonebook_list
            self.fields['phonebook'].initial = str(phonebook_list[0][0])


class CampaignAdminForm(ModelForm):
    """Admin Campaign ModelForm"""

    class Meta:
        model = Campaign
        fields = ['campaign_code', 'name', 'description', 'user', 'status',
                  'callerid', 'caller_name', 'startingdate', 'expirationdate',
                  'aleg_gateway', 'sms_gateway', 'content_type', 'object_id', 'extra_data',
                  'phonebook', 'frequency', 'callmaxduration', 'maxretry',
                  'intervalretry', 'calltimeout', 'daily_start_time',
                  'daily_stop_time', 'monday', 'tuesday', 'wednesday',
                  'thursday', 'friday', 'saturday', 'sunday',
                  'completion_maxretry', 'completion_intervalretry',
                  'agent_script', 'lead_disposition']

    def __init__(self, *args, **kwargs):
        super(CampaignAdminForm, self).__init__(*args, **kwargs)
        self.fields['campaign_code'].widget.attrs['readonly'] = True
        self.fields['campaign_code'].initial = get_unique_code(length=5)


class SubscriberReportForm(SearchForm):
    """SubscriberReportForm Admin Form"""
    campaign_id = forms.ChoiceField(label=_('campaign'), required=True)

    def __init__(self, *args, **kwargs):
        super(SubscriberReportForm, self).__init__(*args, **kwargs)
        campaign_list = Campaign.objects.values_list('id', 'name').all().order_by('-id')
        self.fields['campaign_id'].choices = campaign_list
        list = []
        list.append((0, ''))
        campaign_list = Campaign.objects.values_list('id', 'name').all().order_by('-id')
        for i in campaign_list:
            list.append((i[0], i[1]))

        self.fields['campaign_id'].choices = list


class SubscriberAdminForm(ModelForm):
    """SubscriberAdminForm"""

    class Meta:
        model = Subscriber

    def __init__(self, *args, **kwargs):
        super(SubscriberAdminForm, self).__init__(*args, **kwargs)
        #self.fields['agent'].choices = agent_list()

subscriber_status_list = []
subscriber_status_list.append(('all', _('all').upper()))
for i in SUBSCRIBER_STATUS:
    subscriber_status_list.append((i[0], i[1]))


class SubscriberSearchForm(SearchForm):
    """Search Form on Subscriber List"""
    campaign_id = forms.ChoiceField(label=_('campaign'), required=True)
    agent_id = forms.ChoiceField(label=_('agent'), required=True)
    status = forms.ChoiceField(label=_('status'),
                               choices=subscriber_status_list,
                               required=False)

    def __init__(self, user, *args, **kwargs):
        super(SubscriberSearchForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        if user:
            camp_list = []
            camp_list.append((0, _('all').upper()))
            if user.is_superuser:
                campaign_list = Campaign.objects.values_list('id', 'name') \
                    .all().order_by('-id')
            else:
                campaign_list = Campaign.objects.values_list('id', 'name') \
                    .filter(user=user).order_by('-id')

            for i in campaign_list:
                camp_list.append((i[0], i[1]))

            """
            agent_list = []
            agent_list.append((0, _('all').upper()))

            if user.is_superuser:
                agent_profile_list = AgentProfile.objects.values_list('user_id', flat=True) \
                    .filter(is_agent=True)
            else:
                agent_profile_list = AgentProfile.objects.values_list('user_id', flat=True) \
                    .filter(is_agent=True, manager=user)

            a_list = Agent.objects.values_list('id', 'username') \
                .filter(id__in=agent_profile_list)
            for i in a_list:
                agent_list.append((i[0], i[1]))
            self.fields['agent_id'].choices = agent_list
            """
            self.fields['campaign_id'].choices = camp_list


campaign_status_list = []
campaign_status_list.append(('all', _('all').upper()))
for i in CAMPAIGN_STATUS:
    campaign_status_list.append((i[0], i[1]))


class CampaignSearchForm(forms.Form):
    phonebook_id = forms.ChoiceField(label=_("phonebook"), )
    status = forms.ChoiceField(label=_("status"), choices=campaign_status_list, )

    def __init__(self, user, *args, **kwargs):
        super(CampaignSearchForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        if user:
            self.fields['phonebook_id'].choices = get_phonebook_list(user)
