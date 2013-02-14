#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from dialer_campaign.models import Campaign
from dialer_cdr.forms import VoipSearchForm
from survey.models import Survey_template, Section_template, \
    Branching_template
from survey.constants import SECTION_TYPE
from audiofield.models import AudioFile


def get_audiofile_list(user):
    """Get audio file list for logged in user
    with default none option"""
    list_af = []
    list_af.append(('', '---'))
    list = AudioFile.objects.values_list('id', 'name')\
        .filter(user=user)\
        .order_by('id')
    for i in list:
        list_af.append((i[0], i[1]))
    return list_af


def get_section_question_list(survey_id, section_id):
    """Get survey question list for logged in user
    with default none option"""
    section_branch_list = Branching_template\
        .objects.values_list('section_id', flat=True)\
        .filter(section_id=section_id)
    list_sq = []
    list_sq.append(('', _('Hang up')))

    list = Section_template.objects.filter(survey_id=survey_id)\
        .exclude(pk=section_id)\
        .exclude(id__in=section_branch_list)
    for i in list:
        if i.question:
            q_string = i.question
        else:
            q_string = i.script
        list_sq.append((i.id, "Goto: %s" % (q_string)))

    return list_sq


def get_multi_question_choice_list(section_id):
    """
    Get survey question list for the user with a default none option
    """
    keys_list = Branching_template.objects\
        .values_list('keys', flat=True)\
        .filter(section_id=int(section_id))\
        .exclude(keys='')
    list_sq = []
    obj_section = Section_template.objects.get(id=int(section_id))

    if keys_list:
        keys_list = [integral for integral in keys_list]

    for i in range(0, 10):
        if (obj_section.__dict__['key_' + str(i)]
           and i not in keys_list):
            list_sq.append((i, '%s' % (obj_section.__dict__['key_' + str(i)])))

    list_sq.append(('any', _('Any Other Key')))
    list_sq.append(('invalid', _('Invalid')))
    return list_sq


def get_rating_choice_list(section_id):
    """
    Get survey rating laps for logged in user
    with default any other key option
    """
    keys_list = Branching_template.objects\
        .values_list('keys', flat=True)\
        .filter(section_id=int(section_id))\
        .exclude(keys='')

    obj_section = Section_template.objects.get(id=int(section_id))

    if keys_list:
        keys_list = [integral for integral in keys_list]

    list_sq = []
    if obj_section.rating_laps:
        for i in range(1, int(obj_section.rating_laps) + 1):
            if i not in keys_list:
                list_sq.append((i, '%s' % (str(i))))

    list_sq.append(('any', _('Any Other Key')))
    list_sq.append(('invalid', _('Invalid')))
    return list_sq


class SurveyForm(ModelForm):
    """Survey ModelForm"""

    class Meta:
        model = Survey_template
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['name', 'tts_language', 'description']
        self.fields['description'].widget = forms.TextInput()
        self.fields['description'].widget.attrs['class'] = 'span3'


