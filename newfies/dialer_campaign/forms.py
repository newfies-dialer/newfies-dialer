#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django import forms
from django.conf import settings
from django.forms.util import ErrorList
from django.forms import ModelForm, Textarea
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, Field, HTML
from crispy_forms.bootstrap import TabHolder, Tab
from django_lets_go.common_functions import get_unique_code
from bootstrap3_datetime.widgets import DateTimePicker
from mod_utils.forms import common_submit_buttons

from .models import Campaign, Subscriber
from .constants import CAMPAIGN_STATUS, SUBSCRIBER_STATUS
from .function_def import user_dialer_setting, get_phonebook_list
from dialer_contact.forms import SearchForm
# from agent.function_def import agent_list
# from agent.models import AgentProfile, Agent
from user_profile.models import UserProfile
from dnc.models import DNC


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

    """
    Campaign ModelForm
    """
    campaign_code = forms.CharField(widget=forms.HiddenInput)
    content_object = forms.ChoiceField(label=_("Application"))
    selected_phonebook = forms.CharField(widget=forms.HiddenInput, required=False)
    selected_content_object = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Campaign
        exclude = ['user', 'status', 'content_type', 'object_id', 'has_been_started', 'has_been_duplicated',
                   'created_date', 'totalcontact', 'imported_phonebook', 'completed', 'stoppeddate']
        # fields = ['campaign_code', 'name',
        #           'callerid', 'caller_name', 'aleg_gateway', 'sms_gateway',
        #           'content_object',  # 'content_type', 'object_id'
        #           'extra_data', 'dnc', 'description', 'phonebook',
        #           'frequency', 'callmaxduration', 'maxretry',
        #           'intervalretry', 'calltimeout',
        #           'completion_maxretry', 'completion_intervalretry',
        #           'startingdate', 'expirationdate',
        #           'daily_start_time', 'daily_stop_time',
        #           'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
        #           'saturday', 'sunday',
        #           'selected_phonebook', 'selected_content_object',
        #           'voicemail', 'amd_behavior', 'voicemail_audiofile',
        #           #'agent_script', 'lead_disposition', 'external_link'
        #           ]
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
                Tab(_('General'),
                    Div(
                        Div(Fieldset(_('General Settings')), css_class='col-md-12'),
                        Div('name', css_class=css_class),
                        Div('callerid', css_class=css_class),
                        Div('caller_name', css_class=css_class),
                        Div('content_object', css_class=css_class),
                        css_class='row'
                ),
                    Div(
                        Div('extra_data', css_class=css_class),
                        Div('dnc', css_class=css_class),
                        Div('description', css_class=css_class),
                        Div('phonebook', css_class=css_class),
                        css_class='row'
                ),
                    form_action,
                    css_class='well'
                ),
                Tab('Dialer',
                    Div(
                        Div(Fieldset(_('Dialer Settings')), css_class='col-md-12'),
                        Div('aleg_gateway', css_class=css_class),
                        Div('frequency', css_class=css_class),
                        Div('callmaxduration', css_class=css_class),
                        Div('maxretry', css_class=css_class),
                        Div('intervalretry', css_class=css_class),
                        Div('calltimeout', css_class=css_class),
                        Div(Fieldset(_('Dialer Completion Settings')), css_class='col-md-12'),
                        Div('completion_maxretry', css_class=css_class),
                        Div('completion_intervalretry', css_class=css_class),
                        Div('sms_gateway', css_class=css_class),
                        css_class='row'
                    ),
                    form_action,
                    css_class='well'
                    ),
                Tab('schedule',
                    Div(
                        Div(Fieldset(_('Schedule Settings')), css_class='col-md-12'),
                        Div(HTML("""<label>%s<label>""" % (_('Week Days'))), css_class="col-md-3"),
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

        if settings.AMD:
            amd_layot = Tab(_('Voicemail'),
                            Div(
                                Div(Fieldset(_('Voicemail Settings')), css_class='col-md-12'),
                                Div(HTML("""
                                    <div class="btn-group" data-toggle="buttons">
                                        <label for="{{ form.voicemail.auto_id }}">{{ form.voicemail.label }}</label>
                                        <br/>
                                        <div class="make-switch switch-small">
                                        {{ form.voicemail }}
                                        </div>
                                    </div>
                                    """), css_class='col-md-12 col-xs-10'),
                                HTML("""<div>&nbsp;</div>"""),
                                Div('amd_behavior', css_class=css_class),
                                Div('voicemail_audiofile', css_class=css_class),
                                css_class='row'
            ),
                form_action,
                css_class='well'
            )
            self.helper.layout[1].insert(2, amd_layot)
        # hidden var
        self.helper.layout.append(Field('selected_phonebook'))
        self.helper.layout.append(Field('selected_content_object'))

        instance = getattr(self, 'instance', None)
        self.fields['campaign_code'].initial = get_unique_code(length=5)

        if user:
            list_gw = []
            dnc_list = []
            phonebook_list = get_phonebook_list(user)
            if not phonebook_list:
                phonebook_list = []
                phonebook_list.append(('', '---'))

            self.fields['phonebook'].choices = phonebook_list
            self.fields['phonebook'].initial = str(phonebook_list[0][0])

            gateway_list = UserProfile.objects.get(user=user).userprofile_gateway.all()
            gw_list = ((l.id, l.name) for l in gateway_list)

            dnc_list.append(('', '---'))
            dnc_obj_list = DNC.objects.values_list('id', 'name').filter(user=user).order_by('id')
            for l in dnc_obj_list:
                dnc_list.append((l[0], l[1]))
            self.fields['dnc'].choices = dnc_list

            for i in gw_list:
                list_gw.append((i[0], i[1]))
            self.fields['aleg_gateway'].choices = UserProfile.objects.get(user=user)\
                .userprofile_gateway.all().values_list('id', 'name')

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

        # If campaign is running or has been started
        if instance.status == CAMPAIGN_STATUS.START or instance.has_been_started:
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['caller_name'].widget.attrs['readonly'] = True
            self.fields['callerid'].widget.attrs['readonly'] = True
            self.fields['extra_data'].widget.attrs['readonly'] = True
            self.fields['phonebook'].widget.attrs['readonly'] = True
            self.fields['lead_disposition'].widget.attrs['readonly'] = True
            self.fields['dnc'].widget.attrs['readonly'] = True
            self.fields['aleg_gateway'].widget.attrs['readonly'] = True
            self.fields['sms_gateway'].widget.attrs['readonly'] = True
            self.fields['voicemail'].widget.attrs['readonly'] = True
            self.fields['amd_behavior'].widget.attrs['readonly'] = True
            self.fields['voicemail_audiofile'].widget.attrs['readonly'] = True

            selected_phonebook = ''
            if instance.phonebook.all():
                selected_phonebook = ",".join(["%s" % (i.id) for i in instance.phonebook.all()])
            self.fields['selected_phonebook'].initial = selected_phonebook

            self.fields['content_object'].widget.attrs['disabled'] = 'disabled'
            self.fields['content_object'].required = False
            self.fields['selected_content_object'].initial = "type:%s-id:%s" % \
                (instance.content_type.id, instance.object_id)

    def clean(self):
        cleaned_data = self.cleaned_data
        frequency = cleaned_data.get('frequency')
        callmaxduration = cleaned_data.get('callmaxduration')
        maxretry = cleaned_data.get('maxretry')
        calltimeout = cleaned_data.get('calltimeout')
        phonebook = cleaned_data.get('phonebook')

        if not phonebook:
            msg = _('you must select at least one phonebook')
            self._errors['phonebook'] = ErrorList([msg])
            del self.cleaned_data['phonebook']

        dialer_set = user_dialer_setting(self.user)
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

    """
    DuplicateCampaignForm ModelForm
    """
    campaign_code = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Campaign
        fields = ['campaign_code', 'name', 'phonebook']

    def __init__(self, user, *args, **kwargs):
        super(DuplicateCampaignForm, self).__init__(*args, **kwargs)
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
        camp_list = []
        camp_list.append((0, _('ALL')))
        campaign_list = Campaign.objects.values_list('id', 'name').all().order_by('-id')
        for i in campaign_list:
            camp_list.append((i[0], i[1]))

        self.fields['campaign_id'].choices = camp_list


class SubscriberAdminForm(ModelForm):

    """SubscriberAdminForm"""

    class Meta:
        model = Subscriber
        exclude = ['updated_date', ]

    def __init__(self, *args, **kwargs):
        super(SubscriberAdminForm, self).__init__(*args, **kwargs)
        #self.fields['agent'].choices = agent_list()

subscriber_status_list = []
subscriber_status_list.append(('all', _('ALL')))
for i in SUBSCRIBER_STATUS:
    subscriber_status_list.append((i[0], i[1]))


class SubscriberSearchForm(SearchForm):

    """Search Form on Subscriber List"""
    campaign_id = forms.ChoiceField(label=_('Campaign'), required=True)
    #agent_id = forms.ChoiceField(label=_('agent'), required=True)
    status = forms.ChoiceField(label=_('Status'), choices=subscriber_status_list, required=False)

    def __init__(self, user, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        css_class = 'col-md-3'
        self.helper.layout = Layout(
            Div(
                Div('from_date', css_class=css_class),
                Div('to_date', css_class=css_class),
                Div('campaign_id', css_class=css_class),
                Div('status', css_class=css_class),
                css_class='row'
            ),
        )
        common_submit_buttons(self.helper.layout, 'search')
        super(SubscriberSearchForm, self).__init__(*args, **kwargs)
        if user:
            camp_list = []
            camp_list.append((0, _('ALL')))
            if user.is_superuser:
                campaign_list = Campaign.objects.values_list('id', 'name').all().order_by('-id')
            else:
                campaign_list = Campaign.objects.values_list('id', 'name').filter(user=user).order_by('-id')

            for i in campaign_list:
                camp_list.append((i[0], i[1]))

            """
            agent_list = []
            agent_list.append((0, _('ALL')))
            if user.is_superuser:
                agent_profile_list = AgentProfile.objects.values_list('user_id', flat=True).filter(is_agent=True)
            else:
                agent_profile_list = AgentProfile.objects.values_list('user_id', flat=True)\
                    .filter(is_agent=True, manager=user)

            a_list = Agent.objects.values_list('id', 'username').filter(id__in=agent_profile_list)
            for i in a_list:
                agent_list.append((i[0], i[1]))
            self.fields['agent_id'].choices = agent_list
            """
            self.fields['campaign_id'].choices = camp_list


campaign_status_list = []
campaign_status_list.append(('all', _('ALL')))
for i in CAMPAIGN_STATUS:
    campaign_status_list.append((i[0], i[1]))


class CampaignSearchForm(forms.Form):
    phonebook_id = forms.ChoiceField(label=_("Phonebook"), )
    status = forms.ChoiceField(label=_("Status"), choices=campaign_status_list)

    def __init__(self, user, *args, **kwargs):
        super(CampaignSearchForm, self).__init__(*args, **kwargs)
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
            result_list = get_phonebook_list(user)
            result_list.insert(0, ('0', _('ALL')))
            self.fields['phonebook_id'].choices = result_list
