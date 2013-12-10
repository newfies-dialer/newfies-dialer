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
from agent.models import Agent, AgentProfile
from agent.forms import AgentProfileForm
from agent.admin_filters import ManagerFilter
from appointment.function_def import get_all_calendar_user_id_list


class AgentProfileInline(admin.StackedInline):
    model = AgentProfile
    form = AgentProfileForm


class AgentAdmin(UserAdmin):
    inlines = [
        AgentProfileInline,
    ]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active', 'is_superuser', 'manager_name', 'last_login')
    list_filter = (ManagerFilter, )

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        calendar_user_list = get_all_calendar_user_id_list()
        qs = qs.filter(is_staff=False, is_superuser=False).exclude(id__in=calendar_user_list)
        return qs

admin.site.register(Agent, AgentAdmin)
