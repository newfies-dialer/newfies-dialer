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

from django.contrib.auth.decorators import login_required,\
    permission_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.db.models import Sum, Avg, Count
from dialer_campaign.function_def import user_dialer_setting_msg
from dialer_cdr.models import VoIPCall
from dialer_cdr.constants import CDR_REPORT_COLUMN_NAME
from dialer_cdr.forms import VoipSearchForm
from utils.helper import notice_count
from common.common_functions import current_view, ceil_strdate,\
    get_pagination_vars
from datetime import datetime
import csv


@permission_required('dialer_cdr.view_call_detail_report', login_url='/')
@login_required
def voipcall_report(request):
    """VoIP Call Report

    **Attributes**:

        * ``form`` - VoipSearchForm
        * ``template`` - frontend/report/voipcall_report.html

    **Logic Description**:

        * Get VoIP call list according to search parameters for loggedin user

    **Important variable**:

        * ``request.session['voipcall_record_qs']`` - stores voipcall query set
    """
    sort_col_field_list = ['starting_date', 'leg_type', 'disposition',
                           'used_gateway', 'callerid', 'callid', 'phone_number',
                           'duration', 'billsec']
    default_sort_field = 'starting_date'
    pagination_data =\
        get_pagination_vars(request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']

    search_tag = 1
    form = VoipSearchForm()
    if request.method == 'POST':
        form = VoipSearchForm(request.POST)
        if form.is_valid():
            request.session['session_start_date'] = ''
            request.session['session_end_date'] = ''
            request.session['session_disposition'] = ''

            if request.POST.get('from_date'):
                # From
                from_date = request.POST['from_date']
                start_date = ceil_strdate(from_date, 'start')
                request.session['session_start_date'] = start_date

            if request.POST.get('to_date'):
                # To
                to_date = request.POST['to_date']
                end_date = ceil_strdate(to_date, 'end')
                request.session['session_end_date'] = end_date

            disposition = request.POST.get('status')
            if disposition != 'all':
                request.session['session_disposition'] = disposition

    post_var_with_page = 0
    try:
        if request.GET.get('page') or request.GET.get('sort_by'):
            post_var_with_page = 1
            start_date = request.session.get('session_start_date')
            end_date = request.session.get('session_end_date')
            disposition = request.session.get('session_disposition')
            form = VoipSearchForm(initial={'from_date': start_date.strftime('%Y-%m-%d'),
                                           'to_date': end_date.strftime('%Y-%m-%d'),
                                           'status': disposition})
        else:
            post_var_with_page = 1
            if request.method == 'GET':
                post_var_with_page = 0
    except:
        pass

    if post_var_with_page == 0:
        # default
        tday = datetime.today()
        from_date = tday.strftime('%Y-%m-%d')
        to_date = tday.strftime('%Y-%m-%d')
        start_date = datetime(tday.year, tday.month, tday.day, 0, 0, 0, 0)
        end_date = datetime(tday.year, tday.month, tday.day, 23, 59, 59, 999999)
        disposition = 'all'
        form = VoipSearchForm(initial={'from_date': from_date, 'to_date': to_date,
                                       'status': disposition})
        # unset session var
        request.session['session_from_date'] = from_date
        request.session['session_end_date'] = to_date
        request.session['session_disposition'] = disposition

    kwargs = {}
    if start_date and end_date:
        kwargs['starting_date__range'] = (start_date, end_date)
    if start_date and end_date == '':
        kwargs['starting_date__gte'] = start_date
    if start_date == '' and end_date:
        kwargs['starting_date__lte'] = end_date

    if disposition and disposition != 'all':
        kwargs['disposition__exact'] = disposition

    kwargs['user'] = User.objects.get(username=request.user)

    voipcall_list = VoIPCall.objects.filter(**kwargs).order_by(sort_order)
    #voipcall_list = voipcall_list[start_page:end_page]

    # Session variable is used to get record set with searched option
    # into export file
    request.session['voipcall_record_qs'] = voipcall_list


    select_data = {"starting_date": "SUBSTR(CAST(starting_date as CHAR(30)),1,10)"}

    # Get Total Rrecords from VoIPCall Report table for Daily Call Report
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
        total_avg_duration = (
            sum([x['duration__avg'] for x in total_data])) / total_data.count()
    else:
        max_duration = 0
        total_duration = 0
        total_calls = 0
        total_avg_duration = 0

    template = 'frontend/report/voipcall_report.html'
    data = {
        'form': form,
        'total_data': total_data.reverse(),
        'total_duration': total_duration,
        'total_calls': total_calls,
        'total_avg_duration': total_avg_duration,
        'max_duration': max_duration,
        'module': current_view(request),
        'notice_count': notice_count(request),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
        'voipcall_list': voipcall_list,
        'total_voipcall': voipcall_list.count(),
        'PAGE_SIZE': PAGE_SIZE,
        'CDR_REPORT_COLUMN_NAME': CDR_REPORT_COLUMN_NAME,
        'col_name_with_order': pagination_data['col_name_with_order'],
        'search_tag': search_tag,
        'start_date': start_date,
        'end_date': end_date,
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def export_voipcall_report(request):
    """Export CSV file of VoIP call record

    **Important variable**:

        * ``request.session['voipcall_record_qs']`` - stores voipcall query set

    **Exported fields**: [user, callid, callerid, phone_number, starting_date,
                          duration, disposition, used_gateway]
    """
    # get the response object, this can be used as a stream.
    response = HttpResponse(mimetype='text/csv')
    # force download.
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    # the csv writer
    writer = csv.writer(response)

    # super(VoIPCall_ReportAdmin, self).queryset(request)
    qs = request.session['voipcall_record_qs']

    writer.writerow(['user', 'callid', 'callerid', 'phone_number',
                     'starting_date', 'duration', 'billsec',
                     'disposition', 'hangup_cause', 'hangup_cause_q850',
                     'used_gateway'])
    for i in qs:
        gateway_used = i.used_gateway.name if i.used_gateway else ''
        writer.writerow([
            i.user,
            i.callid,
            i.callerid,
            i.phone_number,
            i.starting_date,
            i.duration,
            i.billsec,
            i.disposition,
            i.hangup_cause,
            i.hangup_cause_q850,
            gateway_used,
        ])
    return response
