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
from django.contrib import messages
from django.conf.urls import patterns
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from dialer_campaign.models import Campaign, Subscriber
from dialer_campaign.function_def import check_dialer_setting, dialer_setting_limit
from dialer_campaign.forms import SubscriberReportForm
from genericadmin.admin import GenericAdminModelAdmin
from common.app_label_renamer import AppLabelRenamer
APP_LABEL = AppLabelRenamer(native_app_label=u'dialer_campaign', app_label=_('Dialer Campaign')).main()


class CampaignAdmin(GenericAdminModelAdmin):
    """
    Allows the administrator to view and modify certain attributes
    of a Campaign.
    """
    content_type_whitelist = ('survey/survey_template', )
    fieldsets = (
        (_('standard options').capitalize(), {
            'fields': ('campaign_code', 'name', 'description', 'callerid',
                       'user', 'status', 'startingdate', 'expirationdate',
                       'aleg_gateway', 'content_type', 'object_id',
                       'extra_data', 'phonebook', 'voicemail', 'amd_behavior',
                       'voicemail_audiofile'
                       ),
        }),
        (_('advanced options').capitalize(), {
            'classes': ('collapse',),
            'fields': ('frequency', 'callmaxduration', 'maxretry',
                       'intervalretry', 'calltimeout', 'imported_phonebook',
                       'daily_start_time', 'daily_stop_time',
                       'monday', 'tuesday', 'wednesday',
                       'thursday', 'friday', 'saturday', 'sunday',
                       'completion_maxretry', 'completion_intervalretry', 'dnc')
        }),
    )
    list_display = ('id', 'name', 'content_type', 'campaign_code', 'user',
                    'startingdate', 'expirationdate', 'frequency',
                    'callmaxduration', 'maxretry', 'aleg_gateway', 'status',
                    'update_campaign_status', 'totalcontact', 'completed',
                    'subscriber_detail', 'progress_bar')

    list_display_links = ('id', 'name', )
    #list_filter doesn't display correctly too many elements in list_display
    #list_filter = ['user', 'status', 'created_date']
    ordering = ('-id', )
    filter_horizontal = ('phonebook',)

    def get_urls(self):
        urls = super(CampaignAdmin, self).get_urls()
        my_urls = patterns('',
                           (r'^$', self.admin_site.admin_view(self.changelist_view)),
                           (r'^add/$', self.admin_site.admin_view(self.add_view)),
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
            msg = _("you have too many campaigns. max allowed %(limit)s") \
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

    def get_urls(self):
        urls = super(SubscriberAdmin, self).get_urls()
        my_urls = patterns('',
                    (r'^subscriber_report/$', self.admin_site.admin_view(self.subscriber_report)),
                  )
        return my_urls + urls

    def subscriber_report(self, request):
        opts = Subscriber._meta
        form = SubscriberReportForm()
        if request.method == 'POST':
            form = SubscriberReportForm(request.POST)
            if form.is_valid():
                print request.POST['campaign']
        ctx = RequestContext(request, {
            'form': form,
            'opts': opts,
            'model_name': opts.object_name.lower(),
            'app_label': APP_LABEL,
            'title': _('subscriber report'),
        })

        return render_to_response('admin/dialer_campaign/subscriber/subscriber_report.html',
               context_instance=ctx)

admin.site.register(Subscriber, SubscriberAdmin)
