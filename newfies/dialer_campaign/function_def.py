from dialer_campaign.models import Phonebook, Campaign, CAMPAIGN_STATUS
from user_profile.models import UserProfile
from dialer_settings.models import DialerSetting
from dateutil.relativedelta import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
import calendar
import string
import urllib


#related to string operation
def nl2br(s):
    return '<br/>'.join(s.split('\n'))


# get news from http://cdr-stats.org/news.php
def get_news():

    news_final = []
    try:
        news_handler = urllib.urlopen('http://www.newfies-dialer.org/news.php')
        news = news_handler.read()
        news = nl2br(news)
        news = string.split(news, '<br/>')

        news_array = {}
        value = {}
        for newsweb in news:
            value = string.split(newsweb, '|')
            if len(value[0]) > 1:
                news_array[value[0]] = value[1]

        info = {}
        for k in news_array:
            link = k[int(k.find("http://")-1):len(k)]
            info = k[0:int(k.find("http://")-1)]
            info = string.split(k, ' - ')
            news_final.append((info[0], info[1], news_array[k]))

        news_handler.close()
    except IndexError:
        pass
    except IOError:
        pass

    return news_final


def field_list(name, user=None):
    """Return List of phonebook"""
    if name == "phonebook" and user is None:
        list = Phonebook.objects.all()
    if name == "phonebook" and user is not None:
        list = Phonebook.objects.filter(user=user)
    if name == "campaign" and user is not None:
        list = Campaign.objects.filter(user=user)
    #else:
    #    list = []
    return ((l.id, l.name) for l in list)


def day_range():
    """List of days"""
    DAYS = range(1, 32)
    days = map(lambda x: (x, x), DAYS)
    return days


def validate_days(year, month, day):
    """Validate no of days in a month"""
    total_days = calendar.monthrange(year, month)
    if day > total_days[1]:
        return total_days[1]
    else:
        return day


def month_year_range():
    """List of months"""
    tday = datetime.today()
    year_actual = tday.year
    YEARS = range(year_actual - 1, year_actual + 1)
    YEARS.reverse()
    m_list = []
    for n in YEARS:
        if year_actual == n:
            month_no = tday.month + 1
        else:
            month_no = 13
        months_list = range(1, month_no)
        months_list.reverse()
        for m in months_list:
            name = datetime(n, m, 1).strftime("%B")
            str_year = datetime(n, m, 1).strftime("%Y")
            str_month = datetime(n, m, 1).strftime("%m")
            sample_str = str_year + "-" + str_month
            sample_name_str = name + "-" + str_year
            m_list.append((sample_str, sample_name_str))
    return m_list


def check_dialer_setting(request, check_for):
    """Check Dialer Setting Limitation

    **Attribute**

        * ``check_for`` -  for campaign or for contact
    """
    try:
        user_obj = UserProfile.objects.get(user=request.user,
                                           dialersetting__isnull=False)
        # DialerSettings link to the User
        if user_obj:
            dialer_set_obj = \
            DialerSetting.objects.get(pk=user_obj.dialersetting_id)

            # check running campaign for User
            if check_for == "campaign":
                campaign_count = Campaign.objects\
                                 .filter(user=request.user).count()
                # Total active campaign matched with
                # max_number_campaigns
                if campaign_count >= dialer_set_obj.max_number_campaign:
                    # Limit matched or exceeded
                    return True
                else:
                    # Limit not matched
                    return False

            # check for subscriber per campaign
            if check_for == "contact":
                # Campaign list for User
                campaign_list = Campaign.objects.filter(user=request.user)
                for i in campaign_list:
                    # Total contacts per campaign
                    contact_count = \
                    Contact.objects.filter(phonebook__campaign=i.id).count()

                    # Total active contacts matched with
                    # max_number_subscriber_campaign
                    if contact_count >= \
                    dialer_set_obj.max_number_subscriber_campaign:
                        # Limit matched or exceeded
                        return True
                # Limit not matched
                return False
    except:
        # DialerSettings not link to the User
        return False


