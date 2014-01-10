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

from django.conf import settings
from common.common_functions import variable_value, ceil_strdate
from country_dialcode.models import Prefix
from datetime import datetime
from django.utils.timezone import utc


def voipcall_record_common_fun(request):
    """Return Form with Initial data or Array (kwargs) for Voipcall_Report
    Changelist_view"""
    start_date = ''
    end_date = ''
    if request.POST.get('from_date'):
        from_date = request.POST.get('from_date')
        start_date = ceil_strdate(from_date, 'start')

    if request.POST.get('to_date'):
        to_date = request.POST.get('to_date')
        end_date = ceil_strdate(to_date, 'end')

    # Assign form field value to local variable
    disposition = variable_value(request, 'status')
    campaign_id = variable_value(request, 'campaign_id')
    leg_type = variable_value(request, 'leg_type')

    kwargs = {}
    if start_date and end_date:
        kwargs['starting_date__range'] = (start_date, end_date)
    if start_date and end_date == '':
        kwargs['starting_date__gte'] = start_date
    if start_date == '' and end_date:
        kwargs['starting_date__lte'] = end_date

    if disposition and disposition != 'all':
        kwargs['disposition__exact'] = disposition

    if campaign_id and campaign_id != '0':
        kwargs['callrequest__campaign_id'] = campaign_id

    if leg_type and leg_type != '':
        kwargs['leg_type__exact'] = leg_type

    if len(kwargs) == 0:
        tday = datetime.today()
        kwargs['starting_date__gte'] = \
            datetime(tday.year, tday.month, tday.day, 0, 0, 0, 0).replace(tzinfo=utc)
        kwargs['starting_date__lte'] = \
            datetime(tday.year, tday.month, tday.day, 23, 59, 59).replace(tzinfo=utc)
    return kwargs


def return_query_string(query_string, para):
    """
    Function is used in voipcall_search_admin_form_fun

    >>> return_query_string('key=1', 'key_val=apple')
    'key=1&key_val=apple'
    >>> return_query_string(False, 'key_val=apple')
    'key_val=apple'
    """
    if query_string:
        query_string += '&%s' % (para)
    else:
        query_string = para
    return query_string


def voipcall_search_admin_form_fun(request):
    """Return query string for Voipcall_Report Changelist_view"""
    start_date = ''
    end_date = ''
    if request.POST.get('from_date'):
        start_date = request.POST.get('from_date')

    if request.POST.get('to_date'):
        end_date = request.POST.get('to_date')

    # Assign form field value to local variable
    disposition = variable_value(request, 'status')
    campaign_id = variable_value(request, 'campaign_id')
    leg_type = variable_value(request, 'leg_type')
    query_string = ''

    if start_date and end_date:
        date_string = 'starting_date__gte=' + start_date + \
            '&starting_date__lte=' + end_date + '+23%3A59%3A59'
        query_string = return_query_string(query_string, date_string)

    if start_date and end_date == '':
        date_string = 'starting_date__gte=' + start_date
        query_string = return_query_string(query_string, date_string)

    if start_date == '' and end_date:
        date_string = 'starting_date__lte=' + end_date
        query_string = return_query_string(query_string, date_string)

    if disposition and disposition != 'all':
        disposition_string = 'disposition__exact=' + disposition
        query_string = return_query_string(query_string, disposition_string)

    if campaign_id and campaign_id != '0':
        campaign_string = 'callrequest__campaign_id=' + str(campaign_id)
        query_string = return_query_string(query_string, campaign_string)

    if leg_type and leg_type != '':
        leg_type_string = 'leg_type__exact=' + str(leg_type)
        query_string = return_query_string(query_string, leg_type_string)

    if start_date == '' and end_date == '':
        tday = datetime.today()
        end_date = start_date = tday.strftime("%Y-%m-%d")
        date_string = 'starting_date__gte=' + start_date + \
            '&starting_date__lte=' + end_date + '+23%3A59%3A59'
        query_string = return_query_string(query_string, date_string)

    return query_string


def prefix_list_string(phone_number):
    """
    To return prefix string
    For Example :-
    phone_no = 34650XXXXXX
    prefix_string = (34650, 3465, 346, 34)

    >>> phone_no = 34650123456

    >>> prefix_list_string(phone_no)
    '34650, 3465, 346, 34'

    >>> phone_no = 34650123456

    >>> prefix_list_string(phone_no)
    '34650, 3465, 346, 34'
    """
    try:
        int(phone_number)
    except ValueError:
        return False
    phone_number = str(phone_number)
    prefix_range = range(settings.PREFIX_LIMIT_MIN,
                         settings.PREFIX_LIMIT_MAX + 1)
    prefix_range.reverse()
    destination_prefix_list = ''
    for i in prefix_range:
        if i == settings.PREFIX_LIMIT_MIN:
            destination_prefix_list = destination_prefix_list \
                + phone_number[0:i]
        else:
            destination_prefix_list = destination_prefix_list \
                + phone_number[0:i] + ', '
    return str(destination_prefix_list)


def get_prefix_obj(phonenumber):
    """Get Prefix object"""
    prefix_obj = None
    list_prefix = prefix_list_string(phonenumber)
    if list_prefix:
        split_prefix_list = list_prefix.split(',')
        for prefix in split_prefix_list:
            try:
                prefix_obj = Prefix.objects.get(prefix=int(prefix))
                break
            except:
                prefix_obj = None
    return prefix_obj
