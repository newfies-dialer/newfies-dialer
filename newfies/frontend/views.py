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

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,\
                                           permission_required
from django.contrib.auth.views import password_reset, password_reset_done,\
                        password_reset_confirm, password_reset_complete
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.db.models import Sum, Avg, Count

from django.conf import settings
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from notification import models as notification
from dialer_contact.models import Phonebook, Contact
from dialer_campaign.models import Campaign, CampaignSubscriber
from frontend.forms import LoginForm, DashboardForm
from dialer_campaign.function_def import calculate_date, date_range, \
                        user_dialer_setting_msg
from dialer_cdr.models import VoIPCall
from common.common_functions import current_view
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
import time
from frontend.constants import COLOR_DISPOSITION


def logout_view(request):
    try:
        del request.session['has_notified']
    except KeyError:
        pass

    logout(request)
    # set language cookie
    response = HttpResponseRedirect('/')
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME,
                        request.LANGUAGE_CODE)
    return response


def login_view(request):
    """Check User credentials

    **Attributes**:

        * ``form`` - LoginForm
        * ``template`` - frontend/index.html

    **Logic Description**:

        * Submitted user credentials need to be checked. If it is not valid
          then the system will redirect to the login page.
        * If submitted user credentials are valid then system will redirect to
          the dashboard.
    """
    template = 'frontend/index.html'
    errorlogin = ''

    if request.method == 'POST':
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            cd = loginform.cleaned_data
            user = authenticate(username=cd['user'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.session['has_notified'] = False
                    # Redirect to a success page (dashboard).
                    return HttpResponseRedirect('/dashboard/')
                else:
                    # Return a 'disabled account' error message
                    errorlogin = _('Disabled Account')
            else:
                # Return an 'invalid login' error message.
                errorlogin = _('Invalid Login.')
        else:
            # Return an 'Valid User Credentials' error message.
            errorlogin = _('Enter Valid User Credentials.')
    else:
        loginform = LoginForm()

    data = {
        'module': current_view(request),
        'loginform': loginform,
        'errorlogin': errorlogin,
        'is_authenticated': request.user.is_authenticated(),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }

    return render_to_response(template, data,
           context_instance=RequestContext(request))


def notice_count(request):
    """Get count of logged in user's notifications"""
    try:
        notice_count = notification.Notice.objects\
                            .filter(
                                recipient=request.user,
                                unseen=1)\
                            .count()
    except:
        notice_count = ''
    return notice_count


def index(request):
    """Index view of the Customer Interface

    **Attributes**:

        * ``form`` - LoginForm
        * ``template`` - frontend/index.html
    """
    template = 'frontend/index.html'
    errorlogin = ''
    data = {'module': current_view(request),
            'user': request.user,
            'notice_count': notice_count(request),
            'loginform': LoginForm(),
            'errorlogin': errorlogin,
            'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }

    return render_to_response(template, data,
           context_instance=RequestContext(request))


def pleaselog(request):
    template = 'frontend/index.html'

    data = {
        'loginform': LoginForm(),
        'notlogged': True,
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def permission_denied(request):
    """Notify user about their access permission"""
    template = 'frontend/permission_denied.html'
    data = {
        'error': _('You don`t have permission to view'),
    }
    return render_to_response(template, data,
        context_instance=RequestContext(request))


@permission_required('dialer_campaign.view_dashboard', login_url='/permission_denied/')
@login_required
def customer_dashboard(request, on_index=None):
    """Customer dashboard gives the following information

        * No of Campaigns for logged in user
        * Total phonebook contacts
        * Total Campaigns contacts
        * Amount of contact reached today
        * Disposition of calls via pie chart
        * Call records & Duration of calls are shown on graph by days/hours

    **Attributes**:

        * ``template`` - frontend/dashboard.html
        * ``form`` - DashboardForm
    """

    # All campaign for logged in User
    campaign = Campaign.objects.filter(user=request.user)
    campaign_count = campaign.count()

    # Contacts count which are active and belong to those phonebook(s) which is
    # associated with all campaign
    campaign_id_list = ''
    pb_active_contact_count = 0
    for i in campaign:
        pb_active_contact_count +=\
            Contact.objects.filter(phonebook__campaign=i.id, status=1).count()
        campaign_id_list += str(i.id) + ","
    campaign_id_list = campaign_id_list[:-1]

    # Phonebook list for logged in user
    phonebook_id_list = Phonebook.objects.values_list('id')\
                                .filter(user=request.user)

    # Total count of contacts for logged in user
    total_of_phonebook_contacts = 0
    if phonebook_id_list:
        total_of_phonebook_contacts = \
            Contact.objects.filter(phonebook__in=phonebook_id_list).count()

    form = DashboardForm(request.user)
    total_data = []  # for humblefinance chart
    final_calls = []  # for pie chart
    min_limit = ''
    max_limit = ''
    total_duration_sum = 0
    total_call_count = 0
    total_answered = 0
    total_not_answered = 0
    total_busy = 0
    total_cancel = 0
    total_congestion = 0
    total_chanunavail = 0
    total_dontcall = 0
    total_torture = 0
    total_invalidargs = 0
    total_noroute = 0
    total_forbidden = 0
    select_graph_for = 'Call Count'  # default (or Duration)
    search_type = 4  # default Last 24 hours
    selected_campaign = ''
    seven_days_option_list = []
    seven_days_result_set = []
    twelve_hour_list = []
    common_hour_result_set = []
    only_data_date_list = []

    if campaign_id_list:
        selected_campaign = campaign_id_list[0]  # default campaign id

    # selected_campaign should not be empty
    if selected_campaign:
        if request.method == 'POST':
            form = DashboardForm(request.user, request.POST)
            selected_campaign = request.POST['campaign']
            search_type = request.POST['search_type']

            if request.POST.get('call_count_button'):
                select_graph_for = request.POST['call_count_button']
            if request.POST.get('duration_button'):
                select_graph_for = request.POST['duration_button']

        end_date = datetime.today()
        start_date = calculate_date(search_type)

        min_limit = time.mktime(start_date.timetuple())
        max_limit = time.mktime(end_date.timetuple())

        # date_length is used to do group by starting_date
        if int(search_type) >= 2:  # all options except 30 days
            date_length = 13
            if int(search_type) == 3:  # yesterday
                now = datetime.now()
                start_date = datetime(
                                now.year,
                                now.month,
                                now.day,
                                0, 0, 0, 0) - relativedelta(days=1)
                end_date = datetime(now.year,
                                    now.month,
                                    now.day,
                                    23, 59, 59, 999999) - relativedelta(days=1)
            if int(search_type) >= 5:
                date_length = 16
        else:
            date_length = 10  # Last 30 days option

        select_data = \
            {"starting_date": "SUBSTR(CAST(starting_date as CHAR(30)),1," + \
                              str(date_length) + ")"}

        # This calls list is used by pie chart
        calls = VoIPCall.objects\
                     .filter(callrequest__campaign=selected_campaign,
                             duration__isnull=False,
                             user=request.user,
                             starting_date__range=(start_date, end_date))\
                     .extra(select=select_data)\
                     .values('starting_date', 'disposition')\
                     .annotate(Sum('duration'))\
                     .annotate(Avg('duration'))\
                     .annotate(Count('starting_date'))\
                     .order_by('starting_date')

        final_calls = []
        for i in calls:
            # convert unicode date string into date
            starting_datetime = parser.parse(str(i['starting_date']))
            final_calls.append(
                    {
                    'starting_date': i['starting_date'],
                    'starting_datetime': \
                        time.mktime(starting_datetime.timetuple()),
                    'starting_date__count': i['starting_date__count'],
                    'duration__sum': i['duration__sum'],
                    'duration__avg': i['duration__avg'],
                    'disposition': i['disposition']
                    })

            if i['disposition'] == 'ANSWER':
                total_answered += i['starting_date__count']
            elif i['disposition'] == 'BUSY' or i['disposition'] == 'USER_BUSY':
                total_busy += i['starting_date__count']
            elif i['disposition'] == 'NOANSWER' \
                or i['disposition'] == 'NO_ANSWER':
                total_not_answered += i['starting_date__count']
            elif i['disposition'] == 'CANCEL':
                total_cancel += i['starting_date__count']
            elif i['disposition'] == 'CONGESTION':
                total_congestion += i['starting_date__count']
            elif i['disposition'] == 'CHANUNAVAIL':
                total_chanunavail += i['starting_date__count']
            elif i['disposition'] == 'DONTCALL':
                total_dontcall += i['starting_date__count']
            elif i['disposition'] == 'TORTURE':
                total_torture += i['starting_date__count']
            elif i['disposition'] == 'INVALIDARGS':
                total_invalidargs += i['starting_date__count']
            elif i['disposition'] == 'NOROUTE' \
                or i['disposition'] == 'NO_ROUTE':
                total_noroute += i['starting_date__count']
            else:
                total_forbidden += i['starting_date__count']  # FORBIDDEN

        # This part got from cdr-stats 'global report' used by humblefinance
        # following calls list is without dispostion & group by call date
        calls = VoIPCall.objects\
                     .filter(callrequest__campaign=selected_campaign,
                             duration__isnull=False,
                             user=request.user,
                             starting_date__range=(start_date, end_date))\
                     .extra(select=select_data)\
                     .values('starting_date').annotate(Sum('duration'))\
                     .annotate(Avg('duration'))\
                     .annotate(Count('starting_date'))\
                     .order_by('starting_date')

        mintime = start_date
        maxtime = end_date
        calls_dict = {}

        for data in calls:
            if int(search_type) >= 2:
                ctime = datetime(int(data['starting_date'][0:4]),
                                 int(data['starting_date'][5:7]),
                                 int(data['starting_date'][8:10]),
                                 int(data['starting_date'][11:13]),
                                 0,
                                 0,
                                 0)
                if int(search_type) >= 5:
                    ctime = datetime(int(data['starting_date'][0:4]),
                                 int(data['starting_date'][5:7]),
                                 int(data['starting_date'][8:10]),
                                 int(data['starting_date'][11:13]),
                                 int(data['starting_date'][14:16]),
                                 0,
                                 0)
            else:
                ctime = datetime(int(data['starting_date'][0:4]),
                                 int(data['starting_date'][5:7]),
                                 int(data['starting_date'][8:10]),
                                 0,
                                 0,
                                 0,
                                 0)
            if ctime > maxtime:
                maxtime = ctime
            elif ctime < mintime:
                mintime = ctime

            # all options except 30 days
            if int(search_type) >= 2:
                calls_dict[int(ctime.strftime("%Y%m%d%H"))] = \
                {'starting_date__count': data['starting_date__count'],
                 'duration__sum': data['duration__sum'],
                 'duration__avg': data['duration__avg'],
                 #'date_in_int': int(ctime.strftime("%Y%m%d%H")),
                 'starting_datetime': time.mktime(ctime.timetuple()),
                }
                seven_days_option_list.append({
                 'starting_date__count': data['starting_date__count'],
                 'starting_date': data['starting_date'],
                 'duration__sum': data['duration__sum'],
                 'duration__avg': data['duration__avg'],
                 'date_in_int': int(ctime.strftime("%Y%m%d%H")),
                 'starting_datetime': time.mktime(ctime.timetuple()),
                })
                only_data_date_list.append(ctime.strftime("%Y%m%d"))
                if int(search_type) >= 5:
                    twelve_hour_list.append({
                     'starting_date__count': data['starting_date__count'],
                     'starting_date': data['starting_date'],
                     'duration__sum': data['duration__sum'],
                     'duration__avg': data['duration__avg'],
                     'date_in_int': int(ctime.strftime("%Y%m%d%H%M")),
                     'starting_datetime': time.mktime(ctime.timetuple()),
                    })
                    only_data_date_list.append(ctime.strftime("%Y%m%d%H"))
            else:
                # Last 30 days option
                calls_dict[int(ctime.strftime("%Y%m%d"))] = \
                {'starting_date__count': data['starting_date__count'],
                 'duration__sum': data['duration__sum'],
                 'duration__avg': data['duration__avg'],
                 #'date_in_int': int(ctime.strftime("%Y%m%d")),
                 'starting_datetime': time.mktime(ctime.timetuple()),
                }

        dateList = date_range(mintime, maxtime, q=search_type)

        i = 0
        for date in dateList:
            # Yesterday & 24 hrs
            if int(search_type) >= 2:
                inttime = int(date.strftime("%Y%m%d%H"))
            else:  # Last 30 days
                inttime = int(date.strftime("%Y%m%d"))

            name_date = _(date.strftime("%B")) + " " + str(date.day) + \
                        ", " + str(date.year)

            if inttime in calls_dict.keys():
                total_data.append({
                    'count': i, 'day': date.day,
                    'month': date.month, 'year': date.year,
                    'date': name_date,
                    'starting_date__count': \
                        calls_dict[inttime]['starting_date__count'],
                    'duration__sum': calls_dict[inttime]['duration__sum'],
                    'duration__avg': calls_dict[inttime]['duration__avg'],
                    #'disposition': calls_dict[inttime]['disposition'],
                    'starting_date': calls_dict[inttime]['starting_datetime'],
                })

                # Extra part: To count total no of calls & their duration
                total_duration_sum = total_duration_sum + \
                                calls_dict[inttime]['duration__sum']
                total_call_count += calls_dict[inttime]['starting_date__count']
            else:
                date = parser.parse(str(date))
                total_data.append({
                       'count': i,
                       'day': date.day,
                       'month': date.month,
                       'year': date.year,
                       'date': name_date,
                       'starting_date__count': 0,
                       'duration__sum': 0,
                       'duration__avg': 0,
                       'disposition': '',
                       'starting_date': inttime,
                    })
            i += 1

        #  following sample code for Last 7 days option
        j = 0
        for date in dateList:
            inttime = str(date.strftime("%Y%m%d"))
            try:
                # Search inttime time only_data_date_list
                only_data_date_list.index(inttime)
                # current/previous date & count check to avoid duplicate
                # in final record set
                current_data_date = inttime
                previous_date = ''
                current_previous_count = 0

                for icalls in seven_days_option_list:
                    if previous_date == '':
                        previous_date = current_data_date

                    # check dateList date into seven_days_option_list date
                    if str(icalls['date_in_int'])[0:8] == inttime:
                        # compare previous & current date & count
                        if previous_date == str(icalls['date_in_int'])[0:8] \
                            and current_previous_count == 0:

                            # count increment
                            current_previous_count = current_previous_count + 1
                            # per day option
                            for option in [0, 6, 12, 18]:
                                temp_date = str(icalls['date_in_int'])[0:8]
                                name_date = \
                                datetime.strptime(str(temp_date[0:4] + '-' +
                                                      temp_date[4:6] + '-' +
                                                      temp_date[6:8] + ' ' +
                                                      str(option).zfill(2)),
                                                      '%Y-%m-%d %H')
                                name_date = _(date.strftime("%B")) + " " + \
                                                str(date.day) + \
                                                ", " + str(date.year)
                                seven_days_result_set.append(
                                    {
                                    'count': j,
                                    'day': temp_date[6:8],
                                    'month': temp_date[4:6],
                                    'year': temp_date[0:4],
                                    'date': name_date,
                                    'starting_date__count': 0,
                                    'duration__sum': 0,
                                    'duration__avg': 0,
                                    'starting_date': inttime,
                                    })
                                j += 1
                        else:
                            previous_date = str(icalls['date_in_int'])[0:8]
                            current_previous_count = current_previous_count + 1

                        # only add seven_days_option_list record
                        name_date = \
                        datetime.strptime(str(icalls['starting_date']),
                                        '%Y-%m-%d %H')

                        name_date = _(name_date.strftime("%B")) + " " + \
                                    str(name_date.day) + \
                                     ", " + str(date.year)
                        seven_days_result_set.append(
                            {
                            'count': j,
                            'day': temp_date[6:8],
                            'month': temp_date[4:6],
                            'year': temp_date[0:4],
                            'date': name_date,
                            'starting_date__count': \
                                    icalls['starting_date__count'],
                            'duration__sum': icalls['duration__sum'],
                            'duration__avg': icalls['duration__avg'],
                            })
                        j += 1
            except:
                # add data for dates which are not in seven_days_option_list
                inttime = datetime.strptime(str(inttime), '%Y%m%d')
                # per day option
                for option in [0, 6, 12, 18]:
                    temp_date = str(inttime)[0:4] + \
                                    str(inttime)[5:7] + \
                                    str(inttime)[8:10]
                    name_date = \
                    datetime.strptime(str(temp_date[0:4] + '-' +
                                          temp_date[4:6] + '-' +
                                          temp_date[6:8] + ' ' +
                                          str(option).zfill(2)),
                                          '%Y-%m-%d %H')
                    name_date = _(date.strftime("%B")) + " " + \
                                    str(date.day) + \
                                    ", " + str(date.year)
                    seven_days_result_set.append(
                        {
                        'count': j,
                        'day': temp_date[6:8],
                        'month': temp_date[4:6],
                        'year': temp_date[0:4],
                        'date': name_date,
                        'starting_date__count': 0,
                        'duration__sum': 0,
                        'duration__avg': 0,
                        'starting_date': inttime,
                        })
                    j += 1

        m = 0
        min_list = []
        # following code for Last 12 hrs / Last 6 hrs / Last hour option
        for date in dateList:
            inttime = str(date.strftime("%Y%m%d%H"))
            try:
                # Search inttime time twelve_hour_list
                only_data_date_list.index(inttime)
                # current/previous date & count check to avoid duplicate
                # in final record set
                current_data_date = inttime
                previous_date = ''
                current_previous_count = 0
                # last_hour_list = twelve_hour_list
                for icalls in twelve_hour_list:
                    if previous_date == '':
                        previous_date = current_data_date

                    # check dateList date into seven_days_option_list date
                    if str(icalls['date_in_int'])[0:10] == inttime:
                        # compare prvious & current date & count
                        if previous_date == str(icalls['date_in_int'])[0:10] \
                           and current_previous_count == 0:

                            # count increment
                            current_previous_count = current_previous_count + 1
                            # per day option
                            if int(search_type) == 5:
                                min_list = [0, 30]

                            if int(search_type) == 6:
                                min_list = [0, 15, 30, 45]

                            if int(search_type) == 7:
                                min_list = [i for i in range(60) if i % 5 == 0]

                            for option in min_list:
                                temp_date = str(icalls['date_in_int'])[0:10]
                                name_date = \
                                datetime.strptime(str(temp_date[0:4] + '-' +
                                                      temp_date[4:6] + '-' +
                                                      temp_date[6:8] + ' ' +
                                                      temp_date[9:11] + ':' +
                                                      str(option).zfill(2)),
                                                      '%Y-%m-%d %H:%M')
                                name_date = \
                                _(date.strftime("%B")) + " " +\
                                str(date.day) + ", " + str(date.year)
                                common_hour_result_set.append({'count': m,
                                                    'day': temp_date[6:8],
                                                    'month': temp_date[4:6],
                                                    'year': temp_date[0:4],
                                                    'date': name_date,
                                                    'starting_date__count': 0,
                                                    'duration__sum': 0,
                                                    'duration__avg': 0,
                                                    'starting_date': inttime,
                                                   })
                                m += 1
                        else:
                            previous_date = str(icalls['date_in_int'])[0:10]
                            current_previous_count = current_previous_count + 1

                        # only add data records
                        name_date = \
                        datetime.strptime(str(icalls['starting_date']),
                                            '%Y-%m-%d %H:%M')

                        name_date = _(name_date.strftime("%B")) + " " + \
                                    str(name_date.day) + \
                                    ", " + str(date.year)
                        common_hour_result_set.append({'count': m,
                                'day': temp_date[6:8],
                                'month': temp_date[4:6],
                                'year': temp_date[0:4],
                                'date': name_date,
                                'starting_date__count': \
                                    icalls['starting_date__count'],
                                'duration__sum': icalls['duration__sum'],
                                'duration__avg': icalls['duration__avg'],
                               })
                        m += 1
            except:
                # add data for dates which are not in seven_days_option_list
                inttime = datetime.strptime(str(inttime), '%Y%m%d%H')
                if int(search_type) == 5:
                    min_list = [0, 30]

                if int(search_type) == 6:
                    min_list = [0, 15, 30, 45]

                if int(search_type) == 7:
                    min_list = [i for i in range(60) if i % 5 == 0]

                for option in min_list:
                    temp_date = str(inttime)[0:4] + str(inttime)[5:7] + \
                                str(inttime)[8:10] + str(inttime)[11:13]
                    name_date = datetime.strptime(str(temp_date[0:4] + '-' +
                                    temp_date[4:6] + '-' +
                                    temp_date[6:8] + ' ' +
                                    temp_date[9:11] + ':' +
                                    str(option).zfill(2)), '%Y-%m-%d %H:%M')
                    name_date = _(date.strftime("%B")) + " " + \
                                str(date.day) + ", " + str(date.year)
                    common_hour_result_set.append({'count': m,
                                                   'day': temp_date[6:8],
                                                   'month': temp_date[4:6],
                                                   'year': temp_date[0:4],
                                                   'date': name_date,
                                                   'starting_date__count': 0,
                                                   'duration__sum': 0,
                                                   'duration__avg': 0,
                                                   'starting_date': inttime,
                                                   })
                    m += 1

        # total_data = seven_days_result_set (for last 7 days option)
        if int(search_type) == 2:
            total_data = seven_days_result_set

        # total_data = (Last 12 hrs / Last 6 hrs/ Last hour)
        if int(search_type) == 5 \
            or int(search_type) == 6 \
            or int(search_type) == 7:
            total_data = common_hour_result_set

    # Contacts which are successfully called for running campaign
    reached_contact = 0
    for i in campaign:
        now = datetime.now()
        start_date = datetime(now.year, now.month, now.day, 0, 0, 0, 0)
        end_date = datetime(now.year, now.month, now.day, 23, 59, 59, 999999)
        campaign_subscriber = CampaignSubscriber.objects\
                .filter(campaign=i.id,  # status=5,
                        updated_date__range=(start_date, end_date))\
                .count()
        reached_contact += campaign_subscriber

    template = 'frontend/dashboard.html'

    data = {
        'module': current_view(request),
        'form': form,
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
        'campaign_count': campaign_count,
        'total_of_phonebook_contacts': total_of_phonebook_contacts,
        'pb_active_contact_count': pb_active_contact_count,
        'reached_contact': reached_contact,
        'notice_count': notice_count(request),
        'total_data': total_data,  # for humblefinanace graph
        'final_calls': final_calls,  # for flot graph
        'min_limit': min_limit,
        'max_limit': max_limit,
        'select_graph_for': select_graph_for,
        'total_duration_sum': total_duration_sum,
        'total_call_count': total_call_count,
        'total_answered':  total_answered,
        'total_not_answered': total_not_answered,
        'total_busy': total_busy,
        #'total_others': total_others,
        'total_cancel': total_cancel,
        'total_congestion': total_congestion,
        'total_chanunavail': total_chanunavail,
        'total_dontcall': total_dontcall,
        'total_torture': total_torture,
        'total_invalidargs': total_invalidargs,
        'total_noroute': total_noroute,
        'total_forbidden': total_forbidden,
        'answered_color': COLOR_DISPOSITION['ANSWER'],
        'busy_color': COLOR_DISPOSITION['BUSY'],
        'not_answered_color': COLOR_DISPOSITION['NOANSWER'],
        'cancel_color': COLOR_DISPOSITION['CANCEL'],
        'congestion_color': COLOR_DISPOSITION['CONGESTION'],
        'chanunavail_color': COLOR_DISPOSITION['CHANUNAVAIL'],
        'dontcall_color': COLOR_DISPOSITION['DONTCALL'],
        'torture_color': COLOR_DISPOSITION['TORTURE'],
        'invalidargs_color': COLOR_DISPOSITION['INVALIDARGS'],
        'noroute_color': COLOR_DISPOSITION['NOROUTE'],
        'forbidden_color': COLOR_DISPOSITION['FORBIDDEN'],
    }
    if on_index == 'yes':
        return data
    return render_to_response(template, data,
           context_instance=RequestContext(request))


def cust_password_reset(request):
    """Use ``django.contrib.auth.views.password_reset`` view method for
    forgotten password on the Customer UI

    This method sends an e-mail to the user's email-id which is entered in
    ``password_reset_form``
    """
    if not request.user.is_authenticated():
        data = {'loginform': LoginForm()}
        return password_reset(request,
            template_name='frontend/registration/password_reset_form.html',
            email_template_name='frontend/registration/password_reset_email.html',
            post_reset_redirect='/password_reset/done/',
            from_email='newfies_admin@localhost.com',
            extra_context=data)
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_done(request):
    """Use ``django.contrib.auth.views.password_reset_done`` view method for
    forgotten password on the Customer UI

    This will show a message to the user who is seeking to reset their
    password.
    """
    if not request.user.is_authenticated():
        data = {'loginform': LoginForm()}
        return password_reset_done(request,
            template_name='frontend/registration/password_reset_done.html',
            extra_context=data)
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_confirm(request, uidb36=None, token=None):
    """Use ``django.contrib.auth.views.password_reset_confirm`` view method for
    forgotten password on the Customer UI

    This will allow a user to reset their password.
    """
    if not request.user.is_authenticated():
        data = {'loginform': LoginForm()}
        return password_reset_confirm(request, uidb36=uidb36, token=token,
        template_name='frontend/registration/password_reset_confirm.html',
        post_reset_redirect='/reset/done/',
        extra_context=data)
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_complete(request):
    """Use ``django.contrib.auth.views.password_reset_complete`` view method
    for forgotten password on theCustomer UI

    This shows an acknowledgement to the user after successfully resetting
    their password for the system.
    """
    if not request.user.is_authenticated():
        data = {'loginform': LoginForm()}
        return password_reset_complete(request,
        template_name='frontend/registration/password_reset_complete.html',
        extra_context=data)
    else:
        return HttpResponseRedirect("/")
