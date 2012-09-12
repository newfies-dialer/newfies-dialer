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
from survey2.models import Survey, Section, Branching
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


def get_section_question_list(user, survey_id, section_id):
    """Get survey question list for logged in user
    with default none option"""
    section_branch_list = \
        Branching.objects.values_list('section_id', flat=True)\
                         .filter(section_id=section_id)
    list_sq = []
    list_sq.append(('', _('Hang up')))

    list = Section.objects.filter(user=user, survey_id=survey_id)\
            .exclude(pk=section_id)\
            .exclude(id__in=section_branch_list)
    for i in list:
        if i.question:
            q_string = i.question
        else:
            q_string = i.phrasing
        list_sq.append((i.id, "Goto# " + q_string))

    return list_sq


def get_question_choice_list(section_id):
    """Get survey question list for logged in user
    with default none option"""
    keys_list = Branching.objects\
                        .values_list('keys', flat=True)\
                        .filter(section_id=int(section_id))
    list_sq = []
    obj_section = Section.objects.get(id=int(section_id))

    if keys_list:
        keys_list = [int(integral) for integral in keys_list]

    if obj_section.key_0 and 0 not in keys_list:
        list_sq.append((0, obj_section.key_0))
    if obj_section.key_1 and 1 not in keys_list:
        list_sq.append((1, obj_section.key_1))
    if obj_section.key_2 and 2 not in keys_list:
        list_sq.append((2, obj_section.key_2))
    if obj_section.key_3 and 3 not in keys_list:
        list_sq.append((3, obj_section.key_3))
    if obj_section.key_4 and 4 not in keys_list:
        list_sq.append((4, obj_section.key_4))
    if obj_section.key_5 and 5 not in keys_list:
        list_sq.append((5, obj_section.key_5))
    if obj_section.key_6 and 6 not in keys_list:
        list_sq.append((6, obj_section.key_6))
    if obj_section.key_7 and 7 not in keys_list:
        list_sq.append((7, obj_section.key_7))
    if obj_section.key_8 and 8 not in keys_list:
        list_sq.append((8, obj_section.key_8))
    if obj_section.key_9 and 9 not in keys_list:
        list_sq.append((9, obj_section.key_9))
    list_sq.append(('', _('Anything')))
    return list_sq


