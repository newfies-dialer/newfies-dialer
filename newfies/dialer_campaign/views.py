# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_reset, password_reset_done,\
password_reset_confirm, password_reset_complete
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.db.models import *
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.db.models import Q
from notification import models as notification
from dialer_campaign.models import *
from dialer_campaign.forms import *
from dialer_campaign.function_def import *
from dialer_campaign.tasks import collect_subscriber
from dialer_cdr.models import *
from inspect import stack, getmodule
from datetime import *
from dateutil import parser
import urllib
import qsstats
import csv
import ast

# Define disposition color
ANSWER_COLOR = '#8BEA00'
BUSY_COLOR = '#F40C27'
NOANSWER_COLOR = '#F40CD5'
CANCEL_COLOR = '#3216B0'
CONGESTION_COLOR = '#F9AA26'
CHANUNAVAIL_COLOR = '#7E8179'
DONTCALL_COLOR = '#5DD0C0'
TORTURE_COLOR = '#FFCE00'
INVALIDARGS_COLOR = '#9B5C00'
NOROUTE_COLOR = '#057D9F'
FORBIDDEN_COLOR = '#A61700'


def current_view(request):
    name = getmodule(stack()[1][0]).__name__
    return stack()[1][3]


@login_required
def customer_dashboard(request, on_index=None):
    """Customer dashboard gives the following information

        * No of Campaigns for logged in user
        * Total phonebook contacts
        * Total Campaigns contacts
        * Amount of contact reached today
        * Disposition of calls via pie chart
        * Call records & Duration of calls are shown on graph by days/hours basis.

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
    campaign_phonebbok_active_contact_count = 0
    for i in campaign:
        campaign_phonebbok_active_contact_count +=\
        Contact.objects.filter(phonebook__campaign=i.id, status=1).count()
        campaign_id_list += str(i.id) + ","
    campaign_id_list = campaign_id_list[:-1]

    # Phonebook list for logged in user
    phonebook_id_list = ''
    phonebook_objs = Phonebook.objects.filter(user=request.user)
    for i in phonebook_objs:
        phonebook_id_list += str(i.id) + ","
    phonebook_id_list = phonebook_id_list[:-1]

    # Total count of contacts for logged in user
    total_of_phonebook_contacts = 0
    if phonebook_id_list:
        total_of_phonebook_contacts = \
        Contact.objects\
        .extra(where=['phonebook_id IN (%s) ' % phonebook_id_list]).count()

    form = DashboardForm(request.user)
    total_data = [] # for humblefinance chart
    final_calls = [] # for pie chart
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
    total_forbiden = 0
    select_graph_for = 'Call Count'  # default (or Duration)
    search_type = 4  # default Last 24 hours
    selected_campaign = ''
    seven_days_option_list = []
    seven_days_result_set = []
    only_data_date_list = []
    if campaign_id_list:
        selected_campaign = campaign_id_list[0] # default campaign id

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

        import time
        min_limit = time.mktime(start_date.timetuple())
        max_limit = time.mktime(end_date.timetuple())

        # date_length is used to do group by starting_date
        if int(search_type) >= 2: # all options except 30 days
            date_length = 13
        else:
            date_length = 10 # Last 30 days option

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
                     .values('starting_date', 'disposition').annotate(Sum('duration'))\
                     .annotate(Avg('duration'))\
                     .annotate(Count('starting_date'))\
                     .order_by('starting_date')

        final_calls = []
        for i in calls:
            # convert unicode date string into date
            starting_datetime = parser.parse(str(i['starting_date']))
            final_calls.append({'starting_date': i['starting_date'],
                                'starting_datetime': \
                                    time.mktime(starting_datetime.timetuple()),
                                'starting_date__count': i['starting_date__count'],
                                'duration__sum': i['duration__sum'],
                                'duration__avg': i['duration__avg'],
                                'disposition': i['disposition']
                                })
            if i['disposition'] == 'ANSWER':
                total_answered = total_answered + 1
            elif i['disposition'] == 'BUSY':
                total_busy = total_busy + 1
            elif i['disposition'] == 'NOANSWER':
                total_not_answered = total_not_answered + 1
            elif i['disposition'] == 'CANCEL':
                total_cancel = total_cancel + 1
            elif i['disposition'] == 'CONGESTION':
                total_congestion = total_congestion + 1
            elif i['disposition'] == 'CHANUNAVAIL':
                total_chanunavail = total_chanunavail + 1
            elif i['disposition'] == 'DONTCALL':
                total_dontcall = total_dontcall + 1
            elif i['disposition'] == 'TORTURE':
                total_torture = total_torture + 1
            elif i['disposition'] == 'INVALIDARGS':
                total_invalidargs = total_invalidargs + 1
            elif i['disposition'] == 'NOROUTE':
                total_noroute = total_noroute + 1
            else:
                total_forbiden = total_forbiden + 1 # FORBIDDEN

        # following part got from cdr-stats 'global report' used by humblefinance
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
                                 0, # int(data['starting_date'][14:16])
                                 0, # int(data['starting_date'][17:19])
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
                {'starting_date__count':data['starting_date__count'],
                 'duration__sum':data['duration__sum'],
                 'duration__avg':data['duration__avg'],
                 #'date_in_int': int(ctime.strftime("%Y%m%d%H")),
                 'starting_datetime': time.mktime(ctime.timetuple()),
                }
                seven_days_option_list.append({
                 'starting_date__count':data['starting_date__count'],
                 'starting_date':data['starting_date'],
                 'duration__sum':data['duration__sum'],
                 'duration__avg':data['duration__avg'],
                 'date_in_int': int(ctime.strftime("%Y%m%d%H")),
                 'starting_datetime': time.mktime(ctime.timetuple()),
                })
                only_data_date_list.append(ctime.strftime("%Y%m%d"))
            else:
                # Last 30 days option
                calls_dict[int(ctime.strftime("%Y%m%d"))] = \
                {'starting_date__count':data['starting_date__count'],
                 'duration__sum':data['duration__sum'],
                 'duration__avg':data['duration__avg'],
                 #'date_in_int': int(ctime.strftime("%Y%m%d")),
                 'starting_datetime': time.mktime(ctime.timetuple()),
                }

        dateList = date_range(mintime, maxtime, q=search_type)
        #for i in seven_days_option_list:
        #    print i

        i = 0
        for date in dateList:
            # all options except 30 days
            if int(search_type) >= 2:
                inttime = int(date.strftime("%Y%m%d%H"))
                inttime_seven_days = int(date.strftime("%Y%m%d"))
            else:
                inttime = int(date.strftime("%Y%m%d"))

            name_date = _(date.strftime("%B")) + " " + str(date.day) + \
                        ", " + str(date.year)

            if inttime in calls_dict.keys():
                total_data.append({'count': i, 'day': date.day,
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
                total_duration_sum = \
                total_duration_sum + calls_dict[inttime]['duration__sum']
                total_call_count = total_call_count + \
                              calls_dict[inttime]['starting_date__count']
            else:
                date = parser.parse(str(date))
                total_data.append({'count':i, 'day':date.day,
                                   'month':date.month, 'year':date.year,
                                   'date':name_date ,
                                   'starting_date__count':0,
                                   'duration__sum':0, 'duration__avg':0,
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
            # current/previous date & count check to avoid duplicate records
            # in final record set
            current_data_date = inttime
            previuos_data_date = ''
            current_previous_count = 0

            for calls_itme in seven_days_option_list:
                if previuos_data_date == '':
                    previuos_data_date = current_data_date

                # check dateList date into seven_days_option_list date
                if str(calls_itme['date_in_int'])[0:8] == inttime:
                    # compare prvious & current date & count
                    if previuos_data_date == str(calls_itme['date_in_int'])[0:8] \
                       and current_previous_count == 0:

                        # count increment
                        current_previous_count = current_previous_count + 1
                        # per day option
                        for option in [0, 6, 12, 18]:
                            temp_date = str(calls_itme['date_in_int'])[0:8]
                            if option == 0:
                                name_date = \
                                datetime.strptime(str(temp_date[0:4] + '-' +
                                                      temp_date[4:6] + '-' +
                                                      temp_date[6:8] + ' 00'),
                                                      '%Y-%m-%d %H')
                            if option == 6:
                                name_date = \
                                datetime.strptime(str(temp_date[0:4] + '-' +
                                                      temp_date[4:6] + '-' +
                                                      temp_date[6:8] + ' 06'),
                                                      '%Y-%m-%d %H')
                            if option == 12:
                                name_date = \
                                datetime.strptime(str(temp_date[0:4] + '-' +
                                                      temp_date[4:6] + '-' +
                                                      temp_date[6:8] + ' 12'),
                                                      '%Y-%m-%d %H')
                            if option == 18:
                                name_date = \
                                datetime.strptime(str(temp_date[0:4] + '-' +
                                                      temp_date[4:6] + '-' +
                                                      temp_date[6:8] + ' 18'),
                                                      '%Y-%m-%d %H')
                            name_date = _(date.strftime("%B")) + " " + str(date.day) + \
                                         ", " + str(date.year)
                            seven_days_result_set.append({'count':j,
                                                'day': temp_date[6:8],
                                                'month':temp_date[4:6],
                                                'year': temp_date[0:4],
                                                'date':name_date ,
                                                'starting_date__count':0,
                                                'duration__sum':0,
                                                'duration__avg':0,
                                                'starting_date': inttime,
                                               })
                            j = j + 1
                    else:
                        previuos_data_date = str(calls_itme['date_in_int'])[0:8]
                        current_previous_count = current_previous_count + 1

                    # only add seven_days_option_list record
                    name_date = \
                    datetime.strptime(str(calls_itme['starting_date']), '%Y-%m-%d %H')

                    name_date = _(name_date.strftime("%B")) + " " + str(name_date.day) + \
                                 ", " + str(date.year)
                    seven_days_result_set.append({'count': j,
                            'day': temp_date[6:8], 'month':temp_date[4:6],
                            'year': temp_date[0:4], 'date':name_date ,
                            'starting_date__count': \
                                calls_itme['starting_date__count'],
                            'duration__sum': calls_itme['duration__sum'],
                            'duration__avg': calls_itme['duration__avg'],
                           })
                    j = j + 1
        except:
            # add data for dates which are not in seven_days_option_list
            inttime = datetime.strptime(str(inttime), '%Y%m%d')
            # per day option 
            for option in [0, 6, 12, 18]:
                temp_date = str(inttime)[0:4] + str(inttime)[5:7] + str(inttime)[8:10]
                if option == 0:
                    name_date = \
                    datetime.strptime(str(temp_date[0:4] + '-' +
                                          temp_date[4:6] + '-' +
                                          temp_date[6:8] + ' 00'),
                                          '%Y-%m-%d %H')
                if option == 6:
                    name_date = \
                    datetime.strptime(str(temp_date[0:4] + '-' +
                                          temp_date[4:6] + '-' +
                                          temp_date[6:8] + ' 06'),
                                          '%Y-%m-%d %H')
                if option == 12:
                    name_date = \
                    datetime.strptime(str(temp_date[0:4] + '-' +
                                          temp_date[4:6] + '-' +
                                          temp_date[6:8] + ' 12'),
                                          '%Y-%m-%d %H')
                if option == 18:
                    name_date = \
                    datetime.strptime(str(temp_date[0:4] + '-' +
                                          temp_date[4:6] + '-' +
                                          temp_date[6:8] + ' 18'),
                                          '%Y-%m-%d %H')
                name_date = _(date.strftime("%B")) + " " + str(date.day) + \
                             ", " + str(date.year)
                seven_days_result_set.append({'count':j, 'day': temp_date[6:8],
                                        'month':temp_date[4:6], 'year': temp_date[0:4],
                                        'date':name_date ,
                                        'starting_date__count':0,
                                        'duration__sum':0, 'duration__avg':0,
                                        'starting_date': inttime,
                                       })
                j = j + 1


    # total_data = seven_days_result_set (for last 7 days option)
    if int(search_type) == 2:
        total_data = seven_days_result_set

    # Last 12 hours option
    for date in dateList:
        print date
    # Contacts which are successfully called for running campaign
    reached_contact = 0
    for i in campaign:
        campaign_subscriber = CampaignSubscriber.objects\
        .filter(campaign=i.id, status=5,
                updated_date__range=(start_date, end_date)).count()
        reached_contact += campaign_subscriber

    template = 'frontend/dashboard.html'

    data = {
        'module': current_view(request),
        'form': form,
        'campaign_count': campaign_count,
        'total_of_phonebook_contacts': total_of_phonebook_contacts,
        'campaign_phonebbok_active_contact_count': \
        campaign_phonebbok_active_contact_count,
        'reached_contact': reached_contact,
        'notice_count': notice_count(request),
        'total_data': total_data, # for humblefinanace graph
        'final_calls': final_calls, # for flot graph
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
        'total_forbiden': total_forbiden,
        'answered_color': ANSWER_COLOR,
        'busy_color': BUSY_COLOR,
        'not_answered_color': NOANSWER_COLOR ,
        'cancel_color': CANCEL_COLOR,
        'congestion_color': CONGESTION_COLOR,
        'chanunavail_color': CHANUNAVAIL_COLOR,
        'dontcall_color': DONTCALL_COLOR,
        'torture_color': TORTURE_COLOR,
        'invalidargs_color': INVALIDARGS_COLOR,
        'noroute_color': NOROUTE_COLOR,
        'forbiden_color': FORBIDDEN_COLOR,
    }
    if on_index == 'yes':
        return data
    return render_to_response(template, data,
           context_instance=RequestContext(request))


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
        try:
            action = request.POST['action']
        except (KeyError):
            action = "login"

        if action == "logout":
            logout(request)
        else:
            loginform = LoginForm(request.POST)
            if loginform.is_valid():
                cd = loginform.cleaned_data
                user = authenticate(username=cd['user'],
                                    password=cd['password'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        # Redirect to a success page (dashboard).
                        return \
                        HttpResponseRedirect('/dashboard/')
                    else:
                        # Return a 'disabled account' error message
                        errorlogin = _('Disabled Account') #True
                else:
                    # Return an 'invalid login' error message.
                    errorlogin = _('Invalid Login.') #True
            else:
                # Return an 'Valid User Credentials' error message.
                errorlogin = _('Enter Valid User Credentials.') #True
    else:
        loginform = LoginForm()

    data = {
        'module': current_view(request),
        'loginform': loginform,
        'errorlogin': errorlogin,
        'is_authenticated': request.user.is_authenticated(),
        'news': get_news(),
    }

    return render_to_response(template, data,
           context_instance=RequestContext(request))


def notice_count(request):
    """Get count of logged in user's notifications"""
    try:
        notice_count = \
        notification.Notice.objects.filter(recipient=request.user,
                                           unseen=1).count()
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
    loginform = LoginForm()
    data = {'module': current_view(request),
            'user': request.user,
            'notice_count': notice_count(request),
            'loginform': loginform,
            'errorlogin': errorlogin,
            'news': get_news(),
    }

    return render_to_response(template, data,
           context_instance=RequestContext(request))


