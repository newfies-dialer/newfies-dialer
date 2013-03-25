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
from agent.models import Agent
from django.utils.translation import ugettext as _
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms


class AgentCreationForm(UserCreationForm):
    """AgentCreationForm"""
    class Meta:
        model = Agent
        fields = ("username", "password1", "password2")


class AgentChangeForm(UserChangeForm):
    """AgentChangeForm"""
    is_agent = forms.BooleanField()

    class Meta:
        model = Agent


class AgentAdmin(UserAdmin):
    form = AgentChangeForm
    add_form = AgentCreationForm

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('is_agent', 'first_name', 'last_name', 'email')}),
        # (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
        #                                'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_filter = []


admin.site.register(Agent, AgentAdmin)


# class AgentProfileInline(admin.StackedInline):
#     model = AgentProfile


# class AgentAdmin(UserAdmin):
#     inlines = [AgentProfileInline]
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
#                     'is_active', 'is_superuser', 'last_login')
#     list_filter = []

#     def queryset(self, request):
#         qs = super(UserAdmin, self).queryset(request)
#         qs = qs.filter(is_staff=False, is_superuser=False)
#         return qs
