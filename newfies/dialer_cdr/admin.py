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
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.views.main import ERROR_FLAG
from django.conf.urls.defaults import patterns
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext
from django.db.models import Sum, Avg, Count
from dialer_cdr.models import Callrequest, VoIPCall
from dialer_cdr.forms import VoipSearchForm
from dialer_cdr.function_def import voipcall_record_common_fun, \
                                    voipcall_search_admin_form_fun
from common.common_functions import variable_value
from genericadmin.admin import GenericAdminModelAdmin
from datetime import datetime
import csv


class CallrequestAdmin(GenericAdminModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a Callrequest."""
    content_type_whitelist = ('voice_app/voiceapp', 'survey/surveyapp', )
    fieldsets = (
        (_('Standard options'), {
            'fields': ('user', 'request_uuid', 'call_time', 'campaign',
                       'status', 'hangup_cause', 'callerid', 'phone_number',
                       'timeout', 'timelimit', 'call_type', 'aleg_gateway',
                       'content_type', 'object_id', ),
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('extra_data', 'extra_dial_string',
                       'campaign_subscriber'),
        }),
    )
    #NOTE : display user / content_type low the performance
    list_display = ('id', 'request_uuid', 'aleg_uuid', 'call_time',
                    'status', 'callerid', 'phone_number', 'call_type',
                    'num_attempt', 'last_attempt_time',)
    list_display_links = ('id', 'request_uuid', )
    list_filter = ['callerid', 'call_time', 'status', 'call_type', 'campaign']
    ordering = ('-id', )
    search_fields = ('request_uuid', )

admin.site.register(Callrequest, CallrequestAdmin)


class VoIPCallAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a VoIPCall."""
    can_add = False
    detail_title = _("Call Report")
    list_display = ('id', 'leg_type',
                    'callid', 'callerid', 'phone_number', 'starting_date',
                    'min_duration', 'billsec', 'disposition', 'hangup_cause',
                    'hangup_cause_q850')
    ordering = ('-id', )

    def user_link(self, obj):
        """User link to user profile"""

        if obj.user.is_staff:
            url = reverse('admin:auth_staff_change', args=(obj.user_id,))
        else:
            url = reverse('admin:auth_customer_change', args=(obj.user_id,))
        return '<a href="%s"><b>%s</b></a>' % (url, obj.user)
    user_link.allow_tags = True
    user_link.short_description = _('User')

    def used_gateway_link(self, obj):
        """Used gateway link to edit gateway detail"""
        if obj.used_gateway:
            url = reverse('admin:dialer_gateway_gateway_change',
                          args=(obj.used_gateway.id,))
            return '<a href="%s">%s</a>' % (url, obj.used_gateway)
    used_gateway_link.allow_tags = True
    used_gateway_link.short_description = _('Gateway used')

    def has_add_permission(self, request):
        """Remove add permission on VoIP Call Report model

        **Logic Description**:

            * Override django admin has_add_permission method to remove add
              permission on VoIP Call Report model
        """
        if not self.can_add:
            return False
        return super(VoIPCallAdmin, self).has_add_permission(request)

    def get_urls(self):
        urls = super(VoIPCallAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^$', self.admin_site.admin_view(self.changelist_view)),
            (r'^voip_report/$',
             self.admin_site.admin_view(self.voip_report)),
            (r'^export_voip_report/$',
             self.admin_site.admin_view(self.export_voip_report)),
        )
        return my_urls + urls

    def changelist_view(self, request, extra_context=None):
        """
        Override changelist_view method of django-admin for search parameters

        **Attributes**:

            * ``form`` - VoipSearchForm
            * ``template`` - admin/dialer_cdr/voipcall/change_list.html

        **Logic Description**:

            * VoIP report Record Listing with search option & Daily Call Report
              search Parameters: by date, by status and by billed.
        """
        opts = VoIPCall._meta
        query_string = ''
        form = VoipSearchForm()
        if request.method == 'POST':
            query_string = voipcall_search_admin_form_fun(request)
            return HttpResponseRedirect("/admin/" + opts.app_label + "/" + \
                opts.object_name.lower() + "/?" + query_string)
        else:
            status = ''
            from_date = ''
            to_date = ''
            if request.GET.get('starting_date__gte'):
                from_date = variable_value(request, 'starting_date__gte')
            if request.GET.get('starting_date__lte'):
                to_date = variable_value(request, 'starting_date__lte')[0:10]
            if request.GET.get('disposition__exact'):
                status = variable_value(request, 'disposition__exact')
            form = VoipSearchForm(initial={'status': status,
                                           'from_date': from_date,
                                           'to_date': to_date})

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
            tday = datetime.today()
            kwargs['starting_date__gte'] = datetime(tday.year,
                                                    tday.month,
                                                    tday.day, 0, 0, 0, 0)
            cl.root_query_set.filter(**kwargs)

        cl.formset = None
        # Session variable get record set with searched option into export file
        request.session['admin_voipcall_record_qs'] = cl.root_query_set

        selection_note_all = ungettext('%(total_count)s selected',
            'All %(total_count)s selected', cl.result_count)

        ctx = {
            'selection_note': \
                _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            'selection_note_all': \
                selection_note_all % {'total_count': cl.result_count},
            'cl': cl,
            'form': form,
            'opts': opts,
            'model_name': opts.object_name.lower(),
            'app_label': _('VoIP Report'),
            'title': _('Call Report'),
        }
        return super(VoIPCallAdmin, self)\
               .changelist_view(request, extra_context=ctx)

    def voip_report(self, request):
        opts = VoIPCall._meta
        kwargs = {}

        form = VoipSearchForm()
        if request.method == 'POST':
            form = VoipSearchForm(request.POST)
            kwargs = voipcall_record_common_fun(request)
            request.session['from_date'] = request.POST.get('from_date')
            request.session['to_date'] = request.POST.get('to_date')
            request.session['status'] = request.POST.get('status')
        else:
            kwargs = voipcall_record_common_fun(request)
            tday = datetime.today()
            if len(kwargs) == 0:
                kwargs['starting_date__gte'] = datetime(tday.year,
                                                        tday.month,
                                                        tday.day, 0, 0, 0, 0)

        select_data = \
            {"starting_date": "SUBSTR(CAST(starting_date as CHAR(30)),1,10)"}

        total_data = ''
        # Get Total Records from VoIPCall Report table for Daily Call Report
        total_data = VoIPCall.objects.extra(select=select_data)\
                     .values('starting_date')\
                     .filter(**kwargs)\
                     .annotate(Count('starting_date'))\
                     .annotate(Sum('duration'))\
                     .annotate(Avg('duration'))\
                     .order_by('-starting_date')

        # Following code will count total voip calls, duration
        if total_data.count() != 0:
            max_duration = \
                max([x['duration__sum'] for x in total_data])
            total_duration = \
                sum([x['duration__sum'] for x in total_data])
            total_calls = \
                sum([x['starting_date__count'] for x in total_data])
            total_avg_duration = \
                (sum([x['duration__avg']\
                    for x in total_data])) / total_data.count()
        else:
            max_duration = 0
            total_duration = 0
            total_calls = 0
            total_avg_duration = 0

        ctx = RequestContext(request, {
            'form': form,
            'total_data': total_data.reverse(),
            'total_duration': total_duration,
            'total_calls': total_calls,
            'total_avg_duration': total_avg_duration,
            'max_duration': max_duration,
            'opts': opts,
            'model_name': opts.object_name.lower(),
            'app_label': _('VoIP Report'),
            'title': _('Call Aggregate Report'),
        })

        return render_to_response('admin/dialer_cdr/voipcall/voip_report.html',
               context_instance=ctx)

    def export_voip_report(self, request):
        """Export a CSV file of VoIP call records

        **Important variable**:

            * request.session['admin_voipcall_record_qs'] - stores voipcall

        **Exported fields**: [user, callid, callerid, phone_number,
                              starting_date, duration, disposition,
                              used_gateway]
        """
        # get the response object, this can be used as a stream.
        response = HttpResponse(mimetype='text/csv')
        # force download.
        response['Content-Disposition'] = 'attachment;filename=export.csv'
        writer = csv.writer(response)

        # super(VoIPCall_ReportAdmin, self).queryset(request)
        qs = request.session['admin_voipcall_record_qs']

        writer.writerow(['user', 'callid', 'callerid',
                         'phone_number', 'starting_date', 'duration',
                         'disposition', 'gateway'])
        for i in qs:
            gateway_used = i.used_gateway.name if i.used_gateway else ''
            writer.writerow([i.user,
                             i.callid,
                             i.callerid,
                             i.phone_number,
                             i.starting_date,
                             i.duration,
                             i.disposition,
                             gateway_used,
                             ])
        return response

admin.site.register(VoIPCall, VoIPCallAdmin)
