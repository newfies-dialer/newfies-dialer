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
from survey2.models import Survey, Section
from dialer_campaign.models import Campaign
from dialer_cdr.forms import VoipSearchForm
from audiofield.models import AudioFile


def get_audiofile_list(user):
    """Get audio file list for logged in user
    with default none option"""
    list_af = []
    list_af.append(('', '---'))
    list = AudioFile.objects.filter(user=user)
    af_list = ((l.id, l.name) for l in list)
    for i in af_list:
        list_af.append((i[0], i[1]))
    return list_af


def get_question_list(user, survey_id):
    """Get survey question list for logged in user
    with default none option"""
    list_sq = []
    list_sq.append(('', '---'))

    list = Section.objects.filter(user=user,
        survey_id=survey_id)
    for i in list:
        list_sq.append((i.id, i.question))

    return list_sq


class SurveyForm(ModelForm):
    """SurveyApp ModelForm"""

    class Meta:
        model = Survey
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance.id:
            self.fields.keyOrder = ['name', 'description']
        self.fields['description'].widget = forms.TextInput()
        self.fields['description'].widget.attrs['class'] = 'span4'


class VoiceSectionForm(ModelForm):
    """VoiceSectionForm ModelForm"""

    class Meta:
        model = Section
        fields = ['type', 'survey', 'phrasing']

    def __init__(self, user, *args, **kwargs):
        super(VoiceSectionForm, self).__init__(*args, **kwargs)
        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['phrasing'].widget = forms.Textarea()
        self.fields['phrasing'].widget.attrs['class'] = 'span5'


class MultipleChoiceSectionForm(ModelForm):
    """MultipleChoiceSectionForm ModelForm"""

    class Meta:
        model = Section
        fields = ['type', 'survey', 'question',
                  'key_0', 'key_1', 'key_2', 'key_3', 'key_4',
                  'key_5', 'key_6', 'key_7', 'key_8', 'key_9',
                  'audiofile']

    def __init__(self, user, *args, **kwargs):
        super(MultipleChoiceSectionForm, self).__init__(*args, **kwargs)
        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['question'].widget.attrs['class'] = 'span5'


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
        self.fields.keyOrder = [ 'campaign', 'from_date', 'to_date']
