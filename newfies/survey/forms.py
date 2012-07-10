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
from django.forms import *
from django.contrib import *
from django.contrib.admin.widgets import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from survey.models import *
from survey.function_def import field_list
from dialer_campaign.models import Campaign
from audiofield.forms import CustomerAudioFileForm

from datetime import *


class SurveyForm(ModelForm):
    """SurveyApp ModelForm"""

    class Meta:
        model = SurveyApp
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance.id:
            self.fields.keyOrder = ['name', 'description']


def get_audiofile_list(user):
    """Get audio file list for logged in user
    with default none option"""
    list_af = []
    list_af.append(('', '---'))
    af_list = field_list(name="audiofile", user=user)
    for i in af_list:
        list_af.append((i[0], i[1]))
    return list_af


def get_question_list(user):
    """Get survey question list for logged in user
    with default none option"""
    list_sq = []
    list_sq.append(('', '---'))

    list = SurveyQuestion.objects.filter(user=user)
    for i in list:
        list_sq.append((i.id, i.question))

    return list_sq


class SurveyQuestionForm(ModelForm):
    """SurveyQuestion ModelForm"""

    class Meta:
        model = SurveyQuestion
        fields = ['question', 'audio_message', 'type',
                  'data', 'gateway']

    def __init__(self, user, *args, **kwargs):
        super(SurveyQuestionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['question'].widget.attrs['class'] = 'span6'
        # To get user's audio file list
        self.fields['audio_message'].choices = get_audiofile_list(user)
        if instance.id:
            js_function = "question_form(" + str(instance.id) + ", 1);"
            self.fields['question'].widget.attrs['onBlur'] = js_function
            self.fields['audio_message'].widget.attrs['onChange'] = js_function
            self.fields['type'].widget.attrs['onChange'] = js_function + \
                            'toggle_gateway_field("' + str(instance.id) + '")'
            self.fields['data'].widget.attrs['onBlur'] = js_function
            self.fields['gateway'].widget.attrs['onChange'] = js_function


class SurveyQuestionNewForm(ModelForm):
    """SurveyQuestionNew ModelForm"""
    class Meta:
        model = SurveyQuestion
        fields = ['question', 'surveyapp', 'audio_message', 'type',
                  'data', 'gateway']

    def __init__(self, user, *args, **kwargs):
        super(SurveyQuestionNewForm, self).__init__(*args, **kwargs)
        self.fields['surveyapp'].widget = forms.HiddenInput()
        self.fields['question'].widget.attrs['class'] = 'span6'
        self.fields['audio_message'].choices = get_audiofile_list(user)
        js_function = "var initial_que_save=1;to_call_question_form();"
        self.fields['question'].widget.attrs['onBlur'] = js_function
        self.fields['audio_message'].widget.attrs['onChange'] = js_function
        self.fields['type'].widget.attrs['onChange'] = js_function
        self.fields['data'].widget.attrs['onBlur'] = js_function
        self.fields['gateway'].widget.attrs['onChange'] = js_function


class SurveyResponseForm(ModelForm):
    """SurveyResponse ModelForm"""

    class Meta:
        model = SurveyResponse
        fields = ['key', 'keyvalue', 'goto_surveyquestion']

    def __init__(self, user, *args, **kwargs):
        super(SurveyResponseForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['key'].widget.attrs['class'] = "input-small"
        self.fields['keyvalue'].widget.attrs['class'] = "input-small"
        self.fields['goto_surveyquestion'].choices = get_question_list(user)

        if instance.id:
            js_function = "response_form(" + str(instance.id) + ", " + \
                            str(instance.surveyquestion_id) + ", 1, 1);"
            self.fields['key'].widget.attrs['onBlur'] = js_function
            self.fields['keyvalue'].widget.attrs['onBlur'] = js_function
            self.fields['goto_surveyquestion'].widget\
                    .attrs['onBlur'] = js_function
            self.fields['goto_surveyquestion'].widget\
                .attrs['onfocus'] = \
                    'call_update_question("goto_'+ str(instance.id) + '");'


class SurveyReportForm(forms.Form):
    """Survey Report Form"""
    campaign = forms.ChoiceField(label=_('Campaign'), required=False)

    def __init__(self, user, *args, **kwargs):
        super(SurveyReportForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['campaign']
        # To get user's campaign list which are attached with survey app
        if user:
            list = []
            try:
                camp_list = Campaign.objects.filter(user=user,
                        content_type=ContentType.objects.get(name='survey'))
                pb_list = ((l.id, l.name) for l in camp_list)
                for i in pb_list:
                    list.append((i[0], i[1]))
            except:
                list.append((0, ''))
            self.fields['campaign'].choices = list


class SurveyCustomerAudioFileForm(CustomerAudioFileForm):

    def __init__(self, *args, **kwargs):
        super(SurveyCustomerAudioFileForm, self).__init__(*args, **kwargs)
        self.fields['audio_file'].widget.attrs['class'] = "input-file"
