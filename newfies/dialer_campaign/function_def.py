from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from dialer_campaign.models import Phonebook, Campaign, Contact, CAMPAIGN_STATUS, CAMPAIGN_STATUS_COLOR
from user_profile.models import UserProfile
from dialer_settings.models import DialerSetting
from voice_app.models import VoiceApp
from user_profile.models import UserProfile
from dateutil.relativedelta import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
import calendar
import string
import urllib
import time


def field_list(name, user=None):
    """Return List of phonebook, campaign, country"""
    if name == "phonebook" and user is None:
        list = Phonebook.objects.all()

    if name == "phonebook" and user is not None:
        list = Phonebook.objects.filter(user=user)

    if name == "campaign" and user is not None:
        list = Campaign.objects.filter(user=user)

    if name == "voiceapp" and user is not None:
        list = VoiceApp.objects.filter(user=user)

    if name == "gateway" and user is not None:
        list = UserProfile.objects.get(user=user)
        list = list.userprofile_gateway.all()
    
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


def user_attached_with_dialer_settings(request):
    """Check user is attached with dialer setting or not"""
    try:
        user_obj = UserProfile.objects.get(user=request.user,
                                           dialersetting__isnull=False)
        # DialerSettings link to the User
        if user_obj:
            dialer_set_obj = \
            DialerSetting.objects.get(pk=user_obj.dialersetting_id)
            # DialerSettings is exists
            if dialer_set_obj:
                # attached with dialer setting
                return False
            else:
                # not attached
                return True
    except:
        # not attached
        return True


def check_dialer_setting(request, check_for, field_value=''):
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
            if dialer_set_obj:
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

                # check for frequency limit
                if check_for == "frequency":
                    if field_value > dialer_set_obj.max_frequency:
                        # Limit matched or exceeded
                        return True
                    # Limit not exceeded
                    return False

                # check for call duration limit
                if check_for == "duration":
                    if field_value > dialer_set_obj.callmaxduration:
                        # Limit matched or exceeded
                        return True
                    # Limit not exceeded
                    return False

                # check for call retry limit
                if check_for == "retry":
                    if field_value > dialer_set_obj.maxretry:
                        # Limit matched or exceeded
                        return True
                    # Limit not exceeded
                    return False

                # check for call timeout limit
                if check_for == "timeout":
                    if field_value > dialer_set_obj.max_calltimeout:
                        # Limit matched or exceeded
                        return True
                    # Limit not exceeded
                    return False
    except:
        # DialerSettings not link to the User
        return False


def dialer_setting_limit(request, limit_for):
    """Return Dialer Setting's limit

    e.g. max_number_subscriber_campaign
         max_number_campaign
         max_frequency
         callmaxduration
         maxretry
         max_calltimeout
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
        if limit_for == "frequency":
            return str(dialer_set_obj.max_frequency)
        if limit_for == "duration":
            return str(dialer_set_obj.callmaxduration)
        if limit_for == "retry":
            return str(dialer_set_obj.maxretry)
        if limit_for == "timeout":
            return str(dialer_set_obj.max_calltimeout)


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
    """Type fields (e.g. equal to, begins with, ends with, contains)
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
                return '<font color="' + CAMPAIGN_STATUS_COLOR[id] + '">'  + 'STARTED' + '</font>'
            if i[1] == 'PAUSE':
                return '<font color="' + CAMPAIGN_STATUS_COLOR[id] + '">'  + 'PAUSED' + '</font>'
            if i[1] == 'ABORT':
                return '<font color="' + CAMPAIGN_STATUS_COLOR[id] + '">'  + 'ABORTED' + '</font>'
            if i[1] == 'END':
                return '<font color="' + CAMPAIGN_STATUS_COLOR[id] + '">'  + 'STOPPED' + '</font>'


def user_dialer_setting(user):
    """Get Dialer setting for user"""
    try:
        user_ds = UserProfile.objects.get(user=User.objects.get(username=user))
        dialer_set = DialerSetting.objects.get(id=user_ds.dialersetting.id)
    except:
        dialer_set = []
    return dialer_set


def user_dialer_setting_msg(user):
    msg = ''
    if not user_dialer_setting(user):
        msg = _('Your settings are not configured properly, Please contact the administrator.')
    return msg
