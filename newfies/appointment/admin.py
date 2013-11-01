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
from appointment.models.events import Event
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


class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'frequency', 'params')
    ordering = ('-id', )


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'start', 'end', 'creator', 'rule',
                    'end_recurring_period', 'calendar', 'notify_count', 'status')
    ordering = ('-id', )


admin.site.register(CalendarUser, CalendarUserAdmin)
admin.site.register(CalendarSetting, CalendarSettingAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(Event, EventAdmin)
