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
from django.utils.translation import ugettext_lazy as _
from dnc.models import DNC, DNCContact
from common.app_label_renamer import AppLabelRenamer
AppLabelRenamer(native_app_label=u'dnc', app_label=_('do not call').title()).main()


class DNCAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a Gateway."""
    list_display = ('id', 'name', 'user', 'dnc_contacts_count')
    list_display_links = ('name', )
    list_filter = ['user']
    ordering = ('id', )

admin.site.register(DNC, DNCAdmin)


class DNCContactAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a Gateway."""
    list_display = ('id', 'dnc', 'phone_number')
    list_display_links = ('id', )
    list_filter = ['dnc', 'updated_date']
    ordering = ('id', )

admin.site.register(DNCContact, DNCContactAdmin)
