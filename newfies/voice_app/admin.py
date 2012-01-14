from django.contrib import admin
#from django.utils.translation import ugettext_lazy as _
from voice_app.models import VoiceApp


class VoiceAppAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a VoiceApp."""
    list_display = ('id', 'name', 'type', 'data', 'user', 'gateway', 'created_date')
    list_display_links = ('id', 'name', )
    list_filter = ['created_date', ]
    ordering = ('id', )
admin.site.register(VoiceApp, VoiceAppAdmin)
