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
from dialer_gateway.models import Gateway
from common.app_label_renamer import AppLabelRenamer
AppLabelRenamer(native_app_label=u'dialer_gateway', app_label=_('Dialer Gateway')).main()

"""
class GatewayGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_date')
    list_display_links = ('name', )
    list_filter = ['metric']
    ordering = ('id', )
admin.site.register(GatewayGroup, GatewayGroupAdmin)
"""


class GatewayAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a Gateway."""

    # fieldsets = (
    #     (_('standard options').capitalize(), {
    #         'fields': ('name', 'description', 'gateways', 'gateway_codecs',
    #             'gateway_timeouts', 'gateway_retries',
    #             'originate_dial_string', 'status'),
    #     }),
    #     (_('advanced options').capitalize(), {
    #         'classes': ('collapse',),
    #         'fields': ('addprefix', 'removeprefix', 'failover', 'addparameter',
    #                    'maximum_call', )
    #     }),
    # )
    fieldsets = (
        (_('standard options').capitalize(), {
            'fields': ('name', 'description', 'gateways',
                'gateway_timeouts', 'originate_dial_string', 'status',
                'addprefix', 'removeprefix', 'addparameter'),
        }),
    )
    list_display = ('id', 'name', 'gateways', 'addprefix',
                    'removeprefix', 'secondused', 'count_call', 'status',)
    list_display_links = ('name', )
    list_filter = ['gateways']
    ordering = ('id', )

admin.site.register(Gateway, GatewayAdmin)
