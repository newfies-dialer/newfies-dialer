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
from dialer_campaign.models import Campaign
from dialer_contact.forms import SearchForm
from survey.models import Survey_template, Section_template, \
    Branching_template, Survey
from survey.constants import SECTION_TYPE
from audiofield.models import AudioFile


def get_audiofile_list(user):
    """Get audio file list for logged in user
    with default none option"""
    list_af = []
    list_af.append(('', '---'))
    af_list = AudioFile.objects.values_list('id', 'name').filter(user=user).order_by('-id')
    for i in af_list:
        list_af.append((i[0], i[1]))
    return list_af


def get_section_question_list(survey_id, section_id):
    """Get survey question list for logged in user
    with default none option"""
    section_branch_list = Branching_template\
        .objects.values_list('section_id', flat=True)\
        .filter(section_id=section_id)
    list_sq = []
    list_sq.append(('', _('hangup').capitalize()))

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

    list_sq.append(('any', _('any other key').capitalize()))
    list_sq.append(('invalid', _('invalid').capitalize()))
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

    list_sq.append(('any', _('any other key').capitalize()))
    list_sq.append(('invalid', _('invalid').capitalize()))
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

        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class PlayMessageSectionForm(ModelForm):
    """PlayMessageForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['type', 'survey', 'question', 'retries',
                  'audiofile', 'completed']

    def __init__(self, user, *args, **kwargs):
        super(PlayMessageSectionForm, self).__init__(*args, **kwargs)
        self.fields['survey'].widget = forms.HiddenInput()
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        if user:
            self.fields['audiofile'].choices = get_audiofile_list(user)


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
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


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
            self.fields['invalid_audiofile'].choices = self.fields['audiofile'].choices

        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        self.fields['rating_laps'].widget.attrs['maxlength'] = 3
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


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

        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class RecordMessageSectionForm(ModelForm):
    """RecordMessageSectionForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['type', 'survey', 'question', 'audiofile', 'completed']

    def __init__(self, user, *args, **kwargs):
        super(RecordMessageSectionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['audiofile'].choices = get_audiofile_list(user)

        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class ConferenceSectionForm(ModelForm):
    """ConferenceSectionForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['type', 'survey', 'question', 'audiofile', 'conference', 'completed']

    def __init__(self, user, *args, **kwargs):
        super(ConferenceSectionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['audiofile'].choices = get_audiofile_list(user)
        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class CallTransferSectionForm(ModelForm):
    """CallTransferSectionForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['type', 'survey', 'question', 'audiofile', 'phonenumber',
                  'completed']

    def __init__(self, user, *args, **kwargs):
        super(CallTransferSectionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['audiofile'].choices = get_audiofile_list(user)
        self.fields['survey'].widget = forms.HiddenInput()
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class SMSSectionForm(ModelForm):
    """SMSSectionForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['type', 'survey', 'question', 'retries',
                  'audiofile', 'completed', 'sms_text']
        widgets = {
            'sms_text': Textarea(attrs={'cols': 23, 'rows': 2}),
        }

    def __init__(self, user, *args, **kwargs):
        super(SMSSectionForm, self).__init__(*args, **kwargs)
        self.fields['survey'].widget = forms.HiddenInput()
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        self.fields['type'].widget.attrs['onchange'] = 'this.form.submit();'
        if user:
            self.fields['audiofile'].choices = get_audiofile_list(user)


class ScriptForm(ModelForm):
    """ScriptForm ModelForm"""

    class Meta:
        model = Section_template
        fields = ['script']

    def __init__(self, *args, **kwargs):
        super(ScriptForm, self).__init__(*args, **kwargs)
        self.fields['script'].widget.attrs['class'] = "form-control"


class BranchingForm(ModelForm):
    """BranchingForm ModelForm"""

    class Meta:
        model = Branching_template
        fields = ['keys', 'section', 'goto']

    def __init__(self, survey_id, section_id, *args, **kwargs):
        super(BranchingForm, self).__init__(*args, **kwargs)
        #instance = getattr(self, 'instance', None)
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

        if (obj_section.type == SECTION_TYPE.PLAY_MESSAGE
           or obj_section.type == SECTION_TYPE.RECORD_MSG
           or obj_section.type == SECTION_TYPE.CALL_TRANSFER
           or obj_section.type == SECTION_TYPE.CONFERENCE
           or obj_section.type == SECTION_TYPE.SMS):
            self.fields['keys'].initial = 0
            self.fields['keys'].widget = forms.HiddenInput()

        self.fields['goto'].choices = \
            get_section_question_list(survey_id, section_id)

        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class SurveyReportForm(forms.Form):
    """Survey Report Form"""
    campaign = forms.ChoiceField(label=_('campaign'), required=False)

    def __init__(self, user, *args, **kwargs):
        super(SurveyReportForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['campaign']
        # To get user's campaign list which are attached with survey
        if user:
            camp_list = []
            camp_list.append((0, _('select campaign').title()))
            try:
                if user.is_superuser:
                    campaign_list = Campaign.objects.values_list('id', 'name')\
                        .filter(content_type__model='survey', has_been_started=True).order_by('-id')
                else:
                    campaign_list = Campaign.objects.values_list('id', 'name')\
                        .filter(user=user, content_type__model='survey', has_been_started=True).order_by('-id')
                for i in campaign_list:
                    camp_list.append((i[0], i[1]))
            except:
                pass
            self.fields['campaign'].choices = camp_list


class SurveyDetailReportForm(SearchForm):

    survey_id = forms.ChoiceField(label=_('survey'), required=False)

    def __init__(self, user, *args, **kwargs):
        super(SurveyDetailReportForm, self).__init__(*args, **kwargs)
        change_field_list = ['survey_id', 'from_date', 'to_date']
        for i in change_field_list:
            self.fields[i].widget.attrs['class'] = "form-control"

        self.fields.keyOrder = change_field_list
        if user:
            survey_list = []
            survey_list.append((0, _('select survey').title()))
            if user.is_superuser:
                survey_objs = Survey.objects.values_list('id', 'name', 'campaign__name').all().order_by('-id')
            else:
                survey_objs = Survey.objects.values_list('id', 'name', 'campaign__name')\
                    .filter(user=user).order_by('-id')

            for i in survey_objs:
                if i[2]:
                    survey_name = i[1] + " : " + i[2]
                else:
                    survey_name = i[1]
                survey_list.append((i[0], survey_name))
            self.fields['survey_id'].choices = survey_list


class SurveyFileImport(forms.Form):
    """General Form : file upload"""
    name = forms.CharField(label=_('survey name'), required=True)
    survey_file = forms.FileField(label=_("upload File"), required=True,
                                  error_messages={'required': 'please upload File'},
                                  help_text=_("browse text file"))

    def __init__(self, *args, **kwargs):
        super(SurveyFileImport, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"

    def clean_csv_file(self):
        """Form Validation :  File extension Check"""
        filename = self.cleaned_data["survey_file"]
        file_exts = ["txt"]
        if str(filename).split(".")[1].lower() in file_exts:
            return filename
        else:
            raise forms.ValidationError(_(u'document types accepted: %s' %
                                          ' '.join(file_exts)))


class SealSurveyForm(SurveyFileImport):
    """General Form : SealSurveyForm"""
    def __init__(self, *args, **kwargs):
        super(SealSurveyForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['name']
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
