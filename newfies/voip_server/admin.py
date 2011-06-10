from django.contrib import admin
#from django.utils.translation import ugettext as _
from voip_server.models import *


class VoipServerGroupAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a VoipServerGroup."""
    list_display = ('id', 'name', 'description', 'created_date')
    list_display_links = ('name', )
    list_filter = ['created_date', ]
    ordering = ('id', )
admin.site.register(VoipServerGroup, VoipServerGroupAdmin)


class VoipServerAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a VoipServer."""
    list_display = ('id', 'name', 'serverip', 'username', 'port', 'status',
                    'type', 'created_date')
    list_display_links = ('name', )
    list_filter = ['serverip', 'status', 'type']
    ordering = ('id', )
admin.site.register(VoipServer, VoipServerAdmin)
