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
from django.contrib.auth.models import User
from django.db.models import Q
from user_profile.models import UserProfile, Manager, Staff
from appointment.function_def import get_all_calendar_user_id_list
#from agent.models import AgentProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class StaffAdmin(UserAdmin):
    inlines = [UserProfileInline]

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active', 'is_superuser', 'last_login')
    list_filter = []

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        qs = qs.filter(Q(is_superuser=True))
        return qs


class ManagerAdmin(UserAdmin):
    inlines = [
        UserProfileInline,
    ]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active', 'is_superuser', 'last_login')
    list_filter = []

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        #agent_id_list = AgentProfile.objects.values_list('user_id', flat=True)\
        #    .filter(is_agent=True, manager__isnull=False)
        calendar_user_list = get_all_calendar_user_id_list()
        qs = qs.filter(is_superuser=False).exclude(id__in=calendar_user_list)  # .exclude(id__in=agent_id_list)
        return qs

admin.site.unregister(User)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Manager, ManagerAdmin)
