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
from django.contrib.contenttypes.models import ContentType
from dialer_campaign.models import Phonebook, Campaign, \
                                    get_unique_code
from dialer_campaign.function_def import user_dialer_setting
from user_profile.models import UserProfile


class CampaignForm(ModelForm):
    """Campaign ModelForm"""
    campaign_code = forms.CharField(widget=forms.HiddenInput)
    ds_user = forms.CharField(widget=forms.HiddenInput)

    content_object = forms.ChoiceField(label=_("Application"),)

    class Meta:
        model = Campaign
        fields = ['campaign_code', 'name', 'description',
                  'callerid', 'status', 'aleg_gateway',
                  'content_object',  # 'content_type', 'object_id'
                  'extra_data', 'phonebook',
                  'frequency', 'callmaxduration', 'maxretry',
                  'intervalretry', 'calltimeout',
                  'startingdate', 'expirationdate',
                  'daily_start_time', 'daily_stop_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday', 'ds_user',
                  ]
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)
        self.fields['campaign_code'].initial = get_unique_code(length=5)
        self.fields['description'].widget.attrs['class'] = "input-xlarge"

        if user:
            self.fields['ds_user'].initial = user
            list_pb = []
            list_gw = []

            list_pb.append((0, '---'))
            list = Phonebook.objects.filter(user=user)
            pb_list = ((l.id, l.name) for l in list)

            for i in pb_list:
                list_pb.append((i[0], i[1]))
            self.fields['phonebook'].choices = list_pb

            list_gw.append((0, '---'))
            list = UserProfile.objects.get(user=user)
            list = list.userprofile_gateway.all()
            gw_list = ((l.id, l.name) for l in list)

            for i in gw_list:
                list_gw.append((i[0], i[1]))
            self.fields['aleg_gateway'].choices = list_gw

            from voice_app.models import VoiceApp
            from survey.models import SurveyApp
            available_objects = list(VoiceApp.objects.filter(user=user))
            available_objects += list(SurveyApp.objects.filter(user=user))
            object_choices = []
            for obj in available_objects:
                type_id = ContentType.objects.get_for_model(obj.__class__).id
                obj_id = obj.id
                # form_value - e.g."type:12-id:3"
                form_value = "type:%s-id:%s" % (type_id, obj_id)
                display_text = str(ContentType.objects\
                            .get_for_model(obj.__class__)) + ' : ' + str(obj)
                object_choices.append([form_value, display_text])
            self.fields['content_object'].choices = object_choices

    def clean(self):
        cleaned_data = self.cleaned_data
        ds_user = cleaned_data.get("ds_user")
        frequency = cleaned_data.get('frequency')
        callmaxduration = cleaned_data.get('callmaxduration')
        maxretry = cleaned_data.get('maxretry')
        calltimeout = cleaned_data.get('calltimeout')

        dialer_set = user_dialer_setting(ds_user)
        if dialer_set:
            if frequency > dialer_set.max_frequency:
                msg = _('Maximum Frequency limit of %d exceeded.'\
                    % dialer_set.max_frequency)
                self._errors['frequency'] = ErrorList([msg])
                del self.cleaned_data['frequency']

            if callmaxduration > dialer_set.callmaxduration:
                msg = _('Maximum Duration limit of %d exceeded.'\
                         % dialer_set.callmaxduration)
                self._errors['callmaxduration'] = ErrorList([msg])
                del self.cleaned_data['callmaxduration']

            if maxretry > dialer_set.maxretry:
                msg = _('Maximum Retries limit of %d exceeded.' \
                    % dialer_set.maxretry)
                self._errors['maxretry'] = ErrorList([msg])
                del self.cleaned_data['maxretry']

            if calltimeout > dialer_set.max_calltimeout:
                msg = _('Maximum Timeout limit of %d exceeded.'\
                    % dialer_set.max_calltimeout)
                self._errors['calltimeout'] = ErrorList([msg])
                del self.cleaned_data['calltimeout']

        return cleaned_data


class CampaignAdminForm(ModelForm):
    """Admin Campaign ModelForm"""
    class Meta:
        model = Campaign
        fields = ['campaign_code', 'name', 'description', 'user', 'status',
                  'callerid', 'startingdate', 'expirationdate', 'aleg_gateway',
                  'content_type', 'object_id', 'extra_data', 'phonebook',
                  'frequency', 'callmaxduration', 'maxretry', 'intervalretry',
                  'calltimeout', 'daily_start_time', 'daily_stop_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday']

    def __init__(self, *args, **kwargs):
        super(CampaignAdminForm, self).__init__(*args, **kwargs)
        self.fields['campaign_code'].widget.attrs['readonly'] = True
        self.fields['campaign_code'].initial = get_unique_code(length=5)
