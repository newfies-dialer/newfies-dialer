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
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from survey.models import SurveyApp, SurveyQuestion, \
                          SurveyResponse, APP_TYPE
from survey.function_def import field_list
from dialer_campaign.models import Campaign
from dialer_cdr.forms import VoipSearchForm


def get_audiofile_list(user):
    """Get audio file list for logged in user
    with default none option"""
    list_af = []
    list_af.append(('', '---'))
    af_list = field_list(name="audiofile", user=user)
    for i in af_list:
        list_af.append((i[0], i[1]))
    return list_af


def get_question_list(user, surveyapp_id):
    """Get survey question list for logged in user
    with default none option"""
    list_sq = []
    list_sq.append(('', '---'))

    list = SurveyQuestion.objects.filter(user=user,
        surveyapp_id=surveyapp_id)
    for i in list:
        list_sq.append((i.id, i.question))

    return list_sq


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
        self.fields['description'].widget = forms.TextInput()
        self.fields['description'].widget.attrs['class'] = 'span4'


class SurveyQuestionForm(ModelForm):
    """SurveyQuestion ModelForm"""

    class Meta:
        model = SurveyQuestion
        fields = ['question', 'surveyapp', 'audio_message', 'type']
        # remove those fields for now 'data', 'gateway'

    def __init__(self, user, *args, **kwargs):
        super(SurveyQuestionForm, self).__init__(*args, **kwargs)
        self.fields['question'].widget.attrs['class'] = 'span5'
        self.fields['surveyapp'].widget = forms.HiddenInput()
        self.fields['audio_message'].choices = get_audiofile_list(user)
        self.fields['audio_message'].widget.attrs['class'] = 'span2'
        self.fields['type'].choices = APP_TYPE
        self.fields['type'].widget.attrs['class'] = 'span2'
        #self.fields['gateway'].widget.attrs['class'] = 'span2'


class SurveyResponseForm(ModelForm):
    """SurveyResponse ModelForm"""

    class Meta:
        model = SurveyResponse
        fields = ['key', 'keyvalue', 'surveyquestion', 'goto_surveyquestion']

    def __init__(self, user, surveyapp_id, *args, **kwargs):
        super(SurveyResponseForm, self).__init__(*args, **kwargs)
        self.fields['surveyquestion'].widget = forms.HiddenInput()
        self.fields['key'].widget.attrs['class'] = "input-small"
        self.fields['keyvalue'].widget.attrs['class'] = "input-small"
        self.fields['goto_surveyquestion'].choices = get_question_list(user,
                                                            surveyapp_id)
        self.fields['goto_surveyquestion'].label = _('Goto')


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


class SurveyDetailReportForm(VoipSearchForm, SurveyReportForm):

    def __init__(self, user, *args, **kwargs):
        super(SurveyDetailReportForm, self).__init__(user, *args, **kwargs)
        self.fields.keyOrder = ['from_date', 'to_date', 'campaign']
