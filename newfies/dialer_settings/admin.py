from django.contrib import admin
#from django.utils.translation import ugettext as _
from dialer_settings.models import DialerSetting


# DialerSetting
class DialerSettingAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a DialerSetting."""
    list_display = ('name', 'max_frequency', 'callmaxduration', 'maxretry',
                    'max_calltimeout', 'max_number_campaign',
                    'max_number_subscriber_campaign', 'blacklist', 'whitelist',
                    'updated_date')
    #list_filter = ['setting_group']
    search_fields = ('name', )
    ordering = ('-name', )

admin.site.register(DialerSetting, DialerSettingAdmin)
