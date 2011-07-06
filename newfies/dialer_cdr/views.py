# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db.models import *
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from dialer_campaign.views import current_view, notice_count
from dialer_cdr.models import *
from dialer_cdr.forms import VoipSearchForm
from dialer_cdr.function_def import *
from datetime import *
import csv
import urllib
import ast


@login_required
def voipcall_report_grid(request):
    """VoIP Call list in json format for flexigrid

    **Model**: VoIPCall

    **Fields**: [id, user__username, used_gateway__name, callid, request_uuid,
                 callerid, phone_number, starting_date, sessiontime,
                 disposition]

    **Logic Description**:

        * Get VoIP call list according to search parameters
    """
    page = variable_value(request, 'page')
    rp = variable_value(request, 'rp')
    sortname = variable_value(request, 'sortname')
    sortorder = variable_value(request, 'sortorder')
    query = variable_value(request, 'query')
    qtype = variable_value(request, 'qtype')

    # page index
    if int(page) > 1:
        start_page = (int(page) - 1) * int(rp)
        end_page = start_page + int(rp)
    else:
        start_page = int(0)
        end_page = int(rp)

    sortorder_sign = ''
    if sortorder == 'desc':
        sortorder_sign = '-'


    # Search vars
    kwargs = {}
    from_date = ''
    start_date = ''
    to_date = ''
    end_date = ''
    disposition = 'all'

    # get querystring from URL
    q_arr = list(request.get_full_path().split('?'))
    j = 0
    q_para = ''

    # get para from querystring
    for i in q_arr:
        if j == 1:
            q_para = i
        j = j + 1

    if "from_date" in q_para:

        # decode query string
        decoded_string = urllib.unquote(q_para.decode("utf8"))

        temp_list = list(decoded_string.split('&'))
        for i in range(0, len(temp_list)):
            if temp_list[i].find('='):
                kwargs_list = list(temp_list[i].split('='))

                if kwargs_list[0] == 'from_date':
                    if kwargs_list[1]:
                        from_date = kwargs_list[1]
                        start_date = \
                        datetime(int(from_date[0:4]), int(from_date[5:7]),
                                 int(from_date[8:10]), 0, 0, 0, 0)

                if kwargs_list[0] == 'to_date':
                    if kwargs_list[1]:
                        to_date = kwargs_list[1]
                        end_date = \
                        datetime(int(to_date[0:4]), int(to_date[5:7]),
                                 int(to_date[8:10]), 23, 59, 59, 999999)

                if kwargs_list[0] == 'disposition':
                    if kwargs_list[1]:
                        disposition = kwargs_list[1]

        if start_date and end_date:
            kwargs['starting_date__range'] = (start_date, end_date)
        if start_date and end_date == '':
            kwargs['starting_date__gte'] = start_date
        if start_date == '' and end_date:
            kwargs['starting_date__lte'] = end_date

        if disposition != 'all':
            kwargs['disposition__exact'] = disposition

        if len(kwargs) == 0:
            tday = datetime.today()
            kwargs['starting_date__gte'] = datetime(tday.year,
                                                    tday.month,
                                                    tday.day, 0, 0, 0, 0)

    voipcall_list = VoIPCall.objects.values('id', 'user__username',
                    'used_gateway__name', 'callid', 'request_uuid', 'callerid',
                    'phone_number', 'starting_date', 'duration',
                    'billsec', 'disposition', 'hangup_cause',
                    'hangup_cause_q850').filter(**kwargs)

    count = voipcall_list.count()
    voipcall_list = \
        voipcall_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    update_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/page_edit.png);"'
    delete_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/delete.png);"'

    rows = [{'id': row['id'],
             'cell': [ row['user__username'],
                       row['used_gateway__name'],
                       row['callid'],
                       row['request_uuid'],
                       row['callerid'],
                       row['phone_number'],
                       row['starting_date'].strftime('%Y-%m-%d %H:%M:%S'),
                       #str(timedelta(seconds=row['duration'])), # original
                       row['duration'], # dilla test
                       #row['billsec'],
                       get_disposition_name(row['disposition']),
                       #row['hangup_cause'],
                       #row['hangup_cause_q850'],
                       ]} for row in voipcall_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    print rows
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@login_required
def voipcall_report(request):
    """VoIP Call Report

    **Attributes**:

        * ``form`` - VoipSearchForm
        * ``template`` - frontend/report/voipcall_report.html

    **Logic Description**:

        * Get VoIP call list according to search parameters

    **Important variable**:

        * ``request.session['voipcall_record_qs']`` - stores voipcall query set
    """
    kwargs = {}
    from_date = ''
    to_date = ''
    disposition = variable_value(request, 'status')
    form = VoipSearchForm()
    if request.method == 'POST':

        if request.POST['from_date'] != "":
            from_date = request.POST['from_date']
        if request.POST['to_date'] != "":
            to_date = request.POST['to_date']

        form = VoipSearchForm(request.POST)
        kwargs = voipcall_record_common_fun(request)
    else:
        tday = datetime.today()
        kwargs['starting_date__gte'] = datetime(tday.year,
                                               tday.month,
                                               tday.day, 0, 0, 0, 0)

    voipcall_list = \
    VoIPCall.objects.filter(**kwargs).order_by('-starting_date')

    # Session variable is used to get recrod set with searched option
    # into export file
    request.session['voipcall_record_qs'] = voipcall_list

    select_data = \
    {"starting_date": "SUBSTR(CAST(starting_date as CHAR(30)),1,10)"}
    total_data = ''
    # Get Total Rrecords from VoIPCall Report table for Daily Call Report
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

    template = 'frontend/report/voipcall_report.html'
    data = {
        'form': form,
        'from_date': from_date,
        'to_date': to_date,
        'disposition': disposition,
        'total_data': total_data.reverse(),
        'total_duration': total_duration,
        'total_calls': total_calls,
        'total_avg_duration': total_avg_duration,
        'max_duration': max_duration,
        'module': current_view(request),
        'notice_count': notice_count(request),
    }

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
        writer.writerow([i.user,
                         i.callid,
                         i.callerid,
                         i.phone_number,
                         i.starting_date,
                         i.duration,
                         i.billsec,
                         get_disposition_name(i.disposition),
                         i.hangup_cause,
                         i.hangup_cause_q850,
                         i.used_gateway,
                         ])
    return response
