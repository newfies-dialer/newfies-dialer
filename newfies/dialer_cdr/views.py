#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.db.models import Sum, Avg, Count
from django.conf import settings
from dialer_cdr.models import VoIPCall
from dialer_cdr.constants import CDR_REPORT_COLUMN_NAME
from dialer_cdr.forms import VoipSearchForm
from django_lets_go.common_functions import ceil_strdate, unset_session_var, getvar, get_pagination_vars
from mod_utils.helper import Export_choice
# from dialer_cdr.constants import Export_choice
from datetime import datetime
from django.utils.timezone import utc
import tablib


def get_voipcall_daily_data(voipcall_list):
    """Get voipcall daily data"""
    select_data = {"starting_date": "SUBSTR(CAST(starting_date as CHAR(30)),1,10)"}

    # Get Total Rrecords from VoIPCall Report table for Daily Call Report
    total_data = voipcall_list.extra(select=select_data).values('starting_date')\
        .annotate(Count('starting_date'))\
        .annotate(Sum('duration'))\
        .annotate(Avg('duration'))\
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
        * ``template`` - dialer_cdr/voipcall_report.html

    **Logic Description**:

        * Get VoIP call list according to search parameters for loggedin user

    **Important variable**:

        * ``request.session['voipcall_record_kwargs']`` - stores voipcall kwargs
    """
    sort_col_field_list = ['starting_date', 'leg_type', 'disposition', 'used_gateway', 'callerid',
                           'callid', 'phone_number', 'duration', 'billsec', 'amd_status']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='starting_date')
    action = 'tabs-1'
    form = VoipSearchForm(request.user, request.POST or None)
    if form.is_valid():
        # Valid form
        field_list = ['start_date', 'end_date', 'disposition', 'campaign_id', 'leg_type']
        unset_session_var(request, field_list)

        from_date = getvar(request, 'from_date')
        to_date = getvar(request, 'to_date')
        start_date = ceil_strdate(str(from_date), 'start')
        end_date = ceil_strdate(str(to_date), 'end')

        converted_start_date = start_date.strftime('%Y-%m-%d')
        converted_end_date = end_date.strftime('%Y-%m-%d')
        request.session['session_start_date'] = converted_start_date
        request.session['session_end_date'] = converted_end_date

        disposition = getvar(request, 'disposition', setsession=True)
        campaign_id = getvar(request, 'campaign_id', setsession=True)
        leg_type = getvar(request, 'leg_type', setsession=True)
        form = VoipSearchForm(request.user, initial={'from_date': start_date.strftime('%Y-%m-%d'),
                                                     'to_date': end_date.strftime('%Y-%m-%d'),
                                                     'disposition': disposition,
                                                     'campaign_id': campaign_id,
                                                     'leg_type': leg_type})

    elif request.GET.get('page') or request.GET.get('sort_by'):
        # Pagination / Sort
        start_date = request.session.get('session_start_date')
        end_date = request.session.get('session_end_date')
        start_date = ceil_strdate(str(start_date), 'start')
        end_date = ceil_strdate(str(end_date), 'end')

        disposition = request.session.get('session_disposition')
        campaign_id = request.session.get('session_campaign_id')
        leg_type = request.session.get('session_leg_type')
        form = VoipSearchForm(request.user, initial={'from_date': start_date.strftime('%Y-%m-%d'),
                                                     'to_date': end_date.strftime('%Y-%m-%d'),
                                                     'disposition': disposition,
                                                     'campaign_id': campaign_id,
                                                     'leg_type': leg_type})
    else:
        # Default
        tday = datetime.utcnow().replace(tzinfo=utc)
        from_date = tday.strftime('%Y-%m-%d')
        to_date = tday.strftime('%Y-%m-%d')
        start_date = datetime(tday.year, tday.month, tday.day, 0, 0, 0, 0).replace(tzinfo=utc)
        end_date = datetime(tday.year, tday.month, tday.day, 23, 59, 59, 999999).replace(tzinfo=utc)
        disposition = 'all'
        campaign_id = 0
        leg_type = ''
        form = VoipSearchForm(request.user, initial={'from_date': from_date,
                                                     'to_date': to_date,
                                                     'disposition': disposition,
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

    voipcall_list = voipcall_list.order_by(pag_vars['sort_order'])[pag_vars['start_page']:pag_vars['end_page']]

    data = {
        'form': form,
        'total_data': daily_data['total_data'],
        'total_duration': daily_data['total_duration'],
        'total_calls': daily_data['total_calls'],
        'total_avg_duration': daily_data['total_avg_duration'],
        'max_duration': daily_data['max_duration'],
        'all_voipcall_list': all_voipcall_list,
        'voipcall_list': voipcall_list,
        'CDR_REPORT_COLUMN_NAME': CDR_REPORT_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
        'start_date': start_date,
        'end_date': end_date,
        'action': action,
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('dialer_cdr/voipcall_report.html', data, context_instance=RequestContext(request))


@login_required
def export_voipcall_report(request):
    """Export CSV file of VoIP call record

    **Important variable**:

        * ``request.session['voipcall_record_kwargs']`` - stores voipcall kwargs

    **Exported fields**: [user, callid, callerid, phone_number, starting_date,
                          duration, disposition, used_gateway]
    """
    format_type = request.GET['format']
    # get the response object, this can be used as a stream.
    response = HttpResponse(content_type='text/%s' % format_type)

    # force download.
    response['Content-Disposition'] = 'attachment;filename=export.%s' % format_type

    # super(VoIPCall_ReportAdmin, self).queryset(request)
    if request.session.get('voipcall_record_kwargs'):
        kwargs = request.session['voipcall_record_kwargs']
        qs = VoIPCall.objects.select_related('user__username').filter(**kwargs)

        amd_status = ''
        if settings.AMD:
            amd_status = 'amd_status'

        headers = ('user', 'callid', 'callerid', 'phone_number', 'starting_date', 'duration', 'billsec',
                   'disposition', 'hangup_cause', 'hangup_cause_q850', 'used_gateway', amd_status)

        list_val = []
        for i in qs:
            gateway_used = i.used_gateway.name if i.used_gateway else ''
            amd_status = i.amd_status if settings.AMD else ''

            starting_date = i.starting_date
            if format_type == Export_choice.JSON or format_type == Export_choice.XLS:
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

        if format_type == Export_choice.XLS:
            response.write(data.xls)
        elif format_type == Export_choice.CSV:
            response.write(data.csv)
        elif format_type == Export_choice.JSON:
            response.write(data.json)

    return response
