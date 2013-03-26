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
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext as _
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.db.models import Q
from agent.models import Agent, AgentProfile
from user_profile.models import Manager


def manager_list():
    manager_list = []
    list = Manager.objects.values_list('id', 'username')\
        .filter(is_staff=True, is_superuser=False, is_active=True).order_by('id')
    for l in list:
        manager_list.append((l[0], l[1]))
    return manager_list


"""
class AgentCreationForm(UserCreationForm):
    class Meta:
        model = Agent
        fields = ("username", "password1", "password2")


class AgentChangeForm(UserChangeForm):
    is_agent = forms.BooleanField()
    manager = forms.ChoiceField(label=_("manager"),
        choices=manager_list())

    class Meta:
        model = Agent
"""

"""
class AgentAdmin(UserAdmin):
    form = AgentChangeForm
    add_form = AgentCreationForm

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('is_agent', 'manager', 'first_name', 'last_name', 'email')}),
        # (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
        #                                'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_filter = []
"""

class AgentProfileInline(admin.StackedInline):
    model = AgentProfile


class AgentAdmin(UserAdmin):
    inlines = [
        AgentProfileInline,
    ]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active', 'is_superuser', 'last_login')
    list_filter = []

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        qs = qs.filter(is_staff=False, is_superuser=False)
        return qs

admin.site.register(Agent, AgentAdmin)
