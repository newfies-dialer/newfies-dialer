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
from django.contrib import messages
from django.conf.urls import patterns
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from dialer_campaign.models import Campaign, Subscriber
from dialer_campaign.function_def import check_dialer_setting, dialer_setting_limit
from genericadmin.admin import GenericAdminModelAdmin


class CampaignAdmin(GenericAdminModelAdmin):
    """
    Allows the administrator to view and modify certain attributes
    of a Campaign.
    """
    content_type_whitelist = ('voice_app/voiceapp_template', 'survey2/survey_template', )
    fieldsets = (
        (_('Standard options'), {
            'fields': ('campaign_code', 'name', 'description', 'callerid',
                       'user', 'status', 'startingdate', 'expirationdate',
                       'aleg_gateway', 'content_type', 'object_id',
                       'extra_data', 'phonebook',
                       ),
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('frequency', 'callmaxduration', 'maxretry',
                       'intervalretry', 'calltimeout', 'imported_phonebook',
                       'daily_start_time', 'daily_stop_time',
                       'monday', 'tuesday', 'wednesday',
                       'thursday', 'friday', 'saturday', 'sunday',
                       'completion_maxretry', 'completion_intervalretry')
        }),
    )
    list_display = ('id', 'name', 'content_type', 'campaign_code', 'user',
                    'startingdate', 'expirationdate', 'frequency',
                    'callmaxduration', 'maxretry', 'aleg_gateway', 'status',
                    'update_campaign_status', 'totalcontact', 'completed',
                    'subscriber_detail', 'progress_bar')

    list_display_links = ('id', 'name', )
    #list_filter = ['user', 'status', 'startingdate', 'created_date']
    ordering = ('id', )
    filter_horizontal = ('phonebook',)

    def get_urls(self):
        urls = super(CampaignAdmin, self).get_urls()
        my_urls = patterns('',
                           (r'^$',
                            self.admin_site.admin_view(self.changelist_view)),
                           (r'^add/$',
                            self.admin_site.admin_view(self.add_view)),
                           )
        return my_urls + urls

    def add_view(self, request, extra_context=None):
        """
        Override django add_view method for checking the dialer setting limit

        **Logic Description**:

            * Before adding campaign, check dialer setting limit if applicable
              to the user, if matched then the user will be redirected to
              the campaign list
        """
        # Check dialer setting limit
        # check Max Number of running campaigns
        if check_dialer_setting(request, check_for="campaign"):
            msg = _("you have too many campaigns. Max allowed %(limit)s") \
                % {'limit':
                    dialer_setting_limit(request, limit_for="campaign")}
            messages.error(request, msg)

            return HttpResponseRedirect(
                reverse("admin:dialer_campaign_campaign_changelist"))
        ctx = {}
        return super(CampaignAdmin, self).add_view(request, extra_context=ctx)
admin.site.register(Campaign, CampaignAdmin)


class SubscriberAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a Subscriber."""
    list_display = ('id', 'contact', 'campaign',
                    'last_attempt', 'count_attempt', 'completion_count_attempt', 'duplicate_contact',
                    'contact_name', 'status', 'created_date')
    list_filter = ['campaign', 'status', 'created_date', 'last_attempt']
    ordering = ('-id', )
admin.site.register(Subscriber, SubscriberAdmin)
