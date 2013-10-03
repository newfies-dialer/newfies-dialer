#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.utils.translation import ugettext_lazy as _
from dialer_contact.models import Contact
from dialer_campaign.models import Campaign
from dialer_campaign.constants import CAMPAIGN_STATUS,\
    CAMPAIGN_STATUS_COLOR
from dateutil.rrule import rrule, DAILY, HOURLY
from dateutil.parser import parse
from datetime import timedelta


def check_dialer_setting(request, check_for, field_value=''):
    """Check Dialer Setting Limitation

    **Attribute**

        * ``check_for`` -  for campaign or for contact
    """
    #TODO: fix the try and improve the nesting
    try:
        # DialerSettings is linked with the User
        dialer_set_obj = request.user.get_profile().dialersetting
        if dialer_set_obj:
            # check running campaign for User
            if check_for == "campaign":
                campaign_count = Campaign.objects\
                    .filter(user=request.user).count()
                # Total active campaign matched with
                # max_cpgs
                if campaign_count >= dialer_set_obj.max_cpg:
                    # Limit matched or exceeded
                    return True
                else:
                    # Limit not matched
                    return False

            # check for subscriber per campaign
            if check_for == "contact":
                # campaign list for User

                # TODO:
                # We need to improve/normalize our limit check at the moment
                # max_subr_cpg doesn't behave as it should.
                #
                # max_subr_cpg = max number of subscriber per campaign,
                # this should be checked when a contact is going to be imported
                # to the subscriber list
                #
                # TODO: This needs to be efficient/fast : Avoid things like
                # checking for ALL the campaigns everytime
                #

                # max_contact = new setting, this will per user define
                # the max number of contact in all the user phonebook together
                # this will be checked when importing/adding new contact to phonebook
                campaign_list = Campaign.objects.filter(user=request.user)
                for i in campaign_list:
                    # total contacts per campaign
                    contact_count = Contact.objects\
                        .filter(phonebook__campaign=i.id, phonebook__user=request.user)\
                        .count()
                    # total active contacts matched with max_subr_cpg
                    if contact_count >= dialer_set_obj.max_contact:
                        # Limit matched or exceeded
                        return True
                # limit not matched
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

            # check for subscriber limit
            if check_for == "subscriber":
                if field_value > dialer_set_obj.max_subr_cpg:
                    # Limit matched or exceeded
                    return True
                # Limit not exceeded
                return False
    except:
        # DialerSettings not link to the User
        return False


def dialer_setting_limit(request, limit_for):
    """Return Dialer Setting's limit

    e.g. max_subr_cpg
         max_cpg
         max_frequency
         callmaxduration
         maxretry
         max_calltimeout
    """
    try:
        # DialerSettings is linked with the User
        dialer_set_obj = request.user.get_profile().dialersetting
        if limit_for == "contact":
            return str(dialer_set_obj.max_contact)
        if limit_for == "subscriber":
            return str(dialer_set_obj.max_subr_cpg)
        if limit_for == "campaign":
            return str(dialer_set_obj.max_cpg)
        if limit_for == "frequency":
            return str(dialer_set_obj.max_frequency)
        if limit_for == "duration":
            return str(dialer_set_obj.callmaxduration)
        if limit_for == "retry":
            return str(dialer_set_obj.maxretry)
        if limit_for == "timeout":
            return str(dialer_set_obj.max_calltimeout)
    except:
        return False


def type_field_chk(base_field, base_field_type, field_name):
    """Type fields (e.g. equal to, begins with, ends with, contains)
    are checked.

    >>> type_field_chk('1234', '1', 'contact')
    {'contact__contains': '1234'}

    >>> type_field_chk('1234', '2', 'contact')
    {'contact__exact': '1234'}

    >>> type_field_chk('1234', '3', 'contact')
    {'contact__startswith': '1234'}

    >>> type_field_chk('1234', '4', 'contact')
    {'contact__endswith': '1234'}

    """
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


def date_range(start, end, q):
    """Date  Range

    >>> from datetime import datetime

    >>> s_date = datetime(2012, 07, 11, 0, 0, 0, 0)

    >>> e_date = datetime(2012, 07, 12, 23, 59, 59, 99999)

    >>> date_range(s_date, e_date, 2)
    [datetime.datetime(2012, 7, 11, 0, 0), datetime.datetime(2012, 7, 12, 0, 0)]

    """
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
    """To get status name from CAMPAIGN_STATUS

    >>> get_campaign_status_name(1)
    '<font color="green">STARTED</font>'

    >>> get_campaign_status_name(2)
    '<font color="blue">PAUSED</font>'

    >>> get_campaign_status_name(3)
    '<font color="orange">ABORTED</font>'

    >>> get_campaign_status_name(4)
    '<font color="red">STOPPED</font>'
    """
    for i in CAMPAIGN_STATUS:
        if i[0] == id:
            #return i[1]
            if i[1] == 'START':
                return '<font color="%s">STARTED</font>' \
                       % (CAMPAIGN_STATUS_COLOR[id])
            if i[1] == 'PAUSE':
                return '<font color="%s">PAUSED</font>' \
                       % (CAMPAIGN_STATUS_COLOR[id])
            if i[1] == 'ABORT':
                return '<font color="%s">ABORTED</font>' \
                       % (CAMPAIGN_STATUS_COLOR[id])
            if i[1] == 'END':
                return '<font color="%s">STOPPED</font>' \
                       % (CAMPAIGN_STATUS_COLOR[id])


def user_dialer_setting(user):
    """Get Dialer setting for user"""
    try:
        dialer_set = user.get_profile().dialersetting
    except:
        dialer_set = []
    return dialer_set


def user_dialer_setting_msg(user):
    msg = ''
    if not user_dialer_setting(user):
        msg = _('your settings are not configured properly, please contact the administrator.')
    return msg
