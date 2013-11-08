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

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from appointment.models.users import CalendarSetting, CalendarUser, CalendarUserProfile
from appointment.models.rules import Rule
from appointment.models.events import Event, Occurrence
from appointment.models.alarms import Alarm, SMSTemplate, AlarmRequest
from appointment.models.calendars import Calendar
from appointment.forms import CalendarUserProfileForm
from common.app_label_renamer import AppLabelRenamer
AppLabelRenamer(native_app_label=u'appointment', app_label=_('appointment')).main()


class CalendarUserProfileInline(admin.StackedInline):
    model = CalendarUserProfile
    form = CalendarUserProfileForm


class CalendarUserAdmin(UserAdmin):
    inlines = [
        CalendarUserProfileInline,
    ]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active', 'is_superuser', 'last_login')

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        qs = qs.filter(is_staff=False, is_superuser=False)
        return qs


class CalendarSettingAdmin(admin.ModelAdmin):
    list_display = ('cid_number', 'cid_name', 'call_timeout', 'user', 'survey')
    ordering = ('-cid_number', )


class CalendarAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'user', 'max_concurrent')
    ordering = ('-id', )


class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'frequency', 'params')
    ordering = ('-id', )


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'start', 'end', 'creator', 'rule',
                    'end_recurring_period', 'calendar', 'notify_count', 'status')
    ordering = ('-id', )


class OccurrenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'start', 'end', 'cancelled',
                    'original_start', 'original_end')
    ordering = ('-id', )


class AlarmAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'daily_start', 'daily_stop',
                    'advance_notice', 'retry_count', 'method',
                    'status', 'result', 'created_date')
    ordering = ('-id', )
    list_filter = ('event', 'created_date')


class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ('label', 'sms_text', 'created_date')
    ordering = ('-id', )


class AlarmRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'alarm', 'date', 'status', 'callstatus', 'callrequest')
    ordering = ('-id', )


admin.site.register(Calendar, CalendarAdmin)
admin.site.register(CalendarUser, CalendarUserAdmin)
admin.site.register(CalendarSetting, CalendarSettingAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(AlarmRequest, AlarmRequestAdmin)
admin.site.register(Alarm, AlarmAdmin)
admin.site.register(SMSTemplate, SMSTemplateAdmin)
