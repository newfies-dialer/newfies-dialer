from django.contrib import admin
from django.conf.urls.defaults import *
from django.utils.translation import ugettext_lazy as _
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

    def get_urls(self):
        urls = super(DialerSettingAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^$', self.admin_site.admin_view(self.changelist_view)),
            (r'^add/$', self.admin_site.admin_view(self.add_view)),
            (r'^/(.+)/$', self.admin_site.admin_view(self.change_view)),
        )
        return my_urls + urls

    def changelist_view(self, request, extra_context=None):
        """
        Dialer setting list
        """
        ctx = {
            #'app_label': _('Dialer setting'),
            #'title': _('Select dialer setting to Change'),
        }
        return super(DialerSettingAdmin, self)\
               .changelist_view(request, extra_context=ctx)

    def add_view(self, request, extra_context=None):
        """
        Add Dialer setting
        """
        ctx = {
            #'app_label': _('Dialer Setting'),
            'title': _('Add dialer settings'),
        }
        return super(DialerSettingAdmin, self)\
               .add_view(request, extra_context=ctx)

    def change_view(self, request, object_id, extra_context=None):
        """
        Edit dialer settings
        """
        ctx = {
            #'app_label': _('Dialer Setting'),
            'title': _('Change dialer settings'),
        }
        return super(DialerSettingAdmin, self)\
               .change_view(request, object_id, extra_context=ctx)

admin.site.register(DialerSetting, DialerSettingAdmin)