def get_rating_choice_list(section_id):
    """Get survey rating laps for logged in user
    with default anything option"""
    keys_list = Branching.objects\
                .values_list('keys', flat=True)\
                .filter(section_id=int(section_id))

    obj_section = Section.objects.get(id=int(section_id))

    if keys_list:
        keys_list = [int(integral) for integral in keys_list]

    list_sq = []
    for i in range(1, int(obj_section.rating_laps) + 1):
        if i not in keys_list:
            list_sq.append((i, i))

    list_sq.append(('', _('Anything')))

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
        fields = ['type', 'survey', 'phrasing', 'retries', 'audiofile']

    def __init__(self, user, *args, **kwargs):
        super(VoiceSectionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['phrasing'].widget = forms.Textarea()
        self.fields['phrasing'].widget.attrs['class'] = 'span5'
        self.fields['retries'].widget.attrs['class'] = 'span1'
        if instance.id and user:
            self.fields['audiofile'].choices = get_audiofile_list(user)
            self.fields['audiofile'].widget.attrs['class'] = 'span2'


class MultipleChoiceSectionForm(ModelForm):
    """MultipleChoiceSectionForm ModelForm"""

    class Meta:
        model = Section
        fields = ['type', 'survey', 'question', 'retries',
                  'key_0', 'key_1', 'key_2', 'key_3', 'key_4',
                  'key_5', 'key_6', 'key_7', 'key_8', 'key_9',
                  'phrasing', 'timeout', 'audiofile', 'invalid_audiofile']

    def __init__(self, user, *args, **kwargs):
        super(MultipleChoiceSectionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if user:
            self.fields['invalid_audiofile'].choices = get_audiofile_list(user)
        if instance.id:
            self.fields['phrasing'].widget = forms.Textarea()
            self.fields['phrasing'].widget.attrs['class'] = 'span5'
            self.fields['audiofile'].choices = get_audiofile_list(user)
            self.fields['audiofile'].widget.attrs['class'] = 'span2'

        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['question'].widget.attrs['class'] = 'span5'
        self.fields['retries'].widget.attrs['class'] = 'span1'
        self.fields['timeout'].widget.attrs['class'] = 'span1'

        for i in range(0, 10):
            self.fields['key_' + str(i)].widget.attrs['class'] = 'span1'


class RatingSectionForm(ModelForm):
    """RatingSectionForm ModelForm"""

    class Meta:
        model = Section
        fields = ['type', 'survey', 'question', 'rating_laps', 'phrasing',
                  'retries', 'timeout', 'audiofile', 'invalid_audiofile']

    def __init__(self, user, *args, **kwargs):
        super(RatingSectionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if user:
            self.fields['invalid_audiofile'].choices = get_audiofile_list(user)

        if instance.id:
            self.fields['phrasing'].widget = forms.Textarea()
            self.fields['phrasing'].widget.attrs['class'] = 'span5'
            self.fields['audiofile'].choices = get_audiofile_list(user)
            self.fields['audiofile'].widget.attrs['class'] = 'span2'

        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['question'].widget = forms.Textarea()
        self.fields['question'].widget.attrs['class'] = 'span5'
        self.fields['retries'].widget.attrs['class'] = 'span1'
        self.fields['timeout'].widget.attrs['class'] = 'span1'


class EnterNumberSectionForm(ModelForm):
    """EnterNumberSectionForm ModelForm"""

    class Meta:
        model = Section
        fields = ['type', 'survey', 'question', 'validate_number',
                  'number_digits', 'min_number', 'max_number', 'phrasing',
                  'retries', 'timeout', 'audiofile', 'invalid_audiofile']

    def __init__(self, user, *args, **kwargs):
        super(EnterNumberSectionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if user:
            self.fields['invalid_audiofile'].choices = get_audiofile_list(user)

        if instance.id:
            self.fields['phrasing'].widget = forms.Textarea()
            self.fields['phrasing'].widget.attrs['class'] = 'span5'
            self.fields['audiofile'].choices = get_audiofile_list(user)
            self.fields['audiofile'].widget.attrs['class'] = 'span2'
        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['question'].widget = forms.Textarea()
        self.fields['question'].widget.attrs['class'] = 'span5'
        self.fields['validate_number'].widget.attrs['class'] = 'span2'
        self.fields['number_digits'].widget.attrs['class'] = 'span1'
        self.fields['min_number'].widget.attrs['class'] = 'span1'
        self.fields['max_number'].widget.attrs['class'] = 'span1'
        self.fields['retries'].widget.attrs['class'] = 'span1'
        self.fields['timeout'].widget.attrs['class'] = 'span1'


class RecordMessageSectionForm(ModelForm):
    """RecordMessageSectionForm ModelForm"""

    class Meta:
        model = Section
        fields = ['type', 'survey', 'phrasing', 'continue_survey']

    def __init__(self, user, *args, **kwargs):
        super(RecordMessageSectionForm, self).__init__(*args, **kwargs)
        #instance = getattr(self, 'instance', None)

        self.fields['phrasing'].widget = forms.Textarea()
        self.fields['phrasing'].widget.attrs['class'] = 'span5'
        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'


class PatchThroughSectionForm(ModelForm):
    """PatchThroughSectionForm ModelForm"""

    class Meta:
        model = Section
        fields = ['type', 'survey', 'phrasing', 'dial_phonenumber',
                  'continue_survey']

    def __init__(self, user, *args, **kwargs):
        super(PatchThroughSectionForm, self).__init__(*args, **kwargs)
        #instance = getattr(self, 'instance', None)

        self.fields['phrasing'].widget = forms.Textarea()
        self.fields['phrasing'].widget.attrs['class'] = 'span5'
        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'


class BranchingForm(ModelForm):
    """BranchingForm ModelForm"""

    class Meta:
        model = Branching
        fields = ['keys', 'section', 'goto']

    def __init__(self, user, survey_id, section_id, *args, **kwargs):
        super(BranchingForm, self).__init__(*args, **kwargs)
        self.fields['keys'].widget.attrs['class'] = 'span2'
        self.fields['section'].widget = forms.HiddenInput()

        # multiple choice section
        obj_section = Section.objects.get(id=section_id)
        if obj_section.type == 2:
            self.fields['keys'] = \
                forms.ChoiceField(choices=get_question_choice_list(section_id))

        # rating section
        if obj_section.type == 3:
            self.fields['keys'] =\
                forms.ChoiceField(choices=get_rating_choice_list(section_id))

        self.fields['goto'].choices = \
            get_section_question_list(user, survey_id, section_id)


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