def pleaselog(request):
    template = 'frontend/index.html'
    loginform = LoginForm()

    data = {
        'loginform': loginform,
        'notlogged': True,
        'news': get_news(),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def cust_password_reset(request):
    """Use ``django.contrib.auth.views.password_reset`` view method for
    forgotten password on the Customer UI

    This method sends an e-mail to the user's email-id which is entered in
    ``password_reset_form``
    """
    if not request.user.is_authenticated():
        return password_reset(request,
        template_name='frontend/registration/password_reset_form.html',
        email_template_name='frontend/registration/password_reset_email.html',
        post_reset_redirect='/password_reset/done/',
        from_email='newfies_admin@localhost.com')
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_done(request):
    """Use ``django.contrib.auth.views.password_reset_done`` view method for
    forgotten password on the Customer UI

    This will show a message to the user who is seeking to reset their
    password.
    """
    if not request.user.is_authenticated():
        return password_reset_done(request,
        template_name='frontend/registration/password_reset_done.html')
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_confirm(request, uidb36=None, token=None):
    """Use ``django.contrib.auth.views.password_reset_confirm`` view method for
    forgotten password on the Customer UI

    This will allow a user to reset their password.
    """
    if not request.user.is_authenticated():
        return password_reset_confirm(request, uidb36=uidb36, token=token,
        template_name='frontend/registration/password_reset_confirm.html',
        post_reset_redirect='/reset/done/')
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_complete(request):
    """Use ``django.contrib.auth.views.password_reset_complete`` view method
    for forgotten password on theCustomer UI

    This shows an acknowledgement to the user after successfully resetting
    their password for the system.
    """
    if not request.user.is_authenticated():
        return password_reset_complete(request,
        template_name='frontend/registration/password_reset_complete.html')
    else:
        return HttpResponseRedirect("/")


def common_send_notification(request, status, recipient=None):
    """User Notification (e.g. start | stop | pause) needs to be saved.
    It is a common function for the admin and customer UI's

    **Attributes**:

        * ``pk`` - primary key of the campaign record
        * ``status`` - get label for notifications

    **Logic Description**:

        * This function is used by ``update_campaign_status_admin()`` &
          ``update_campaign_status_cust()``

    """
    if not recipient:
        recipient = request.user
        sender = User.objects.get(is_superuser=1)
    else:
        sender = request.user

    if notification:
        note_label = notification.NoticeType.objects.get(default=status)
        notification.send([recipient],
                          note_label.label,
                          {"from_user": request.user},
                          sender=sender)
    return True


def common_campaign_status(pk, status):
    """Campaign Status (e.g. start | stop | pause) needs to be changed.
    It is a common function for the admin and customer UI's

    **Attributes**:

        * ``pk`` - primary key of the campaign record
        * ``status`` - selected status for the campaign record

    **Logic Description**:

        * Selected Campaign's status needs to be changed.
          Changed status can be start, stop or pause.

        * This function is used by ``update_campaign_status_admin()`` &
          ``update_campaign_status_cust()``
    """
    campaign = Campaign.objects.get(pk=pk)
    previous_status = campaign.status
    campaign.status = status
    campaign.save()

    #Start tasks to import subscriber
    if status == "1" and previous_status != "1":
        collect_subscriber.delay(pk)

    return campaign.user


@login_required
def update_campaign_status_admin(request, pk, status):
    """Campaign Status (e.g. start|stop|pause) can be changed from
    admin interface (via campaign list)"""
    recipient = common_campaign_status(pk, status)
    common_send_notification(request, status, recipient)
    return HttpResponseRedirect(reverse(
                                "admin:dialer_campaign_campaign_changelist"))


@login_required
def update_campaign_status_cust(request, pk, status):
    """Campaign Status (e.g. start|stop|pause) can be changed from
    customer interface (via dialer_campaign/campaign list)"""
    recipient = common_campaign_status(pk, status)
    common_send_notification(request, status, recipient)
    return HttpResponseRedirect('/campaign/')


# Phonebook
@login_required
def phonebook_grid(request):
    """Phonebook list in json format for flexigrid.
    
    **Model**: Phonebook
    
    **Fields**: [id, name, description, updated_date]
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


    #phonebook_list = []
    sortorder_sign = ''
    if sortorder == 'desc':
        sortorder_sign = '-'

    phonebook_list = Phonebook.objects\
                     .values('id', 'name', 'description', 'updated_date')\
                     .annotate(contact_count=Count('contact'))\
                     .filter(user=request.user)

    count = phonebook_list.count()
    phonebook_list = \
        phonebook_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    update_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/page_edit.png);"'
    delete_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/delete.png);"'

    rows = [{'id': row['id'],
             'cell': ['<input type="checkbox" name="select" class="checkbox"\
                      value="' + str(row['id']) + '" />',
                      row['id'],
                      row['name'],
                      row['description'],
                      row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
                      row['contact_count'],
                      '<a href="' + str(row['id']) + '/" class="icon" ' \
                      + update_style + ' title="Update phonebook">&nbsp;</a>' +
                      '<a href="del/' + str(row['id']) + '/" class="icon" ' \
                      + delete_style + ' onClick="return get_alert_msg(' +
                      str(row['id']) +
                      ');"  title="Delete phonebook">&nbsp;</a>']}\
                      for row in phonebook_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@login_required
def phonebook_list(request):
    """Phonebook list for the logged in user

    **Attributes**:

        * ``template`` - frontend/phonebook/list.html

    **Logic Description**:

        * List all phonebooks which belong to the logged in user.
    """
    template = 'frontend/phonebook/list.html'
    data = {
        'module': current_view(request),        
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def phonebook_add(request):
    """Add new Phonebook for the logged in user

    **Attributes**:

        * ``form`` - PhonebookForm
        * ``template`` - frontend/phonebook/change.html

    **Logic Description**:

        * Add a new phonebook which will belong to the logged in user
          via the phonebookForm & get redirected to the phonebook list
    """
    form = PhonebookForm()
    if request.method == 'POST':
        form = PhonebookForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.save()
            request.session["msg"] = _('"%s" is added successfully.' %\
            request.POST['name'])
            return HttpResponseRedirect('/phonebook/')
    template = 'frontend/phonebook/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'add',
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def get_contact_count(request):
    """To get total no of contacts belonging to a phonebook list"""
    contact_list = Contact.objects.extra(where=['phonebook_id IN (%s)'\
                       % request.GET['pb_ids']])
    data = contact_list.count()
    return HttpResponse(data)


@login_required
def phonebook_del(request, object_id):
    """Delete a phonebook for a logged in user

    **Attributes**:

        * ``object_id`` - Selected phonebook object
        * ``object_list`` - Selected phonebook objects

    **Logic Description**:

        * Delete contacts from a contact list belonging to a phonebook list.
        * Delete selected the phonebook from the phonebook list
    """
    try:
        # When object_id is not 0
        phonebook = Phonebook.objects.get(pk=object_id)
        if object_id:
            # 1) delete all contacts belonging to a phonebook
            contact_list = Contact.objects.filter(phonebook=object_id)
            contact_list.delete()

            # 2) delete phonebook
            request.session["msg"] = _('"%s" is deleted successfully.' \
                                        % phonebook.name)
            phonebook.delete()
            return HttpResponseRedirect('/phonebook/')
    except:
        # When object_id is 0 (Multiple recrod delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        # 1) delete all contacts belonging to a phonebook
        contact_list = Contact.objects.extra(where=['phonebook_id IN (%s)'\
                       % values])
        contact_list.delete()

        # 2) delete phonebook
        phonebook_list = Phonebook.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] =\
        _('%d phonebook(s) are deleted successfully.' % phonebook_list.count())
        phonebook_list.delete()
        return HttpResponseRedirect('/phonebook/')


@login_required
def phonebook_change(request, object_id):
    """Update/Delete Phonebook for the logged in user

    **Attributes**:

        * ``object_id`` - Selected phonebook object
        * ``form`` - PhonebookForm
        * ``template`` - frontend/phonebook/change.html

    **Logic Description**:

        * Update/delete selected phonebook from the phonebook list
          via PhonebookForm & get redirected to phonebook list
    """
    phonebook = Phonebook.objects.get(pk=object_id)
    form = PhonebookForm(instance=phonebook)
    if request.method == 'POST':
        if request.POST.get('delete'):
            phonebook_del(request, object_id)
            return HttpResponseRedirect('/phonebook/')
        else:
            form = PhonebookForm(request.POST, instance=phonebook)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%s" is updated successfully.' \
                % request.POST['name'])
                return HttpResponseRedirect('/phonebook/')

    template = 'frontend/phonebook/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'update',
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_grid(request):
    """Contact list in json format for flexigrid

    **Model**: Contact

    **Fields**: [id, phonebook__name, contact, last_name, first_name,
                 description, status, additional_vars, updated_date]
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

    kwargs = {}
    name = ''

    # get querystring from URL
    q_arr = list(request.get_full_path().split('?'))
    j = 0
    q_para = ''

    # get para from querystring
    for i in q_arr:
        if j == 1:
            q_para = i
        j = j + 1

    if "kwargs" in q_para:
        # decode query string
        decoded_string = urllib.unquote(q_para.decode("utf8"))
        temp_list = list(decoded_string.split('&'))
        for i in range(0, len(temp_list)):
            if temp_list[i].find('='):
                kwargs_list = list(temp_list[i].split('='))
                if kwargs_list[0] == 'kwargs':
                    kwargs = kwargs_list[1]
                if kwargs_list[0] == 'name':
                    name = kwargs_list[1]

    phonebook_id_list = ''
    phonebook_objs = Phonebook.objects.filter(user=request.user)
    for i in phonebook_objs:
        phonebook_id_list += str(i.id) + ","
    phonebook_id_list = phonebook_id_list[:-1]

    contact_list = []
    sortorder_sign = ''
    if sortorder == 'desc':
        sortorder_sign = '-'

    if phonebook_id_list:
        select_data = \
        {"status": "(CASE status WHEN 1 THEN 'ACTIVE' ELSE 'INACTIVE' END)"}
        contact_list = Contact.objects\
        .extra(select=select_data,
               where=['phonebook_id IN (%s) ' % phonebook_id_list])\
        .values('id', 'phonebook__name', 'contact', 'last_name',
                'first_name', 'description', 'status', 'additional_vars',
                'updated_date').all()

        # Search option on grid but not working
        #if str(query) and str(qtype):
            #grid_search_kwargs = {}
            #grid_search_kwargs[qtype] = query
            #contact_list = contact_list.filter(**grid_search_kwargs)

        if kwargs:
            kwargs = ast.literal_eval(kwargs)
            contact_list = contact_list.filter(**kwargs)

        if name:
            # Search on contact name
            q = (Q(last_name__icontains=name) |
                 Q(first_name__icontains=name))
            if q:
                contact_list = contact_list.filter(q)

    count = contact_list.count()
    contact_list = \
        contact_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    update_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/page_edit.png);"'
    delete_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/delete.png);"'

    rows = [{'id': row['id'],
             'cell': ['<input type="checkbox" name="select" class="checkbox"\
                      value="' + str(row['id']) + '" />',
                      row['id'], row['phonebook__name'], row['contact'],
                      row['last_name'], row['first_name'], row['status'],
                      row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
                      '<a href="' + str(row['id']) + '/" class="icon" ' \
                      + update_style + ' title="Update contact">&nbsp;</a>' +
                      '<a href="del/' + str(row['id']) + '/" class="icon" ' \
                      + delete_style + ' onClick="return get_alert_msg(' +
                      str(row['id']) +
                      ');" title="Delete contact">&nbsp;</a>']}\
                      for row in contact_list]


    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


