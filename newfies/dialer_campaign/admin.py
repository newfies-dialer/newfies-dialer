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
from django.contrib import messages
from django.conf.urls import patterns
from django.utils.translation import ugettext as _
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from dialer_campaign.models import Campaign, Subscriber
#from dialer_campaign.admin_filters import AgentFilter
from dialer_campaign.function_def import check_dialer_setting, dialer_setting_limit
from dialer_campaign.constants import SUBSCRIBER_STATUS, SUBSCRIBER_STATUS_NAME
from dialer_campaign.forms import SubscriberReportForm, SubscriberAdminForm
from genericadmin.admin import GenericAdminModelAdmin
from common.common_functions import variable_value, ceil_strdate
# from common.app_label_renamer import AppLabelRenamer
from datetime import datetime
APP_LABEL = _('Dialer Campaign')
# AppLabelRenamer(native_app_label=u'dialer_campaign', app_label=APP_LABEL).main()


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
                       'aleg_gateway', 'sms_gateway', 'content_type',
                       'object_id', 'extra_data', 'phonebook', 'voicemail',
                       'amd_behavior', 'voicemail_audiofile'
                       ),
        }),
        (_('advanced options').capitalize(), {
            'classes': ('collapse', ),
            'fields': ('frequency', 'callmaxduration', 'maxretry',
                       'intervalretry', 'calltimeout', 'imported_phonebook',
                       'daily_start_time', 'daily_stop_time',
                       'monday', 'tuesday', 'wednesday',
                       'thursday', 'friday', 'saturday', 'sunday',
                       'completion_maxretry', 'completion_intervalretry',
                       'dnc', 'agent_script', 'lead_disposition',
                       'external_link')
        }),
    )
    list_display = ('id', 'name', 'content_type', 'campaign_code', 'user',
                    'startingdate', 'expirationdate', 'frequency',
                    'callmaxduration', 'maxretry', 'aleg_gateway', 'sms_gateway',
                    'status', 'update_campaign_status', 'totalcontact',
                    'completed', 'subscriber_detail', 'progress_bar')

    list_display_links = ('id', 'name', )
    #list_filter doesn't display correctly too many elements in list_display
    #list_filter = ['user', 'status', 'created_date']
    ordering = ('-id', )
    filter_horizontal = ('phonebook', )

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
    form = SubscriberAdminForm
    list_display = ('id', 'contact', 'campaign', 'last_attempt', 'get_attempts',
                    'get_completion_attempts', 'duplicate_contact', 'disposition',
                    'collected_data', 'status', 'created_date')  # 'agent',
    list_filter = ('campaign', 'status', 'created_date', 'last_attempt', )  # AgentFilter
    ordering = ('-id', )

    def get_urls(self):
        urls = super(SubscriberAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^subscriber_report/$', self.admin_site.admin_view(self.subscriber_report)),
        )
        return my_urls + urls

    def subscriber_report(self, request):
        """
        Get subscriber report

        **Attributes**:

            * ``form`` - SubscriberReportForm
            * ``template`` - admin/dialer_campaign/subscriber/subscriber_report.html
        """
        opts = Subscriber._meta
        tday = datetime.today()
        form = SubscriberReportForm(initial={"from_date": tday.strftime("%Y-%m-%d"),
                                             "to_date": tday.strftime("%Y-%m-%d")})
        total_subscriber = 0
        total_pending = 0
        total_pause = 0
        total_abort = 0
        total_fail = 0
        total_sent = 0
        total_in_process = 0
        total_not_auth = 0
        total_completed = 0

        if request.method == 'POST':
            form = SubscriberReportForm(request.POST)
            if form.is_valid():
                start_date = ''
                end_date = ''
                if request.POST.get('from_date'):
                    from_date = request.POST.get('from_date')
                    start_date = ceil_strdate(from_date, 'start')

                if request.POST.get('to_date'):
                    to_date = request.POST.get('to_date')
                    end_date = ceil_strdate(to_date, 'end')

                campaign_id = variable_value(request, 'campaign_id')
                kwargs = {}
                if start_date and end_date:
                    kwargs['updated_date__range'] = (start_date, end_date)
                if start_date and end_date == '':
                    kwargs['updated_date__gte'] = start_date
                if start_date == '' and end_date:
                    kwargs['updated_date__lte'] = end_date
                if campaign_id and campaign_id != '0':
                    kwargs['campaign_id'] = campaign_id

                select_data = {"updated_date": "SUBSTR(CAST(updated_date as CHAR(30)),1,10)"}
                subscriber = Subscriber.objects \
                    .filter(**kwargs) \
                    .extra(select=select_data) \
                    .values('updated_date', 'status') \
                    .annotate(Count('updated_date')) \
                    .order_by('updated_date')

                for i in subscriber:
                    total_subscriber += i['updated_date__count']
                    if i['status'] == SUBSCRIBER_STATUS.PENDING:
                        total_pending += i['updated_date__count']
                    elif i['status'] == SUBSCRIBER_STATUS.PAUSE:
                        total_pause += i['updated_date__count']
                    elif i['status'] == SUBSCRIBER_STATUS.ABORT:
                        total_abort += i['updated_date__count']
                    elif i['status'] == SUBSCRIBER_STATUS.FAIL:
                        total_fail += i['updated_date__count']
                    elif i['status'] == SUBSCRIBER_STATUS.SENT:
                        total_sent += i['updated_date__count']
                    elif i['status'] == SUBSCRIBER_STATUS.IN_PROCESS:
                        total_in_process += i['updated_date__count']
                    elif i['status'] == SUBSCRIBER_STATUS.NOT_AUTHORIZED:
                        total_not_auth += i['updated_date__count']
                    else:
                        #status COMPLETED
                        total_completed += i['updated_date__count']

        ctx = RequestContext(request, {
            'form': form,
            'opts': opts,
            'total_subscriber': total_subscriber,
            'total_pending': total_pending,
            'total_pause': total_pause,
            'total_abort': total_abort,
            'total_fail': total_fail,
            'total_sent': total_sent,
            'total_in_process': total_in_process,
            'total_not_auth': total_not_auth,
            'total_completed': total_completed,
            'SUBSCRIBER_STATUS_NAME': SUBSCRIBER_STATUS_NAME,
            'model_name': opts.object_name.lower(),
            'app_label': APP_LABEL,
            'title': _('subscriber report'),
        })

        return render_to_response('admin/dialer_campaign/subscriber/subscriber_report.html',
               context_instance=ctx)

admin.site.register(Subscriber, SubscriberAdmin)
