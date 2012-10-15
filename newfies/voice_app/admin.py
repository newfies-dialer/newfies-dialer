#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django.contrib import admin
from voice_app.models import VoiceApp_template


class VoiceAppAdmin(admin.ModelAdmin):
    """
    Allows the administrator to view and modify certain attributes
    of a VoiceApp
    """
    list_display = ('id', 'name', 'type', 'data', 'tts_language', 'user',
                    'gateway', 'created_date')
    list_display_links = ('id', 'name', )
    list_filter = ['created_date', ]
    ordering = ('id', )

admin.site.register(VoiceApp_template, VoiceAppAdmin)
