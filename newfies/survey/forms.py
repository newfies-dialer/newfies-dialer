from django.contrib.auth.models import User
from django import forms
from django.forms.util import ErrorList
from django.forms import *
from django.contrib import *
from django.contrib.admin.widgets import *
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory
from bootstrap.forms import BootstrapForm, BootstrapModelForm, Fieldset
from survey.models import *
from dialer_campaign.function_def import field_list
from audiofield.models import AudioFile
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


class SurveyQuestionForm(ModelForm):
    """SurveyQuestion ModelForm"""

    class Meta:
        model = SurveyQuestion
        fields = ['question', 'audio_message', 'message_type']
    
    def __init__(self, *args, **kwargs):
        super(SurveyQuestionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['question'].widget.attrs['style'] = 'width:350px;'
        if instance.id:
            js_function = "question_form(" + str(instance.id) + ", 1);"
            self.fields['question'].widget.attrs['onBlur'] = js_function
            self.fields['audio_message'].widget.attrs['onChange'] = js_function
            self.fields['message_type'].widget.attrs['onChange'] = js_function

        
class SurveyQuestionNewForm(ModelForm):
    """SurveyQuestionNew ModelForm"""
    class Meta:
        model = SurveyQuestion
        fields = ['question', 'surveyapp', 'audio_message', 'message_type']
        
    def __init__(self, user, *args, **kwargs):
        super(SurveyQuestionNewForm, self).__init__(*args, **kwargs)
        self.fields['surveyapp'].widget = forms.HiddenInput()
        self.fields['question'].widget.attrs['style'] = 'width:350px;'
        js_function = "var initial_que_save=1;to_call_question_form();"
        self.fields['question'].widget.attrs['onBlur'] = js_function
        self.fields['audio_message'].widget.attrs['onChange'] = js_function
        self.fields['message_type'].widget.attrs['onChange'] = js_function


class SurveyResponseForm(ModelForm):
    """SurveyResponse ModelForm"""

    class Meta:
        model = SurveyResponse
        fields = ['key', 'keyvalue']

    def __init__(self, *args, **kwargs):
        super(SurveyResponseForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        
        if instance.id:
            self.fields['key'].widget.attrs['onBlur'] = "response_form(" + str(instance.id) + ", " + str(instance.surveyquestion_id) + ", 1, 1);"
            self.fields['keyvalue'].widget.attrs['onBlur'] = "response_form(" + str(instance.id) + ", " + str(instance.surveyquestion_id) + ", 1, 1);"


class SurveyReportForm(forms.Form):
    """Survey Report Form"""
    campaign = forms.ChoiceField(label=_('Campaign'), required=False)

    def __init__(self, user, *args, **kwargs):
        super(SurveyReportForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['campaign']
         # To get user's running campaign list
        if user:
            list = []
            #list.append((0, '---'))
            pb_list = field_list("campaign", user)
            for i in pb_list:
                list.append((i[0], i[1]))
            self.fields['campaign'].choices = list

            
class NewfiesCustomerAudioFileForm(CustomerAudioFileForm, BootstrapModelForm):
    class Meta:
        model = AudioFile
        layout = (
            Fieldset("Audio File", 'name', 'audio_file'),
        )