# Subscriber
@login_required
def contact_list(request):
    """Contact list for the logged in user

    **Attributes**:

        * ``template`` - frontend/contact/list.html
        * ``form`` - ContactSearchForm

    **Logic Description**:

        * List all contacts from phonebooks belonging to the logged in user
    """
    form = ContactSearchForm(request.user)
    kwargs = {}
    name = ''
    if request.method == 'POST':
        form = ContactSearchForm(request.user, request.POST)
        kwargs = contact_search_common_fun(request)
        if request.POST['name'] != '':
            name = request.POST['name']

    template = 'frontend/contact/list.html'
    data = {
        'module': current_view(request),        
        'msg': request.session.get('msg'),
        'form': form,
        'user': request.user,
        'kwargs': kwargs,
        'name': name,
        'notice_count': notice_count(request),
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_add(request):
    """Add a new contact into the selected phonebook for the logged in user

    **Attributes**:

        * ``form`` - ContactForm
        * ``template`` - frontend/contact/change.html

    **Logic Description**:

        * Before adding a contact, check dialer setting limit if applicable
          to the user.
        * Add new contact belonging to the logged in user
          via ContactForm & get redirected to the contact list
    """
    # Check dialer setting limit
    if request.user and request.method == 'POST':
        # check  Max Number of subscriber per campaign
        if check_dialer_setting(request, check_for="contact"):
            request.session['msg'] = \
            _("You have too many contacts per campaign.\
            You are allowed a maximum of %s" % \
            dialer_setting_limit(request, limit_for="contact"))

            # campaign limit reached
            common_send_notification(request, '3')
            return HttpResponseRedirect("/contact/")

    form = ContactForm(request.user)
    # Add contact
    if request.method == 'POST':
        form = ContactForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            request.session["msg"] = _('"%s" is added successfully.' %\
            request.POST['contact'])
            return HttpResponseRedirect('/contact/')

    phonebook_count = Phonebook.objects.filter(user=request.user).count()    
    template = 'frontend/contact/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'add',
       'phonebook_count': phonebook_count,
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_del(request, object_id):
    """Delete contact for the logged in user

    **Attributes**:

        * ``object_id`` - Selected contact object
        * ``object_list`` - Selected contact objects

    **Logic Description**:

        * Delete selected contact from the contact list
    """
    try:
        # When object_id is not 0
        contact = Contact.objects.get(pk=object_id)
        # Delete phonebook
        if object_id:
            request.session["msg"] = _('"%s" is deleted successfully.' \
            % contact.first_name)
            contact.delete()
            return HttpResponseRedirect('/contact/')
    except:
        # When object_id is 0 (Multiple recrod delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        contact_list = Contact.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] =\
        _('%d contact(s) are deleted successfully.' % contact_list.count())
        contact_list.delete()
        return HttpResponseRedirect('/contact/')


@login_required
def contact_change(request, object_id):
    """Update/Delete contact for the logged in user

    **Attributes**:

        * ``object_id`` - Selected contact object
        * ``form`` - ContactForm
        * ``template`` - frontend/contact/change.html

    **Logic Description**:

        * Update/delete selected contact from the contact list
          via ContactForm & get redirected to the contact list
    """
    contact = Contact.objects.get(pk=object_id)
    form = ContactForm(request.user, instance=contact)
    if request.method == 'POST':
        # Delete contact
        if request.POST.get('delete'):
            contact_del(request, object_id)
            return HttpResponseRedirect('/contact/')
        else: # Update contact
            form = ContactForm(request.user, request.POST,
                                  instance=contact)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%s" is updated successfully.' \
                % request.POST['contact'])
                return HttpResponseRedirect('/contact/')

    template = 'frontend/contact/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'update',
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_import(request):
    """Import CSV file of Contacts for the logged in user

    **Attributes**:

        * ``form`` - Contact_fileImport
        * ``template`` - frontend/contact/import_contact.html

    **Logic Description**:

        * Before adding contacts, check dialer setting limit if applicable
          to the user.
        * Add new contacts which will belong to the logged in user
          via csv file & get the result (upload success and failure 
          statistics)

    **Important variable**:

        * total_rows - Total no. of records in the CSV file
        * retail_record_count - No. of records imported from the CSV file
    """
    # Check dialer setting limit
    if request.user and request.method == 'POST':
        # check  Max Number of subscribers per campaign
        if check_dialer_setting(request, check_for="contact"):
            request.session['msg'] = \
            _("You have too many contacts per campaign.\
            You are allowed a maximum of %s" % \
            dialer_setting_limit(request, limit_for="contact"))

            # campaign limit reached
            common_send_notification(request, '3')
            return HttpResponseRedirect("/contact/")

    form = Contact_fileImport(request.user)
    file_exts = ('.csv', )
    rdr = ''  # will contain CSV data
    msg = ''
    error_msg = ''
    success_import_list = []
    error_import_list = []
    type_error_import_list = []
    if request.method == 'POST':
        form = Contact_fileImport(request.user, request.POST, request.FILES)
        if form.is_valid():
            # col_no - field name
            #  0     - contact
            #  1     - last_name
            #  2     - first_name
            #  3     - email
            #  4     - description
            #  5     - status
            #  6     - additional_vars
            # To count total rows of CSV file
            records = csv.reader(request.FILES['csv_file'],
                             delimiter=',', quotechar='"')
            total_rows = len(list(records))

            rdr = csv.reader(request.FILES['csv_file'],
                             delimiter=',', quotechar='"')
            contact_record_count = 0
            # Read each Row
            for row in rdr:
                row = striplist(row)

                if (row and str(row[0]) > 0):
                    try:
                        # check field type
                        int(row[5])

                        phonebook = \
                        Phonebook.objects.get(pk=request.POST['phonebook'])
                        try:
                            # check if prefix is alredy
                            # exist with retail plan or not
                            contact = Contact.objects.get(
                                 phonebook_id=phonebook.id,
                                 contact=row[0])
                            error_msg = _('Subscriber is already exist !!')
                            error_import_list.append(row)
                        except:
                            # if not, insert record
                            Contact.objects.create(
                                  phonebook=phonebook,
                                  contact=row[0],
                                  last_name=row[1],
                                  first_name=row[2],
                                  email=row[3],
                                  description=row[4],
                                  status=int(row[5]),
                                  additional_vars=row[6])
                            contact_record_count = \
                                contact_record_count + 1
                            msg = \
                            '%d Contact(s) are uploaded  \
                             successfully out of %d row(s) !!'\
                             % (contact_record_count, total_rows)
                            success_import_list.append(row)
                    except:
                        error_msg = _("Invalid value for import! \
                               Please look at the import samples.")
                        type_error_import_list.append(row)

    data = RequestContext(request, {
    'form': form,
    'rdr': rdr,
    'msg': msg,
    'error_msg': error_msg,
    'success_import_list': success_import_list,
    'error_import_list': error_import_list,
    'type_error_import_list': type_error_import_list,
    'module': current_view(request),
    'notice_count': notice_count(request),
    })
    template = 'frontend/contact/import_contact.html'
    return render_to_response(template, data,
           context_instance=RequestContext(request))


def count_contact_of_campaign(campaign_id):
    """Count no of Contacts from phonebook belonging to the campaign"""
    count_contact = \
    Contact.objects.filter(phonebook__campaign=campaign_id).count()
    if not count_contact:
        return str("Phonebook Empty")
    return count_contact


def get_url_campaign_status(id, status):

    control_play_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL\
    + 'newfies/icons/control_play.png);"'
    control_pause_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL \
    + 'newfies/icons/control_pause.png);"'
    control_abort_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL\
    + 'newfies/icons/abort.png);"'
    control_stop_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL\
    + 'newfies/icons/control_stop.png);"'


    control_play_blue_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL \
    + 'newfies/icons/control_play_blue.png);"'
    control_pause_blue_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL \
    + 'newfies/icons/control_pause_blue.png);"'
    control_abort_blue_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL \
    + 'newfies/icons/abort.png);"' # control_abort_blue
    control_stop_blue_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL \
    + 'newfies/icons/control_stop_blue.png);"'

    if status == 1:
        url_str = str("<a href='#' class='icon' title='campaign is running' " +
                  control_play_style + ">&nbsp;</a>\
                  <a href='update_campaign_status_cust/" + str(id) +
                  "/2/' class='icon' title='Pause' " +
                  control_pause_blue_style +
                  ">&nbsp;</a><a href='update_campaign_status_cust/" + str(id) +
                  "/3/' class='icon' title='Abort' " +
                  control_abort_blue_style +
                  ">&nbsp;</a><a href='update_campaign_status_cust/"
                  + str(id) + "/4/' class='icon' title='Stop' " +
                  control_stop_blue_style + ">&nbsp;</a>")
    if status == 2:
        url_str = str("<a href='update_campaign_status_cust/" + str(id) +
                  "/1/' class='icon' title='Start' " +
                  control_play_blue_style +">&nbsp;</a><a href='#'\
                  class='icon' title='campaign is paused' " +
                  control_pause_style +">&nbsp;</a>" +
                  "<a href='update_campaign_status_cust/" + str(id) +
                  "/3/' class='icon' title='Abort' " +
                  control_abort_blue_style +
                  ">&nbsp;</a>" +
                  "<a href='update_campaign_status_cust/" + str(id) +
                  "/4/' class='icon' title='Stop' " +
                  control_stop_blue_style +
                  ">&nbsp;</a>")
    if status == 3:
        url_str = str("<a href='update_campaign_status_cust/" + str(id) +
                  "/1/' class='icon' title='Start' " +
                  control_play_blue_style +
                  ">&nbsp;</a>" + "<a href='update_campaign_status_cust/" +
                  str(id) + "/2/' class='icon' \
                  title='Pause' " + control_pause_blue_style +
                  ">&nbsp;</a>" +
                  "<a href='#' class='icon' title='Abort' " +
                  control_abort_style + " >&nbsp;</a>" +
                  "<a href='update_campaign_status_cust/" + str(id) +
                  "/4/' class='icon' title='Stop' " +
                  control_stop_blue_style + ">&nbsp;</a>")
    if status == 4:
        url_str = str("<a href='update_campaign_status_cust/" + str(id) +
                  "/1/' class='icon' title='Start' " +
                  control_play_blue_style +
                  ">&nbsp;</a>" +
                  "<a href='update_campaign_status_cust/" + str(id) +
                  "/2/' class='icon' title='Pause' " +
                  control_pause_blue_style +
                  ">&nbsp;</a>" +
                  "<a href='update_campaign_status_cust/" + str(id) +
                  "/3/' class='icon' title='campaign is aborted' " +
                  control_abort_blue_style +
                  ">&nbsp;</a>"
                  "<a href='#' class='icon' title='campaign is stopped' " +
                  control_stop_style + ">&nbsp;</a>")

    return url_str


# Campaign
@login_required
def campaign_grid(request):
    """Campaign list in json format for flexigrid

    **Model**: Campaign

    **Fields**: [id, campaign_code, name, startingdate, expirationdate,
    aleg_gateway, aleg_gateway__name, status, voipapp__name]
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


    #campaign_list = []
    sortorder_sign = ''
    if sortorder == 'desc':
        sortorder_sign = '-'

    campaign_list = Campaign.objects\
                    .values('id', 'campaign_code', 'name', 'startingdate',
                            'expirationdate', 'aleg_gateway',
                            'aleg_gateway__name', 'status',
                            'voipapp__name').filter(user=request.user)
    count = campaign_list.count()
    campaign_list = \
        campaign_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    update_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/page_edit.png);"'
    delete_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/delete.png);"'

    rows = [{'id': row['id'],
             'cell': ['<input type="checkbox" name="select" class="checkbox"\
                      value="' + str(row['id']) + '" />',
                      row['campaign_code'],
                      row['name'],
                      row['startingdate'].strftime('%Y-%m-%d %H:%M:%S'),
                      row['expirationdate'].strftime('%Y-%m-%d %H:%M:%S'),
                      row['aleg_gateway__name'],
                      row['voipapp__name'],
                      count_contact_of_campaign(row['id']),
                      get_campaign_status_name(row['status']),
                      str('<a href="' + str(row['id']) + '/" class="icon" ' \
                      + update_style + ' title="Update campaign">&nbsp;</a>' +
                      '<a href="del/' + str(row['id']) + '/" class="icon" ' \
                      + delete_style + ' onClick="return get_alert_msg(' +
                      str(row['id'])
                      + ');" title="Delete campaign">&nbsp;</a>'
                      + get_url_campaign_status(row['id'], row['status'])
                      ),
             ]}for row in campaign_list ]

    data = {'rows': rows,
            'page': page,
            'total': count}

    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@login_required
def campaign_list(request):
    """List all campaigns for the logged in user

    **Attributes**:

        * ``template`` - frontend/campaign/list.html

    **Logic Description**:

        * List all campaigns belonging to the logged in user
    """
    template = 'frontend/campaign/list.html'
    data = {
        'module': current_view(request),        
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def campaign_add(request):
    """Add a new campaign for the logged in user

    **Attributes**:

        * ``form`` - CampaignForm
        * ``template`` - frontend/campaign/change.html

    **Logic Description**:

        * Before adding a campaign, check dialer setting limit if
          applicable to the user.
        * Add the new campaign which will belong to the logged in user
          via CampaignForm & get redirected to campaign list
    """
    # Check dialer setting limit
    if request.user and request.method != 'POST':
        # check Max Number of running campaign
        if check_dialer_setting(request, check_for="campaign"):
            request.session['msg'] = msg = _("you have too many campaign.\
            Max allowed %s" \
            % dialer_setting_limit(request, limit_for="campaign"))

            # campaign limit reached
            common_send_notification(request, '3')
            return HttpResponseRedirect("/campaign/")

    form = CampaignForm()
    # Add campaign
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.save()
            request.session["msg"] = _('"%s" is added successfully.' %\
            request.POST['name'])
            return HttpResponseRedirect('/campaign/')

    template = 'frontend/campaign/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'add',
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def campaign_del(request, object_id):
    """Delete campaign for the logged in user

    **Attributes**:

        * ``object_id`` - Selected campaign object
        * ``object_list`` - Selected campaign objects

    **Logic Description**:

        * Delete the selected campaign from the campaign list
    """
    try:
        # When object_id is not 0
        campaign = Campaign.objects.get(pk=object_id)
        # Delete campaign
        if object_id:
            request.session["msg"] = _('"%s" is deleted successfully.' \
            % campaign.name)
            campaign.delete()
            return HttpResponseRedirect('/campaign/')
    except:
        # When object_id is 0 (Multiple recrod delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        campaign_list = Campaign.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] = _('%d campaign(s) are deleted successfully.'\
        % campaign_list.count())
        campaign_list.delete()
        return HttpResponseRedirect('/campaign/')


@login_required
def campaign_change(request, object_id):
    """Update/Delete campaign for the logged in user

    **Attributes**:

        * ``object_id`` - Selected campaign object
        * ``form`` - CampaignForm
        * ``template`` - frontend/campaign/change.html

    **Logic Description**:

        * Update/delete selected campaign from the campaign list
          via CampaignForm & get redirected to the campaign list
    """
    campaign = Campaign.objects.get(pk=object_id)
    form = CampaignForm(instance=campaign)
    if request.method == 'POST':
        # Delete campaign
        if request.POST.get('delete'):
            campaign_del(request, object_id)
            return HttpResponseRedirect('/campaign/')
        else: # Update campaign
            form = CampaignForm(request.POST, instance=campaign)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%s" is updated successfully.' \
                % request.POST['name'])
                return HttpResponseRedirect('/campaign/')

    template = 'frontend/campaign/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'update',
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))