def dialer_setting_limit(request, limit_for):
    """Return Dialer Setting's limit

    e.g. max_number_subscriber_campaign
         max_number_campaign
    """
    user_obj = UserProfile.objects.get(user=request.user,
                                       dialersetting__isnull=False)
    # DialerSettings link to the User
    if user_obj:
        dialer_set_obj = \
        DialerSetting.objects.get(pk=user_obj.dialersetting_id)
        if limit_for == "contact":
            return str(dialer_set_obj.max_number_subscriber_campaign)
        if limit_for == "campaign":
            return str(dialer_set_obj.max_number_campaign)


def variable_value(request, field_name):
    """Variables are checked with request &
    return field value"""
    if request.method == 'GET':
        if field_name in request.GET:
            field_name = request.GET[field_name]
        else:
            field_name = ''

    if request.method == 'POST':
        if field_name in request.POST:
            field_name = request.POST[field_name]
        else:
            field_name = ''

    return field_name


def type_field_chk(base_field, base_field_type, field_name):
    """Type fileds (e.g. equal to, begins with, ends with, contains)
    are checked."""
    kwargs = {}
    if base_field != '':
        if base_field_type == '1':
            kwargs[field_name + '__contains'] = base_field
        if base_field_type == '2':
            kwargs[field_name + '__exact'] = base_field
        if base_field_type == '3':
            kwargs[field_name + '__startswith'] = base_field
        if base_field_type == '4':
            kwargs[field_name + '__endswith'] = base_field
    return kwargs


def contact_search_common_fun(request):
    """Return Array (kwargs) for Contact list"""

    # Assign form field value to local variable
    contact_no = variable_value(request, 'contact_no')
    contact_no_type = variable_value(request, 'contact_no_type')
    phonebook = variable_value(request, 'phonebook')
    status = variable_value(request, 'status')

    kwargs = {}
    if phonebook != '0':
        kwargs['phonebook'] = phonebook

    if status != '2':
        kwargs['status'] = status

    contact_no = type_field_chk(contact_no, contact_no_type, 'contact')
    for i in contact_no:
        kwargs[i] = contact_no[i]

    return kwargs


def striplist(l):
    """Take a list of string objects and return the same list
    stripped of extra whitespace.
    """
    return([x.strip() for x in l])


def calculate_date(search_type):
    """calculate date"""
    end_date = datetime.today()
    search_type = int(search_type)
    # Last 30 days
    if search_type == 1:
        start_date = end_date+relativedelta(days=-int(30))
    # Last 7 days
    if search_type == 2:
        start_date = end_date+relativedelta(days=-int(7))
    # Yesterday
    if search_type == 3:
        start_date = end_date+relativedelta(days=-int(1),
                                            hour=0,
                                            minute=0,
                                            second=0)
    # Last 24 hours
    if search_type == 4:
        start_date = end_date+relativedelta(hours=-int(24))
    # Last 12 hours
    if search_type == 5:
        start_date = end_date+relativedelta(hours=-int(12))
    # Last 6 hours
    if search_type == 6:
        start_date = end_date+relativedelta(hours=-int(6))
    # Last hour
    if search_type == 7:
        start_date = end_date+relativedelta(hours=-int(1))

    return start_date


def date_range(start, end, q):
    """Date  Range"""
    r = (end + timedelta(days=1) - start).days
    if int(q) <= 2:
        return list(rrule(DAILY,
               dtstart=parse(str(start)),
               until=parse(str(end))))
    if int(q) >= 3:
        return list(rrule(HOURLY, interval=1,
               dtstart=parse(str(start)),
               until=parse(str(end))))
    else:
        return [start + timedelta(days=i) for i in range(r)]


def get_campaign_status_name(id):
    """To get status name from CAMPAIGN_STATUS"""
    for i in CAMPAIGN_STATUS:
        if i[0] == id:
            #return i[1]
            if i[1] == 'START':
                return 'STARTED'
            if i[1] == 'PAUSE':
                return 'PAUSED'
            if i[1] == 'ABORT':
                return 'ABORTED'
            if i[1] == 'END':
                return 'STOPPED'
