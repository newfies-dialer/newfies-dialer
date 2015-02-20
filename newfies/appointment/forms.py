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
from django.forms import ModelForm
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, AdminPasswordChangeForm, UserChangeForm
from user_profile.models import CalendarUser, CalendarUserProfile
from calendar_settings.models import CalendarSetting
from appointment.models.events import Event
from appointment.models.calendars import Calendar
from appointment.models.alarms import Alarm
from appointment.constants import EVENT_STATUS
from appointment.function_def import get_calendar_user_id_list, get_calendar_user_list,\
    get_calendar_list, get_all_calendar_user_id_list, manager_list_of_calendar_user
from survey.models import Survey
from user_profile.models import UserProfile
from mod_utils.forms import SaveUserModelForm
from bootstrap3_datetime.widgets import DateTimePicker
from mod_utils.forms import common_submit_buttons
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.layout import Layout, Div, Fieldset, HTML


class CalendarUserPasswordChangeForm(AdminPasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(CalendarUserPasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Fieldset('', 'password1', 'password2', css_class='col-md-4')
        )


class CalendarUserCreationForm(UserCreationForm):
    calendar_setting_id = forms.ChoiceField(label=_('calendar setting'), required=True, choices=[('', '---')])

    def __init__(self, manager, *args, **kwargs):
        super(CalendarUserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = False
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Fieldset('', 'username', 'password1', 'password2', 'calendar_setting_id', css_class='col-md-6 col-xs-8')
        )
        cal_setting_list = []
        setting_list = CalendarSetting.objects.filter(user=manager)
        cal_setting_list.append(('', _('Select Calendar Setting')))
        for i in setting_list:
            cal_setting_list.append((i.id, i.label))
        self.fields['calendar_setting_id'].choices = cal_setting_list


class CalendarUserChangeDetailExtendForm(ModelForm):

    """A form used to change the detail of a CalendarUser in the manager UI."""

    class Meta:
        model = CalendarUserProfile
        exclude = ('manager', 'user',)

    def __init__(self, user, *args, **kwargs):
        super(CalendarUserChangeDetailExtendForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = False
        css_class = 'col-md-6'
        self.helper.layout = Layout(
            Div(
                Div('calendar_setting', css_class=css_class),
                Div('accountcode', css_class=css_class),
                Div('address', css_class=css_class),
                Div('city', css_class=css_class),
                Div('state', css_class=css_class),
                Div('country', css_class=css_class),
                Div('zip_code', css_class=css_class),
                Div('phone_no', css_class=css_class),
                Div('fax', css_class=css_class),
                Div('company_name', css_class=css_class),
                Div('company_website', css_class=css_class),
                Div('language', css_class=css_class),
                Div('note', css_class=css_class),
                css_class='row'
            ),
        )
        list_calendar_setting = []
        list_calendar_setting.append((0, _('Select Calendar Setting')))
        for l in CalendarSetting.objects.filter(user=user).order_by('id'):
            list_calendar_setting.append((l.id, l.label))
        self.fields['calendar_setting'].choices = list_calendar_setting


class CalendarUserProfileForm(ModelForm):

    """CalendarUserProfileForm"""

    class Meta:
        model = CalendarUserProfile
        fields = ['manager', 'calendar_setting', ]

    def __init__(self, *args, **kwargs):
        super(CalendarUserProfileForm, self).__init__(*args, **kwargs)
        self.fields['manager'].choices = manager_list_of_calendar_user()


class CalendarSettingForm(SaveUserModelForm):

    """CalendarSetting ModelForm"""

    class Meta:
        model = CalendarSetting
        exclude = ('user', )

    def __init__(self, user, *args, **kwargs):
        super(CalendarSettingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        css_class = 'col-md-6'

        self.helper.layout = Layout(
            Div(
                Div('label', css_class=css_class),
                Div('callerid', css_class=css_class),
                Div('caller_name', css_class=css_class),
                Div('call_timeout', css_class=css_class),
                Div('survey', css_class=css_class),
                Div('aleg_gateway', css_class=css_class),
                Div('sms_gateway', css_class=css_class),
                css_class='row'
            ),
        )
        if settings.AMD:
            self.helper.layout.append(
                Div(
                    Div(
                        HTML("""
                            <div class="btn-group" data-toggle="buttons">
                                <label for="{{ form.voicemail.auto_id }}">{{ form.voicemail.label }}</label><br/>
                                <div class="make-switch switch-small">
                                {{ form.voicemail }}
                                </div>
                            </div>
                            """), css_class='col-md-12 col-xs-10'
                    ),
                    css_class='row'
                ),
            )
            self.helper.layout.append(
                Div(
                    Div('amd_behavior', css_class=css_class),
                    Div('voicemail_audiofile', css_class=css_class),
                    css_class='row'
                )
            )

        if self.instance.id:
            form_action = common_submit_buttons(default_action='update')
        else:
            form_action = common_submit_buttons(default_action='add')

        self.helper.layout.append(form_action)

        list_survey = []
        list_survey.append((0, '---'))
        for l in Survey.objects.values_list('id', 'name').filter(user=user).order_by('id'):
            list_survey.append((l[0], l[1]))
        self.fields['survey'].choices = list_survey

        list_gateway = []
        list_gateway.append((0, '---'))
        for l in UserProfile.objects.get(user=user).userprofile_gateway.all():
            list_gateway.append((l.id, l.name))
        self.fields['aleg_gateway'].choices = list_gateway


class CalendarUserNameChangeForm(UserChangeForm):

    """CalendarUserNameChangeForm is used to change CalendarUser username"""

    class Meta:
        model = CalendarUser
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super(CalendarUserNameChangeForm, self).__init__(*args, **kwargs)


class CalendarForm(ModelForm):

    """CalendarForm"""

    class Meta:
        model = Calendar
        fields = ['name', 'user', 'max_concurrent', ]

    def __init__(self, user, *args, **kwargs):
        super(CalendarForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Fieldset('', 'name', 'user', 'max_concurrent', css_class='col-xs-4')
        )
        if self.instance.id:
            form_action = common_submit_buttons(default_action='update')
        else:
            form_action = common_submit_buttons(default_action='add')
        self.helper.layout.append(form_action)
        calendar_user_list = get_calendar_user_id_list(user)
        self.fields['user'].choices = get_calendar_user_list(calendar_user_list)


class AdminCalendarForm(ModelForm):

    class Meta:
        model = Calendar
        fields = ['name', 'user', 'max_concurrent', ]

    def __init__(self, *args, **kwargs):
        super(AdminCalendarForm, self).__init__(*args, **kwargs)
        calendar_user_list = get_all_calendar_user_id_list()
        self.fields['user'].choices = get_calendar_user_list(calendar_user_list)


class EventAdminForm(ModelForm):

    """Admin Event ModelForm"""

    class Meta:
        model = Event
        exclude = ('parent_event', 'occ_count', )

    def __init__(self, *args, **kwargs):
        super(EventAdminForm, self).__init__(*args, **kwargs)

        calendar_user_list = get_all_calendar_user_id_list()
        self.fields['creator'].choices = get_calendar_user_list(calendar_user_list)


class EventForm(ModelForm):

    """Event ModelForm"""

    class Meta:
        model = Event
        exclude = ('status', 'parent_event', 'occ_count', )
        widgets = {
            'start': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
            'end': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
            'end_recurring_period': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
            'created_on': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
        }

    def __init__(self, user, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        css_class = 'col-md-6'
        self.helper.layout = Layout(
            Fieldset(_('Event Settings')),
            Div(
                Div('title', css_class=css_class),
                Div('calendar', css_class=css_class),
                Div('creator', css_class=css_class),
                Div('created_on', css_class=css_class),
                Div('rule', css_class=css_class),
                Div('end_recurring_period', css_class=css_class),
                Div('start', css_class=css_class),
                Div('end', css_class=css_class),
                css_class='row'
            ),
            Div(
                Div('description', css_class=css_class),
                Div('data', css_class=css_class),
                css_class='row'
            ),
        )
        if self.instance.id:
            common_submit_buttons(self.helper.layout, 'update')
        else:
            common_submit_buttons(self.helper.layout)

        calendar_user_list = get_calendar_user_id_list(user)
        self.fields['calendar'].choices = get_calendar_list(calendar_user_list)
        self.fields['creator'].choices = get_calendar_user_list(calendar_user_list)


class EventSearchForm(forms.Form):

    """Event Search Form"""
    start_date = forms.CharField(
        label=_('Start Date'), required=False, max_length=20,
        widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}))
    calendar_id = forms.ChoiceField(label=_('Calendar'), required=False, choices=[('0', '---')])
    calendar_user_id = forms.ChoiceField(label=_('Calendar User'), required=False, choices=[('0', '---')])

    def __init__(self, user, *args, **kwargs):
        super(EventSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        css_class = 'col-md-4'
        self.helper.layout = Layout(
            Div(
                Div('start_date', css_class=css_class),
                Div('calendar_id', css_class=css_class),
                Div('calendar_user_id', css_class=css_class),
                css_class='row'
            ),
        )
        common_submit_buttons(self.helper.layout, 'search')
        calendar_user_list = get_calendar_user_id_list(user)
        self.fields['calendar_id'].choices = get_calendar_list(calendar_user_list)
        self.fields['calendar_user_id'].choices = get_calendar_user_list(calendar_user_list)


class AlarmForm(ModelForm):

    """Alarm ModelForm"""

    class Meta:
        model = Alarm
        exclude = ('status', 'num_attempt', )
        widgets = {
            'date_start_notice': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
        }

    def __init__(self, user, *args, **kwargs):
        super(AlarmForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        if self.instance.id:
            form_action = common_submit_buttons(default_action='update')
        else:
            form_action = common_submit_buttons(default_action='add')

        css_class = 'col-md-6'
        self.helper.layout = Layout(
            TabHolder(
                Tab(_('General Settings'),
                    Div(
                        Div('date_start_notice', css_class=css_class),
                        Div('event', css_class=css_class),
                        Div('alarm_phonenumber', css_class=css_class),
                        Div('alarm_email', css_class=css_class),
                        Div('method', css_class=css_class),
                        Div('survey', css_class=css_class),
                        Div('mail_template', css_class=css_class),
                        Div('sms_template', css_class=css_class),
                        css_class='row'
                ),
                    form_action,
                    css_class='well'
                ),
                Tab(_('Alarm Settings'),
                    Div(
                        Div('daily_start', css_class=css_class),
                        Div('daily_stop', css_class=css_class),
                        Div('maxretry', css_class=css_class),
                        Div('retry_delay', css_class=css_class),
                        Div('advance_notice', css_class=css_class),
                        css_class='row'
                ),
                    form_action,
                    css_class='well'
                ),
                Tab(_('Result Settings'),
                    Div(
                        Div('result', css_class=css_class),
                        Div('url_cancel', css_class=css_class),
                        Div('phonenumber_sms_failure', css_class=css_class),
                        Div('url_confirm', css_class=css_class),
                        Div('phonenumber_transfer', css_class=css_class),
                        css_class='row'
                ),
                    form_action,
                    css_class='well'
                ),
            ),
        )

        list_survey = []
        list_survey.append((0, '---'))
        for l in Survey.objects.values_list('id', 'name').filter(user=user).order_by('id'):
            list_survey.append((l[0], l[1]))
        self.fields['survey'].choices = list_survey

        calendar_user_list = get_calendar_user_id_list(user)

        list_event = []
        list_event.append((0, '---'))
        event_list = Event.objects.values_list('id', 'title')\
            .filter(calendar__user_id__in=calendar_user_list,
                    status=EVENT_STATUS.PENDING).order_by('id')
        for l in event_list:
            list_event.append((l[0], l[1]))
        self.fields['event'].choices = list_event
