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
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.views.main import ERROR_FLAG
from django.conf.urls import patterns
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext
from django.db.models import Sum, Avg, Count
from dialer_cdr.models import Callrequest, VoIPCall
from dialer_cdr.forms import AdminVoipSearchForm
from dialer_cdr.function_def import voipcall_record_common_fun, \
    voipcall_search_admin_form_fun
from common.common_functions import getvar
# from common.app_label_renamer import AppLabelRenamer
from genericadmin.admin import GenericAdminModelAdmin
from datetime import datetime
from django.utils.timezone import utc
import tablib

# AppLabelRenamer(native_app_label=u'dialer_cdr', app_label=_('Dialer CDR')).main()
APP_LABEL = _('VoIP report')


class CallrequestAdmin(GenericAdminModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a Callrequest."""
    content_type_whitelist = ('survey/survey', )
    fieldsets = (
        (_('standard options').capitalize(), {
            'fields': ('user', 'request_uuid', 'call_time', 'campaign',
                       'status', 'hangup_cause', 'callerid', 'phone_number',
                       'timeout', 'timelimit', 'call_type', 'aleg_gateway',
                       'content_type', 'object_id', ),
        }),
        (_('advanced options').capitalize(), {
            'classes': ('collapse', ),
            'fields': ('extra_data', 'extra_dial_string', 'subscriber', 'completed'),
        }),
    )
    #If we try to display user / content_type low the performance
    list_display = ('id', 'request_uuid', 'aleg_uuid', 'call_time',
                    'status', 'callerid', 'phone_number', 'call_type',
                    'completed', 'num_attempt', 'last_attempt_time', )
    list_display_links = ('id', 'request_uuid', )
    list_filter = ['callerid', 'call_time', 'status', 'call_type', 'campaign']
    ordering = ('-id', )
    search_fields = ('request_uuid', )

admin.site.register(Callrequest, CallrequestAdmin)


class VoIPCallAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a VoIPCall."""
    can_add = False
    detail_title = _("call report").title()
    list_display = ('id', 'leg_type', 'callid', 'callerid', 'phone_number',
                    'starting_date', 'min_duration', 'billsec', 'disposition',
                    'hangup_cause', 'hangup_cause_q850')
    valid_lookups = ('callrequest__campaign_id', )
    if settings.AMD:
        list_display += ('amd_status', )
    ordering = ('-id', )

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup.startswith(self.valid_lookups):
            return True
        return super(VoIPCallAdmin, self).lookup_allowed(lookup, *args, **kwargs)

    def user_link(self, obj):
        """User link to user profile"""

        if obj.user.is_staff:
            url = reverse('admin:auth_staff_change', args=(obj.user_id, ))
        else:
            url = reverse('admin:auth_customer_change', args=(obj.user_id, ))
        return '<a href="%s"><b>%s</b></a>' % (url, obj.user)
    user_link.allow_tags = True
    user_link.short_description = _('user').capitalize()

    def used_gateway_link(self, obj):
        """Used gateway link to edit gateway detail"""
        if obj.used_gateway:
            url = reverse('admin:dialer_gateway_gateway_change',
                          args=(obj.used_gateway.id, ))
            return '<a href="%s">%s</a>' % (url, obj.used_gateway)
    used_gateway_link.allow_tags = True
    used_gateway_link.short_description = _('gateway used').capitalize()

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
            (r'^voip_daily_report/$',
             self.admin_site.admin_view(self.voip_daily_report)),
            (r'^export_voip_report/$',
             self.admin_site.admin_view(self.export_voip_report)),
        )
        return my_urls + urls

    def changelist_view(self, request, extra_context=None):
        """
        Override changelist_view method of django-admin for search parameters

        **Attributes**:

            * ``form`` - AdminVoipSearchForm
            * ``template`` - admin/dialer_cdr/voipcall/change_list.html

        **Logic Description**:

            * VoIP report Record Listing with search option & Daily Call Report
              search Parameters: by date, by status and by billed.
        """
        opts = VoIPCall._meta
        query_string = ''
        form = AdminVoipSearchForm()
        if request.method == 'POST':
            # Session variable get record set with searched option into export file
            request.session['admin_voipcall_record_kwargs'] = voipcall_record_common_fun(request)

            query_string = voipcall_search_admin_form_fun(request)
            return HttpResponseRedirect("/admin/%s/%s/?%s"
                % (opts.app_label, opts.object_name.lower(), query_string))
        else:
            status = ''
            from_date = ''
            to_date = ''
            campaign_id = ''
            leg_type = ''

            from_date = getvar(request, 'starting_date__gte')
            to_date = getvar(request, 'starting_date__lte')[0:10]
            status = getvar(request, 'disposition__exact')
            campaign_id = getvar(request, 'callrequest__campaign_id')
            leg_type = getvar(request, 'leg_type__exact')

            form = AdminVoipSearchForm(initial={'status': status,
                                                'from_date': from_date,
                                                'to_date': to_date,
                                                'campaign_id': campaign_id,
                                                'leg_type': leg_type})

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
            return HttpResponseRedirect('%s?%s=1' % (request.path, ERROR_FLAG))

        if request.META['QUERY_STRING'] == '':
            # Default
            # Session variable get record set with searched option into export file
            request.session['admin_voipcall_record_kwargs'] = voipcall_record_common_fun(request)

            query_string = voipcall_search_admin_form_fun(request)
            return HttpResponseRedirect("/admin/%s/%s/?%s"
                % (opts.app_label, opts.object_name.lower(), query_string))

        cl.formset = None

        selection_note_all = ungettext('%(total_count)s selected',
            'All %(total_count)s selected', cl.result_count)

        ctx = {
            'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            'selection_note_all': selection_note_all % {'total_count': cl.result_count},
            'cl': cl,
            'form': form,
            'opts': opts,
            'model_name': opts.object_name.lower(),
            'app_label': APP_LABEL,
            'title': _('call report'),
        }
        return super(VoIPCallAdmin, self).changelist_view(request, extra_context=ctx)

    def voip_daily_report(self, request):
        opts = VoIPCall._meta
        kwargs = {}
        if request.method == 'POST':
            form = AdminVoipSearchForm(request.POST)
            kwargs = voipcall_record_common_fun(request)
        else:
            kwargs = voipcall_record_common_fun(request)
            tday = datetime.today()
            form = AdminVoipSearchForm(initial={"from_date": tday.strftime("%Y-%m-%d"),
                                                "to_date": tday.strftime("%Y-%m-%d")})
            if len(kwargs) == 0:
                kwargs['starting_date__gte'] = datetime(tday.year, tday.month, tday.day,
                                                        0, 0, 0, 0).replace(tzinfo=utc)

        select_data = {"starting_date": "SUBSTR(CAST(starting_date as CHAR(30)),1,10)"}
        # Get Total Records from VoIPCall Report table for Daily Call Report
        total_data = VoIPCall.objects.extra(select=select_data) \
            .values('starting_date') \
            .filter(**kwargs) \
            .annotate(Count('starting_date')) \
            .annotate(Sum('duration')) \
            .annotate(Avg('duration')) \
            .order_by('-starting_date')

        # Following code will count total voip calls, duration
        if total_data:
            max_duration = max([x['duration__sum'] for x in total_data])
            total_duration = sum([x['duration__sum'] for x in total_data])
            total_calls = sum([x['starting_date__count'] for x in total_data])
            total_avg_duration = (sum([x['duration__avg']
                    for x in total_data])) / total_calls
        else:
            max_duration = 0
            total_duration = 0
            total_calls = 0
            total_avg_duration = 0

        ctx = RequestContext(request, {
            'form': form,
            'total_data': total_data,
            'total_duration': total_duration,
            'total_calls': total_calls,
            'total_avg_duration': total_avg_duration,
            'max_duration': max_duration,
            'opts': opts,
            'model_name': opts.object_name.lower(),
            'app_label': APP_LABEL,
            'title': _('call aggregate report'),
        })

        return render_to_response('admin/dialer_cdr/voipcall/voip_report.html',
               context_instance=ctx)

    def export_voip_report(self, request):
        """Export a CSV file of VoIP call records

        **Important variable**:

            * request.session['admin_voipcall_record_kwargs'] - stores voipcall kwargs

        **Exported fields**: [user, callid, callerid, phone_number,
                              starting_date, duration, disposition,
                              used_gateway]
        """
        # get the response object, this can be used as a stream.
        format = request.GET['format']
        response = HttpResponse(mimetype='text/' + format)
        # force download.
        response['Content-Disposition'] = 'attachment;filename=export.' + format

        # super(VoIPCall_ReportAdmin, self).queryset(request)
        kwargs = request.session['admin_voipcall_record_kwargs']
        qs = VoIPCall.objects.filter(**kwargs)

        amd_status = ''
        if settings.AMD:
            amd_status = 'amd_status'

        headers = ('user', 'callid', 'callerid', 'phone_number',
                   'starting_date', 'duration', 'billsec',
                   'disposition', 'used_gateway', amd_status)

        list_val = []
        for i in qs:
            gateway_used = i.used_gateway.name if i.used_gateway else ''
            amd_status = i.amd_status if settings.AMD else ''

            starting_date = i.starting_date
            if format == 'json':
                starting_date = str(i.starting_date)

            list_val.append((i.user.username,
                             i.callid,
                             i.callerid,
                             i.phone_number,
                             starting_date,
                             i.duration,
                             i.billsec,
                             i.disposition,
                             gateway_used,
                             amd_status))

        data = tablib.Dataset(*list_val, headers=headers)

        if format == 'xls':
            response.write(data.xls)

        if format == 'csv':
            response.write(data.csv)

        if format == 'json':
            response.write(data.json)

        return response

admin.site.register(VoIPCall, VoIPCallAdmin)
