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
from django.utils.translation import ugettext as _
from django.contrib.auth.forms import UserCreationForm, AdminPasswordChangeForm,\
    UserChangeForm
from appointment.models.users import CalendarUserProfile, CalendarUser,\
    CalendarSetting
from appointment.models.events import Event
from appointment.models.calendars import Calendar
from appointment.models.alarms import Alarm
from appointment.function_def import get_calendar_user_id_list,\
    get_calendar_user_list, get_calendar_list
from survey.models import Survey


class CalendarUserPasswordChangeForm(AdminPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CalendarUserPasswordChangeForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class CalendarUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CalendarUserCreationForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class CalendarUserProfileForm(ModelForm):
    """CalendarUserProfileForm"""

    class Meta:
        model = CalendarUserProfile


class CalendarSettingForm(ModelForm):
    """CalendarSetting ModelForm"""

    class Meta:
        model = CalendarSetting
        exclude = ('user')

    def __init__(self, user, *args, **kwargs):
        super(CalendarSettingForm, self).__init__(*args, **kwargs)

        list_survey = []
        list_survey.append((0, '---'))
        survey_list = Survey.objects.values_list(
            'id', 'name').filter(user=user).order_by('id')
        for l in survey_list:
            list_survey.append((l[0], l[1]))
        self.fields['survey'].choices = list_survey

        list_gateway = []
        list_gateway.append((0, '---'))
        gateway_list = user.get_profile().userprofile_gateway.all()
        for l in gateway_list:
            list_gateway.append((l.id, l.name))
        self.fields['aleg_gateway'].choices = list_gateway

        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class CalendarUserNameChangeForm(UserChangeForm):
    """CalendarUserNameChangeForm is used to change CalendarUser username"""

    class Meta:
        model = CalendarUser
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super(CalendarUserNameChangeForm, self).__init__(*args, **kwargs)


class CalendarUserChangeDetailExtendForm(ModelForm):
    """A form used to change the detail of a CalendarUser in the manager UI."""
    class Meta:
        model = CalendarUserProfile
        exclude = ('manager', 'user')

    def __init__(self, user, *args, **kwargs):
        super(CalendarUserChangeDetailExtendForm, self).__init__(*args, **kwargs)

        list_calendar_setting = []
        list_calendar_setting.append((0, '---'))
        calendar_setting_list = CalendarSetting.objects.filter(user=user).order_by('id')
        for l in calendar_setting_list:
            list_calendar_setting.append((l.id, l.caller_name))
        self.fields['calendar_setting'].choices = list_calendar_setting

        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class CalendarForm(ModelForm):
    """CalendarForm"""
    class Meta:
        model = Calendar
        exclude = ('slug')

    def __init__(self, user, *args, **kwargs):
        super(CalendarForm, self).__init__(*args, **kwargs)
        calendar_user_list = get_calendar_user_id_list(user)
        self.fields['user'].choices = get_calendar_user_list(calendar_user_list)


class EventAdminForm(ModelForm):
    """Admin Event ModelForm"""
    class Meta:
        model = Event
        exclude = ('parent_event', 'occ_count')


class EventForm(ModelForm):
    """Event ModelForm"""

    class Meta:
        model = Event
        exclude = ('parent_event', 'occ_count')

    def __init__(self, user, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['start', 'end', 'title', 'description',
                                'creator', 'created_on', 'end_recurring_period',
                                'rule', 'calendar', 'notify_count', 'status',
                                'data']

        calendar_user_list = get_calendar_user_id_list(user)
        self.fields['calendar'].choices = get_calendar_list(calendar_user_list)
        self.fields['creator'].choices = get_calendar_user_list(calendar_user_list)


class EventSearchForm(forms.Form):
    """Event Search Form"""
    start_date = forms.CharField(label=_('start date'), required=False, max_length=20)
    calendar_id = forms.ChoiceField(label=_('calendar'), required=False,
                                    choices=[('0', '---')])
    calendar_user_id = forms.ChoiceField(label=_('calendar user'), required=False,
                                         choices=[('0', '---')])

    def __init__(self, user, *args, **kwargs):
        super(EventSearchForm, self).__init__(*args, **kwargs)
        calendar_user_list = get_calendar_user_id_list(user)
        self.fields['calendar_id'].choices = get_calendar_list(calendar_user_list)
        self.fields['calendar_user_id'].choices = get_calendar_user_list(calendar_user_list)


class AlarmForm(ModelForm):
    """Alarm ModelForm"""

    class Meta:
        model = Alarm

    def __init__(self, user, *args, **kwargs):
        super(AlarmForm, self).__init__(*args, **kwargs)

        list_survey = []
        list_survey.append((0, '---'))
        survey_list = Survey.objects.values_list(
            'id', 'name').filter(user=user).order_by('id')
        for l in survey_list:
            list_survey.append((l[0], l[1]))
        self.fields['survey'].choices = list_survey

        calendar_user_list = get_calendar_user_id_list(user)

        list_event = []
        list_event.append((0, '---'))
        event_list = Event.objects.values_list(
            'id', 'title').filter(calendar__user_id__in=calendar_user_list).order_by('id')
        for l in event_list:
            list_event.append((l[0], l[1]))
        self.fields['event'].choices = list_event


