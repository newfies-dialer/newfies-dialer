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
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.views.main import ERROR_FLAG
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.db.models import Count
from django.utils.translation import ungettext
from dialer_campaign.function_def import dialer_setting_limit
from common.common_functions import variable_value
from models import SMSCampaign, SMSCampaignSubscriber, SMSMessage, SMSTemplate
from function_def import check_sms_dialer_setting,\
    sms_record_common_fun, sms_search_admin_form_fun
from forms import AdminSMSSearchForm
from genericadmin.admin import GenericAdminModelAdmin
from datetime import datetime
from django.utils.timezone import utc
import tablib


class SMSCampaignAdmin(GenericAdminModelAdmin):
    """
    Allows the administrator to view and modify certain attributes
    of a SMSCampaign.
    """
    fieldsets = (
        (_('Standard options'), {
            'fields': ('campaign_code', 'name', 'description', 'callerid',
                       'user', 'status', 'startingdate', 'expirationdate',
                       'sms_gateway', 'text_message',
                       'extra_data', 'phonebook',
                       ),
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('frequency', 'maxretry',
                       'intervalretry', 'imported_phonebook', 'daily_start_time',
                       'daily_stop_time', 'monday', 'tuesday', 'wednesday',
                       'thursday', 'friday', 'saturday', 'sunday')
        }),
    )
    list_display = ('id', 'name', 'campaign_code', 'user',
                    'startingdate', 'expirationdate', 'frequency',
                    'maxretry', 'sms_gateway', 'status',
                    'update_sms_campaign_status', 'count_contact_of_phonebook',
                    'sms_campaignsubscriber_detail', 'progress_bar')

    list_display_links = ('id', 'name', )
    #list_filter = ['user', 'status', 'startingdate', 'created_date']
    ordering = ('id', )
    filter_horizontal = ('phonebook',)

    def get_urls(self):
        urls = super(SMSCampaignAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^$', self.admin_site.admin_view(self.changelist_view)),
            (r'^add/$', self.admin_site.admin_view(self.add_view)),
        )
        return my_urls + urls

    def add_view(self, request, extra_context=None):
        """
        Override django add_view method for checking the dialer setting limit

        **Logic Description**:

            * Before adding sms campaign, check dialer setting limit if applicable
              to the user, if matched then the user will be redirected to
              the sms campaign list
        """
        # Check dialer setting limit
        # check Max Number of running sms campaigns
        if check_sms_dialer_setting(request, check_for="smscampaign"):
            msg = _("you have too many sms campaigns. Max allowed %(limit)s") \
                % {'limit': dialer_setting_limit(request, limit_for="smscampaign")}
            messages.error(request, msg)

            # campaign limit reached
            #common_send_notification(request, '3')
            return HttpResponseRedirect(reverse("admin:sms_campaign_campaign_changelist"))
        ctx = {}
        return super(SMSCampaignAdmin, self).add_view(request, extra_context=ctx)
admin.site.register(SMSCampaign, SMSCampaignAdmin)


class SMSCampaignSubscriberAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a SMSCampaignSubscriber."""
    list_display = ('id', 'contact', 'sms_campaign',
                    'last_attempt', 'count_attempt', 'duplicate_contact',
                    'contact_name', 'status', 'created_date')
    list_filter = ['sms_campaign', 'status', 'created_date', 'last_attempt']
    ordering = ('id', )

admin.site.register(SMSCampaignSubscriber, SMSCampaignSubscriberAdmin)


class SMSMessageAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a SMSMessage."""
    can_add = True
    detail_title = _("SMS report")
    list_display = ('sender', 'recipient_number', 'send_date', 'uuid',
                    'status', 'status_message', 'sms_gateway')
    ordering = ('-id', )

    def has_add_permission(self, request):
        """Remove add permission on SMSMessage Report model

        **Logic Description**:

            * Override django admin has_add_permission method to remove add
              permission on SMSMessage Report model
        """
        if not self.can_add:
            return False
        return super(SMSMessageAdmin, self).has_add_permission(request)

    def get_urls(self):
        urls = super(SMSMessageAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^$', self.admin_site.admin_view(self.changelist_view)),
            (r'^sms_daily_report/$', self.admin_site.admin_view(self.sms_daily_report)),
            (r'^export_sms_report/$', self.admin_site.admin_view(self.export_sms_report)),
        )
        return my_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Override changelist_view method of django-admin for search parameters

        **Attributes**:

            * ``form`` - AdminSMSSearchForm
            * ``template`` - admin/sms_module/smsmessage/sms_report.html

        **Logic Description**:

            * SMSMessage report Record Listing with search option
              search Parameters: by date, by status and by billed.
        """
        opts = SMSMessage._meta

        query_string = ''
        form = AdminSMSSearchForm()
        if request.method == 'POST':
            query_string = sms_search_admin_form_fun(request)
            return HttpResponseRedirect(
                "/admin/" + opts.app_label + "/" + opts.object_name.lower() + "/?" + query_string)
        else:
            status = ''
            from_date = ''
            to_date = ''
            smscampaign = ''
            if request.GET.get('send_date__gte'):
                from_date = variable_value(request, 'send_date__gte')
            if request.GET.get('send_date__lte'):
                to_date = variable_value(request, 'send_date__lte')[0:10]
            if request.GET.get('status__exact'):
                status = variable_value(request, 'status__exact')
            if request.GET.get('sms_campaign'):
                smscampaign = variable_value(request, 'sms_campaign')
            form = AdminSMSSearchForm(initial={'status': status,
                                               'from_date': from_date,
                                               'to_date': to_date,
                                               'smscampaign': smscampaign})

        ChangeList = self.get_changelist(request)
        try:
            cl = ChangeList(request, self.model, self.list_display,
                self.list_display_links, self.list_filter, self.date_hierarchy,
                self.search_fields, self.list_select_related,
                self.list_per_page, self.list_max_show_all, self.list_editable,
                self)
        except IncorrectLookupParameters:
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html',
                                          {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        kwargs = {}
        if request.META['QUERY_STRING'] == '':
            tday = datetime.utcnow().replace(tzinfo=utc)
            kwargs['send_date__gte'] = datetime(tday.year, tday.month, tday.day,
                0, 0, 0, 0).replace(tzinfo=utc)
            cl.root_query_set.filter(**kwargs)

        cl.formset = None
        # Session variable is used to get record set with searched option into export file
        request.session['admin_sms_record_qs'] = cl.root_query_set

        selection_note_all = ungettext('%(total_count)s selected',
            'All %(total_count)s selected', cl.result_count)

        ctx = {
            'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            'selection_note_all': selection_note_all % {'total_count': cl.result_count},
            'cl': cl,
            'form': form,
            'opts': opts,
            'model_name': opts.object_name.lower(),
            'app_label': _('SMS module'),
            'title': _('SMS report'),
        }
        return super(SMSMessageAdmin, self).changelist_view(request, extra_context=ctx)

    def sms_daily_report(self, request):
        opts = SMSMessage._meta
        kwargs = {}

        form = AdminSMSSearchForm()
        if request.method == 'POST':
            form = AdminSMSSearchForm(request.POST)
            kwargs = sms_record_common_fun(request)
            request.session['from_date'] = request.POST.get('from_date')
            request.session['to_date'] = request.POST.get('to_date')
            request.session['status'] = request.POST.get('status')
            request.session['smscampaign'] = request.POST.get('smscampaign')
        else:
            kwargs = sms_record_common_fun(request)
            tday = datetime.utcnow().replace(tzinfo=utc)
            if len(kwargs) == 0:
                kwargs['send_date__gte'] = datetime(tday.year, tday.month, tday.day,
                    0, 0, 0, 0).replace(tzinfo=utc)

        select_data = {"send_date": "SUBSTR(CAST(send_date as CHAR(30)),1,10)"}

        # Get Total Records from VoIPCall Report table for Daily Call Report
        total_data = SMSMessage.objects.extra(select=select_data)\
            .values('send_date').filter(**kwargs).annotate(Count('send_date'))\
            .order_by('-send_date')

        # Following code will count total sms calls, duration
        if total_data.count() != 0:
            total_sms = sum([x['send_date__count'] for x in total_data])
        else:
            total_sms = 0

        ctx = RequestContext(request, {
            'form': form,
            'total_data': total_data.reverse(),
            'total_sms': total_sms,
            'opts': opts,
            'model_name': opts.object_name.lower(),
            'app_label': _('SMS module'),
            'title': _('SMS aggregate report'),
        })

        return render_to_response(
            'admin/sms_module/smsmessage/sms_report.html', context_instance=ctx)

    def export_sms_report(self, request):
        """Export a CSV file of SMS records

        **Important variable**:

            * request.session['admin_sms_record_qs'] - stores sms query set

        **Exported fields**: ['sender', 'recipient_number', 'send_date',
                              'uuid', 'status', 'status_message', 'gateway']
        """
        format = request.GET['format']
        # get the response object, this can be used as a stream.
        response = HttpResponse(mimetype='text/' + format)

        # force download.
        response['Content-Disposition'] = 'attachment;filename=sms_export.' + format

        # super(SMSMessageAdmin, self).queryset(request)
        qs = request.session['admin_sms_record_qs']

        headers = ('sender', 'recipient_number', 'send_date', 'uuid',
                   'status', 'status_message', 'gateway')
        list_val = []

        for i in qs:
            gateway = i.gateway.name if i.gateway else ''
            send_date = i.send_date
            if format == 'json':
                send_date = str(i.send_date)

            list_val.append(
                (i.sender,
                 i.recipient_number,
                 send_date,
                 i.uuid,
                 i.status,
                 i.status_message,
                 gateway
                 ))

        data = tablib.Dataset(*list_val, headers=headers)

        if format == 'xls':
            response.write(data.xls)

        if format == 'csv':
            response.write(data.csv)

        if format == 'json':
            response.write(data.json)
        return response


class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ('label', 'sms_text', 'created_date')
    ordering = ('-id', )


admin.site.register(SMSMessage, SMSMessageAdmin)
admin.site.register(SMSTemplate, SMSTemplateAdmin)