class PlayMessageSectionForm(ModelForm):
    """PlayMessageForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['type', 'survey', 'question', 'retries',
                  'audiofile', 'completed']

    def __init__(self, user, *args, **kwargs):
        super(PlayMessageSectionForm, self).__init__(*args, **kwargs)
        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['question'].widget.attrs['class'] = 'span3'
        self.fields['retries'].widget.attrs['class'] = 'span1'
        if user:
            self.fields['audiofile'].choices = get_audiofile_list(user)
            self.fields['audiofile'].widget.attrs['class'] = 'span2'


class MultipleChoiceSectionForm(ModelForm):
    """MultipleChoiceSectionForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['type', 'survey', 'question', 'retries',
                  'key_0', 'key_1', 'key_2', 'key_3', 'key_4',
                  'key_5', 'key_6', 'key_7', 'key_8', 'key_9',
                  'timeout', 'audiofile', 'invalid_audiofile',
                  'completed']

    def __init__(self, user, *args, **kwargs):
        super(MultipleChoiceSectionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['audiofile'].choices = get_audiofile_list(user)
            self.fields['audiofile'].widget.attrs['class'] = 'span2'
            self.fields['invalid_audiofile'].choices = self.fields['audiofile'].choices
            self.fields['invalid_audiofile'].widget.attrs['class'] = 'span2'

        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['question'].widget.attrs['class'] = 'span3'
        self.fields['retries'].widget.attrs['class'] = 'span1'
        self.fields['timeout'].widget.attrs['class'] = 'span1'

        for i in range(0, 10):
            self.fields['key_' + str(i)].widget.attrs['class'] = 'span1'


class RatingSectionForm(ModelForm):
    """RatingSectionForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['type', 'survey', 'question', 'rating_laps',
                  'retries', 'timeout', 'audiofile', 'invalid_audiofile',
                  'completed']

    def __init__(self, user, *args, **kwargs):
        super(RatingSectionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['audiofile'].choices = get_audiofile_list(user)
            self.fields['audiofile'].widget.attrs['class'] = 'span2'
            self.fields['invalid_audiofile'].choices = self.fields['audiofile'].choices
            self.fields['invalid_audiofile'].widget.attrs['class'] = 'span2'

        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['question'].widget.attrs['class'] = 'span3'
        self.fields['retries'].widget.attrs['class'] = 'span1'
        self.fields['timeout'].widget.attrs['class'] = 'span1'
        self.fields['rating_laps'].widget.attrs['class'] = 'span1'
        self.fields['rating_laps'].widget.attrs['maxlength'] = 3


class CaptureDigitsSectionForm(ModelForm):
    """CaptureDigitsSectionForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['type', 'survey', 'question', 'validate_number',
                  'number_digits', 'min_number', 'max_number',
                  'retries', 'timeout', 'audiofile', 'invalid_audiofile',
                  'completed']

    def __init__(self, user, *args, **kwargs):
        super(CaptureDigitsSectionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['audiofile'].choices = get_audiofile_list(user)
            self.fields['audiofile'].widget.attrs['class'] = 'span2'

        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['question'].widget.attrs['class'] = 'span3'
        self.fields['number_digits'].widget.attrs['class'] = 'span1'
        self.fields['min_number'].widget.attrs['class'] = 'span1'
        self.fields['max_number'].widget.attrs['class'] = 'span1'
        self.fields['retries'].widget.attrs['class'] = 'span1'
        self.fields['timeout'].widget.attrs['class'] = 'span1'


class RecordMessageSectionForm(ModelForm):
    """RecordMessageSectionForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['type', 'survey', 'question', 'audiofile', 'completed']

    def __init__(self, user, *args, **kwargs):
        super(RecordMessageSectionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['audiofile'].choices = get_audiofile_list(user)
            self.fields['audiofile'].widget.attrs['class'] = 'span2'
        self.fields['question'].widget.attrs['class'] = 'span3'
        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'


class CallTransferSectionForm(ModelForm):
    """CallTransferSectionForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['type', 'survey', 'question', 'phonenumber', 'completed']

    def __init__(self, user, *args, **kwargs):
        super(CallTransferSectionForm, self).__init__(*args, **kwargs)
        self.fields['question'].widget.attrs['class'] = 'span3'
        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'


class ScriptForm(ModelForm):
    """ScriptForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['script']

    def __init__(self, *args, **kwargs):
        super(ScriptForm, self).__init__(*args, **kwargs)
        self.fields['script'].widget = forms.Textarea()
        self.fields['script'].widget.attrs['class'] = 'span4'


class BranchingForm(ModelForm):
    """BranchingForm ModelForm"""

    class Meta:
        model = Branching_template
        fields = ['keys', 'section', 'goto']

    def __init__(self, survey_id, section_id, *args, **kwargs):
        super(BranchingForm, self).__init__(*args, **kwargs)
        #instance = getattr(self, 'instance', None)
        self.fields['keys'].widget.attrs['class'] = 'span2'
        self.fields['section'].widget = forms.HiddenInput()

        # multiple choice section
        obj_section = Section_template.objects.get(id=section_id)

        if obj_section.type == SECTION_TYPE.MULTI_CHOICE:
            self.fields['keys'] = forms.ChoiceField(
                choices=get_multi_question_choice_list(section_id),
                required=False)

        # rating section
        if obj_section.type == SECTION_TYPE.RATING_SECTION:
            self.fields['keys'] = forms.ChoiceField(
                choices=get_rating_choice_list(section_id),
                required=False)

        # voice & record section
        if (obj_section.type == SECTION_TYPE.PLAY_MESSAGE
           or obj_section.type == SECTION_TYPE.RECORD_MSG):
            self.fields['keys'].initial = 0
            self.fields['keys'].widget = forms.HiddenInput()

        self.fields['goto'].choices = \
            get_section_question_list(survey_id, section_id)


class SurveyReportForm(forms.Form):
    """Survey Report Form"""
    campaign = forms.ChoiceField(label=_('Campaign'), required=False)

    def __init__(self, user, *args, **kwargs):
        super(SurveyReportForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['campaign']
        # To get user's campaign list which are attached with survey
        if user:
            list = []
            try:
                camp_list = Campaign.objects.values_list('id', 'name')\
                    .filter(user=user, content_type__model='survey')
                for i in camp_list:
                    list.append((i[0], i[1]))
            except:
                list.append((0, ''))
            self.fields['campaign'].choices = list


class SurveyDetailReportForm(VoipSearchForm, SurveyReportForm):

    def __init__(self, user, *args, **kwargs):
        super(SurveyDetailReportForm, self).__init__(user, *args, **kwargs)
        self.fields.keyOrder = ['campaign', 'from_date', 'to_date']


class SurveyFileImport(forms.Form):
    """General Form : file upload"""
    name = forms.CharField(label=_('Survey name'), required=True)
    survey_file = forms.FileField(label=_("Upload File "), required=True,
        error_messages={'required': 'Please upload File'},
        help_text=_("Browse text file"))

    def clean_csv_file(self):
        """Form Validation :  File extension Check"""
        filename = self.cleaned_data["survey_file"]
        file_exts = ["txt"]
        if str(filename).split(".")[1].lower() in file_exts:
            return filename
        else:
            raise forms.ValidationError(_(u'Document types accepted: %s' %
                                          ' '.join(file_exts)))
