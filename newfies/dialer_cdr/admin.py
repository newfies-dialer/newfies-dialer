from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.views.main import ERROR_FLAG
from django.conf.urls.defaults import *
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext
from django.db.models import *
from dialer_cdr.models import *
from dialer_cdr.forms import *
from dialer_cdr.function_def import *
import csv
from genericadmin.admin import GenericAdminModelAdmin, GenericTabularInline


class CallrequestAdmin(GenericAdminModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a Callrequest."""
    content_type_whitelist = ('voice_app/voiceapp', 'survey/surveyapp', )
    fieldsets = (
        (_('Standard options'), {
            'fields': ('user', 'request_uuid',  'call_time', 'campaign',
                       'status','hangup_cause', 'callerid', 'phone_number',
                       'timeout', 'timelimit', 'call_type', 'aleg_gateway',
                       'content_type', 'object_id', ),
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('extra_data',  'extra_dial_string',
                       'campaign_subscriber'),
        }),
    )
    list_display = ('id', 'user', 'campaign', 'content_type', 'request_uuid', 
            'aleg_uuid', 'call_time', 'status', 'callerid', 'phone_number', 
            'call_type', 'num_attempt', 'last_attempt_time',)
    list_display_links = ('id', 'request_uuid', )
    list_filter = ['callerid', 'call_time', 'status', 'call_type']
    ordering = ('id', )
    search_fields  = ('request_uuid', )
admin.site.register(Callrequest, CallrequestAdmin)


class VoIPCallAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a VoIPCall."""
    can_add = False
    detail_title = _("Call Report")
    list_display = ('id', 'user_link', 'leg_type', 'used_gateway_link', 
                    'callid', 'callerid', 'phone_number', 'starting_date', 
                    'min_duration', 'billsec', 'disposition', 'hangup_cause',
                    'hangup_cause_q850')
    #list_filter = ['disposition', 'starting_date']

    def user_link(self, obj):
        """User link to user profile"""
        
        if obj.user.is_staff:
            url = reverse('admin:auth_staff_change', args=(obj.user_id,))
        else:
            url = reverse('admin:auth_customer_change', args=(obj.user_id,))
        return '<a href="%s"><b>%s</b></a>' %  (url, obj.user)
    user_link.allow_tags = True
    user_link.short_description = _('User')

    def used_gateway_link(self, obj):
        """Used gateway link to edit gateway detail"""
        if obj.used_gateway:
            url = reverse('admin:dialer_gateway_gateway_change',
                          args=(obj.used_gateway.id,))
            return '<a href="%s">%s</a>' %  (url, obj.used_gateway)
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
            (r'^export_voip_report/$',
             self.admin_site.admin_view(self.export_voip_report)),
        )
        return my_urls + urls

    
    def changelist_view(self, request, extra_context=None):
        """Override changelist_view method of django-admin for search parameters

        **Attributes**:

            * ``form`` - VoipSearchForm
            * ``template`` - admin/dialer_cdr/voipcall/change_list.html

        **Logic Description**:

            * VoIP report Record Listing with search option & Daily Call Report
              search Parameters: by date, by status and by billed.
        """
        opts = VoIPCall._meta
        app_label = opts.app_label


        ChangeList = self.get_changelist(request)
        try:
            cl = ChangeList(request, self.model, self.list_display, self.list_display_links,
                self.list_filter, self.date_hierarchy, self.search_fields,
                self.list_select_related, self.list_per_page, self.list_editable, self)
        except IncorrectLookupParameters:
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')


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

        formset = cl.formset = None
        cl.result_list = cl.result_list.filter(**kwargs).order_by('-starting_date')
        
        # Session variable is used to get record set with searched option
        # into export file
        request.session['voipcall_record_qs'] = \
        super(VoIPCallAdmin, self).queryset(request).filter(**kwargs)\
        .order_by('-starting_date')

        select_data = \
        {"starting_date": "SUBSTR(CAST(starting_date as CHAR(30)),1,10)"}
        total_data = ''
        # Get Total Records from VoIPCall Report table for Daily Call Report
        total_data = VoIPCall.objects.extra(select=select_data)\
                     .values('starting_date')\
                     .filter(**kwargs).annotate(Count('starting_date'))\
                     .annotate(Sum('duration'))\
                     .annotate(Avg('duration'))\
                     .order_by('-starting_date')

        # Following code will count total voip calls, duration
        if total_data.count() != 0:
            max_duration = \
            max([x['duration__sum'] for x in total_data])
            total_duration = \
            sum([x['duration__sum'] for x in total_data])
            total_calls = sum([x['starting_date__count'] for x in total_data])
            total_avg_duration = \
            (sum([x['duration__avg']\
            for x in total_data])) / total_data.count()
        else:
            max_duration = 0
            total_duration = 0
            total_calls = 0
            total_avg_duration = 0

        selection_note_all = ungettext('%(total_count)s selected',
            'All %(total_count)s selected', cl.result_count)
        
        ctx = {
            'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            'selection_note_all': selection_note_all % {'total_count': cl.result_count},
            'cl': cl,
            'form': form,
            'total_data': total_data.reverse(),
            'total_duration': total_duration,
            'total_calls': total_calls,
            'total_avg_duration': total_avg_duration,
            'max_duration': max_duration,
            'opts': opts,
            'model_name': opts.object_name.lower(),
            'app_label': _('VoIP Report'),
            'title': _('Call Report'),
        }
        return super(VoIPCallAdmin, self)\
               .changelist_view(request, extra_context=ctx)

    def export_voip_report(self, request):
        """Export a CSV file of VoIP call records

        **Important variable**:

            * request.session['voipcall_record_qs'] - stores voipcall query set

        **Exported fields**: [user, callid, callerid, phone_number,
                              starting_date, duration, disposition,
                              used_gateway]
        """
        # get the response object, this can be used as a stream.
        response = HttpResponse(mimetype='text/csv')
        # force download.
        response['Content-Disposition'] = 'attachment;filename=export.csv'
        # the csv writer
        writer = csv.writer(response)

        # super(VoIPCall_ReportAdmin, self).queryset(request)
        qs = request.session['voipcall_record_qs']

        writer.writerow(['user', 'callid', 'callerid',
                         'phone_number', 'starting_date', 'duration',
                         'disposition', 'gateway'])
        for i in qs:
            writer.writerow([i.user,
                             i.callid,
                             i.callerid,
                             i.phone_number,
                             i.starting_date,
                             i.duration,
                             get_disposition_name(i.disposition),
                             i.used_gateway,
                             ])
        return response
admin.site.register(VoIPCall, VoIPCallAdmin)
