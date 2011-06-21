from django.contrib import admin
#from django.utils.translation import ugettext as _
from dialer_gateway.models import Gateway


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

    fieldsets = (
        ('Standard options', {
         'fields': ('name', 'description', 'gateways', 'gateway_codecs', 'gateway_timeouts', 'gateway_retries', 'originate_dial_string', 'status'),
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('addprefix', 'removeprefix', 'failover', 'addparameter',
                       'maximum_call', )
        }),
    )
    list_display = ('id', 'name', 'gateways', 'addprefix',
                    'removeprefix', 'secondused', 'count_call', 'status',)
    list_display_links = ('name', )
    list_filter = ['gateways',]
    ordering = ('id', )
admin.site.register(Gateway, GatewayAdmin)
