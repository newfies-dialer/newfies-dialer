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
from apt_reminder.models import Calender_Setting, Calender_User, Calender_UserProfile
from apt_reminder.forms import Calender_UserProfileForm
from common.app_label_renamer import AppLabelRenamer
AppLabelRenamer(native_app_label=u'apt_reminder', app_label=_('appointment reminder')).main()


class Calender_UserProfileInline(admin.StackedInline):
    model = Calender_UserProfile
    form = Calender_UserProfileForm


class Calender_UserAdmin(UserAdmin):
    inlines = [
        Calender_UserProfileInline,
    ]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active', 'is_superuser', 'last_login')

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        qs = qs.filter(is_staff=False, is_superuser=False)
        return qs

admin.site.register(Calender_User, Calender_UserAdmin)


class Calender_SettingAdmin(admin.ModelAdmin):
    list_display = ('cid_number', 'cid_name', 'call_timeout', 'user', 'survey')
    ordering = ('-cid_number', )


admin.site.register(Calender_Setting, Calender_SettingAdmin)
