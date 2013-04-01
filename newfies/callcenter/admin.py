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
from django.utils.translation import ugettext as _
from callcenter.models import Queue, Tier
from callcenter.forms import QueueForm, TierForm
from callcenter.admin_filters import CallcenterAdminAgentFilter, CallcenterAdminManagerFilter


class QueueAdmin(admin.ModelAdmin):
    form = QueueForm
    list_display = ('id', 'manager', 'strategy', 'moh_sound', 'time_base_score')
    list_filter = (CallcenterAdminManagerFilter,)


class TierAdmin(admin.ModelAdmin):
    form = TierForm
    list_display = ('id', 'manager', 'agent', 'queue', 'level', 'position')
    list_filter = (CallcenterAdminManagerFilter, CallcenterAdminAgentFilter, 'queue')

admin.site.register(Queue, QueueAdmin)
admin.site.register(Tier, TierAdmin)
