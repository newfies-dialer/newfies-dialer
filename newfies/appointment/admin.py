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

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from appointment.models.users import CalendarSetting, CalendarUser, \
    CalendarUserProfile
from appointment.models.rules import Rule
from appointment.models.events import Event, Occurrence
from appointment.models.alarms import Alarm, AlarmRequest
from appointment.models.calendars import Calendar
from appointment.admin_filters import ManagerFilter
from appointment.forms import CalendarUserProfileForm, EventAdminForm, \
    AdminCalendarForm


class CalendarUserProfileInline(admin.StackedInline):
    model = CalendarUserProfile
    form = CalendarUserProfileForm


class CalendarUserAdmin(UserAdmin):
    inlines = [
        CalendarUserProfileInline,
    ]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active', 'is_superuser', 'last_login')
    list_filter = (ManagerFilter, )

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        calendar_user_list = CalendarUserProfile.objects.values_list('user_id', flat=True).all()
        qs = qs.filter(id__in=calendar_user_list)
        return qs


class CalendarSettingAdmin(admin.ModelAdmin):
    list_display = ('label', 'callerid', 'caller_name', 'call_timeout', 'user', 'survey',
                    'aleg_gateway', 'sms_gateway', 'voicemail', 'amd_behavior', 'updated_date')
    ordering = ('-callerid', )


class CalendarAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'max_concurrent')
    ordering = ('-id', )
    form = AdminCalendarForm


class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'frequency', 'params')
    ordering = ('-id', )


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'start', 'end', 'creator', 'rule',
                    'end_recurring_period', 'calendar', 'notify_count', 'status',
                    'parent_event', 'occ_count')
    ordering = ('-id', )
    form = EventAdminForm


class OccurrenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'start', 'end', 'cancelled',
                    'original_start', 'original_end')
    ordering = ('-id', )


class AlarmAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'alarm_phonenumber', 'alarm_email',
                    'daily_start', 'daily_stop', 'advance_notice',
                    'maxretry', 'retry_delay', 'num_attempt', 'method',
                    'status', 'result', 'created_date', 'date_start_notice')
    ordering = ('-id', )
    list_filter = ('event', 'created_date')


class AlarmRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'alarm', 'date', 'status', 'callstatus')
    ordering = ('-id', )

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(CalendarUser, CalendarUserAdmin)
admin.site.register(CalendarSetting, CalendarSettingAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(AlarmRequest, AlarmRequestAdmin)
admin.site.register(Alarm, AlarmAdmin)
