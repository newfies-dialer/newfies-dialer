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
from apt_reminder.models import Calendar_Setting, Calendar_User, Calendar_UserProfile
from apt_reminder.forms import Calendar_UserProfileForm
from common.app_label_renamer import AppLabelRenamer
AppLabelRenamer(native_app_label=u'apt_reminder', app_label=_('appointment reminder')).main()


class Calendar_UserProfileInline(admin.StackedInline):
    model = Calendar_UserProfile
    form = Calendar_UserProfileForm


class Calendar_UserAdmin(UserAdmin):
    inlines = [
        Calendar_UserProfileInline,
    ]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active', 'is_superuser', 'last_login')

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        qs = qs.filter(is_staff=False, is_superuser=False)
        return qs

admin.site.register(Calendar_User, Calendar_UserAdmin)


class Calendar_SettingAdmin(admin.ModelAdmin):
    list_display = ('cid_number', 'cid_name', 'call_timeout', 'user', 'survey')
    ordering = ('-cid_number', )


admin.site.register(Calendar_Setting, Calendar_SettingAdmin)
