#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.contrib import admin
from dnc.models import DNC, DNCContact


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
