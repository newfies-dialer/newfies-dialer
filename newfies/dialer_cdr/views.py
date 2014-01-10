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

from django.contrib.auth.decorators import login_required, \
    permission_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.db.models import Sum, Avg, Count
from django.conf import settings
from dialer_campaign.function_def import user_dialer_setting_msg
from dialer_cdr.models import VoIPCall
from dialer_cdr.constants import CDR_REPORT_COLUMN_NAME
from dialer_cdr.forms import VoipSearchForm
from common.common_functions import ceil_strdate, unset_session_var, \
    get_pagination_vars
from datetime import datetime
from django.utils.timezone import utc
import tablib


def get_voipcall_daily_data(voipcall_list):
    """Get voipcall daily data"""
    select_data = {"starting_date": "SUBSTR(CAST(starting_date as CHAR(30)),1,10)"}

    # Get Total Rrecords from VoIPCall Report table for Daily Call Report
    total_data = voipcall_list.extra(select=select_data) \
        .values('starting_date') \
        .annotate(Count('starting_date')) \
        .annotate(Sum('duration')) \
        .annotate(Avg('duration')) \
        .order_by('-starting_date')

    # Following code will count total voip calls, duration
    if total_data:
        max_duration = max([x['duration__sum'] for x in total_data])
        total_duration = sum([x['duration__sum'] for x in total_data])
        total_calls = sum([x['starting_date__count'] for x in total_data])
        total_avg_duration = (sum([x['duration__avg'] for x in total_data])) / total_calls
    else:
        max_duration = 0
        total_duration = 0
        total_calls = 0
        total_avg_duration = 0

    data = {
        'total_data': total_data,
        'total_duration': total_duration,
        'total_calls': total_calls,
        'total_avg_duration': total_avg_duration,
        'max_duration': max_duration,
    }
    return data


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

        * ``request.session['voipcall_record_kwargs']`` - stores voipcall kwargs
    """
    sort_col_field_list = ['starting_date', 'leg_type', 'disposition',
                           'used_gateway', 'callerid', 'callid', 'phone_number',
                           'duration', 'billsec', 'amd_status']
    default_sort_field = 'starting_date'
    pagination_data = \
        get_pagination_vars(request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']
    start_page = pagination_data['start_page']
    end_page = pagination_data['end_page']

    search_tag = 1
    action = 'tabs-1'

    if request.method == 'POST':
        form = VoipSearchForm(request.user, request.POST)
        if form.is_valid():
            field_list = ['start_date', 'end_date',
                          'disposition', 'campaign_id', 'leg_type']
            unset_session_var(request, field_list)

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

            campaign_id = request.POST.get('campaign_id')
            if campaign_id and int(campaign_id) != 0:
                request.session['session_campaign_id'] = int(campaign_id)

            leg_type = request.POST.get('leg_type')
            if leg_type and leg_type != '':
                request.session['session_leg_type'] = leg_type

    post_var_with_page = 0
    try:
        if request.GET.get('page') or request.GET.get('sort_by'):
            post_var_with_page = 1
            start_date = request.session.get('session_start_date')
            end_date = request.session.get('session_end_date')
            disposition = request.session.get('session_disposition')
            campaign_id = request.session.get('session_campaign_id')
            leg_type = request.session.get('session_leg_type')
            form = VoipSearchForm(request.user,
                initial={'from_date': start_date.strftime('%Y-%m-%d'),
                       'to_date': end_date.strftime('%Y-%m-%d'),
                       'status': disposition,
                       'campaign_id': campaign_id,
                       'leg_type': leg_type})
        else:
            post_var_with_page = 1
            if request.method == 'GET':
                post_var_with_page = 0
    except:
        pass

    if post_var_with_page == 0:
        # default
        tday = datetime.utcnow().replace(tzinfo=utc)
        from_date = tday.strftime('%Y-%m-%d')
        to_date = tday.strftime('%Y-%m-%d')
        start_date = datetime(tday.year, tday.month, tday.day, 0, 0, 0, 0).replace(tzinfo=utc)
        end_date = datetime(tday.year, tday.month, tday.day, 23, 59, 59, 999999).replace(tzinfo=utc)
        disposition = 'all'
        campaign_id = 0
        leg_type = ''
        form = VoipSearchForm(request.user,
            initial={'from_date': from_date,
                    'to_date': to_date,
                    'status': disposition,
                    'campaign_id': campaign_id,
                    'leg_type': leg_type})
        # unset session var
        request.session['session_start_date'] = start_date
        request.session['session_end_date'] = end_date
        request.session['session_disposition'] = disposition
        request.session['session_campaign_id'] = ''
        request.session['session_leg_type'] = ''

    kwargs = {}
    if start_date and end_date:
        kwargs['starting_date__range'] = (start_date, end_date)
    if start_date and end_date == '':
        kwargs['starting_date__gte'] = start_date
    if start_date == '' and end_date:
        kwargs['starting_date__lte'] = end_date

    if disposition and disposition != 'all':
        kwargs['disposition__exact'] = disposition

    if campaign_id and int(campaign_id) != 0:
        kwargs['callrequest__campaign_id'] = campaign_id

    if leg_type and leg_type != '':
        kwargs['leg_type__exact'] = leg_type

    if not request.user.is_superuser:
        kwargs['user_id'] = request.user.id

    voipcall_list = VoIPCall.objects.filter(**kwargs)

    all_voipcall_list = voipcall_list.values_list('id', flat=True)

    # Session variable is used to get record set with searched option
    # into export file
    request.session['voipcall_record_kwargs'] = kwargs

    if request.GET.get('page') or request.GET.get('sort_by'):
        daily_data = request.session['voipcall_daily_data']
    else:
        if not voipcall_list:
            request.session['voipcall_daily_data'] = ''
        daily_data = get_voipcall_daily_data(voipcall_list)
        request.session['voipcall_daily_data'] = daily_data

    voipcall_list = voipcall_list.order_by(sort_order)[start_page:end_page]

    template = 'frontend/report/voipcall_report.html'
    data = {
        'form': form,
        'total_data': daily_data['total_data'],
        'total_duration': daily_data['total_duration'],
        'total_calls': daily_data['total_calls'],
        'total_avg_duration': daily_data['total_avg_duration'],
        'max_duration': daily_data['max_duration'],
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
        'all_voipcall_list': all_voipcall_list,
        'voipcall_list': voipcall_list,
        'PAGE_SIZE': PAGE_SIZE,
        'CDR_REPORT_COLUMN_NAME': CDR_REPORT_COLUMN_NAME,
        'col_name_with_order': pagination_data['col_name_with_order'],
        'search_tag': search_tag,
        'start_date': start_date,
        'end_date': end_date,
        'action': action,
        'AMD': settings.AMD,
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@login_required
def export_voipcall_report(request):
    """Export CSV file of VoIP call record

    **Important variable**:

        * ``request.session['voipcall_record_kwargs']`` - stores voipcall kwargs

    **Exported fields**: [user, callid, callerid, phone_number, starting_date,
                          duration, disposition, used_gateway]
    """
    format = request.GET['format']
    # get the response object, this can be used as a stream.
    response = HttpResponse(mimetype='text/' + format)

    # force download.
    response['Content-Disposition'] = 'attachment;filename=export.' + format

    # super(VoIPCall_ReportAdmin, self).queryset(request)
    if request.session.get('voipcall_record_kwargs'):
        kwargs = request.session['voipcall_record_kwargs']
        qs = VoIPCall.objects.filter(**kwargs)

        amd_status = ''
        if settings.AMD:
            amd_status = 'amd_status'

        headers = ('user', 'callid', 'callerid', 'phone_number',
                   'starting_date', 'duration', 'billsec',
                   'disposition', 'hangup_cause', 'hangup_cause_q850',
                   'used_gateway', amd_status)

        list_val = []
        for i in qs:
            gateway_used = i.used_gateway.name if i.used_gateway else ''
            amd_status = i.amd_status if settings.AMD else ''

            starting_date = i.starting_date
            if format == 'json' or format == 'xls':
                starting_date = str(i.starting_date)

            list_val.append((i.user.username,
                             i.callid,
                             i.callerid,
                             i.phone_number,
                             starting_date,
                             i.duration,
                             i.billsec,
                             i.disposition,
                             i.hangup_cause,
                             i.hangup_cause_q850,
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
