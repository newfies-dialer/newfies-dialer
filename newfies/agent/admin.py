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
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext as _
from agent.models import Agent, AgentProfile
from agent.forms import AgentProfileForm
from agent.function_def import manager_list


class ManagerFilter(SimpleListFilter):
    title = _('manager')
    parameter_name = 'manager'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return manager_list()

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() != None:
            agent_id_list = AgentProfile.objects.values_list('user_id', flat=True).filter(manager_id=self.value())
            return queryset.filter(id__in=agent_id_list)
        else:
            return queryset


class AgentProfileInline(admin.StackedInline):
    model = AgentProfile
    form = AgentProfileForm


class AgentAdmin(UserAdmin):
    inlines = [
        AgentProfileInline,
    ]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active', 'is_superuser', 'manager_name', 'last_login')
    list_filter = (ManagerFilter,)

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        qs = qs.filter(is_staff=False, is_superuser=False)
        return qs

admin.site.register(Agent, AgentAdmin)
