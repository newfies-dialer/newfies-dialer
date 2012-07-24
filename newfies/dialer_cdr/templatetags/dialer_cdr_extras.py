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

from django import template
from django.template.defaultfilters import *
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from survey.views import survey_audio_recording
from dialer_campaign.models import CAMPAIGN_STATUS
from dialer_cdr.models import LEG_TYPE
from survey.models import APP_TYPE
import operator
import copy


@register.filter()
def profit_amount(value, arg):
    """Profit Percentage without % sign"""
    val = value - arg
    return round(val * 100, 2)


@register.filter
def adjust_for_pagination(value, page):
    value, page = int(value), int(page)
    adjusted_value = value + ((page - 1) * 10)
    return adjusted_value


@register.filter()
def month_int(value):
    val = int(value[0:2])
    return val


@register.filter()
def month_name(value, arg):
    """Get month name"""
    month_dict = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May",
                  6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct",
                  11: "Nov", 12: "Dec"}
    no = int(value)
    m_name = month_dict[no]
    return str(m_name) + " " + str(arg)


@register.filter()
def cal_width(value, max):
    """Get width"""
    if not value or not max:
        return "None"
    width = (value / float(max)) * 200
    return width


@register.filter()
def contact_status(value):
    """Contact status"""
    if value == 1:
        return str('ACTIVE')
    else:
        return str('INACTIVE')


@register.filter()
def campaign_status(value):
    """Campaign Status"""
    if not value:
        return ''
    STATUS = dict(CAMPAIGN_STATUS)
    try:
        status = STATUS[value]
    except:
        status = ''
    return str(status)



@register.filter(name='sort')
def listsort(value):
        if isinstance(value, dict):
            new_dict = SortedDict()
            key_list = value.keys()
            key_list.sort()
            for key in key_list:
                new_dict[key] = value[key]
            return new_dict
        elif isinstance(value, list):
            new_list = list(value)
            new_list.sort()
            return new_list
        else:
            return value
        listsort.is_safe = True


@register.filter()
def leg_type_name(value):
    """leg type"""
    if not value:
        return ''
    TYPE = dict(LEG_TYPE)
    try:
        status = TYPE[value]
    except:
        status = ''
    return str(status)


@register.filter()
def action_type_name(value):
    """action type name"""
    if not value:
        return ''
    TYPE = dict(APP_TYPE)
    try:
        status = TYPE[value]
    except:
        status = ''
    return str(status)


@register.filter()
def que_res_string(val):
    """Modify survey result string for display"""
    if not val:
        return ''

    val_list = val.split("-|-")
    result_string = '<table class="table table-striped table-bordered '\
                    'table-condensed">'

    for i in val_list:
        if "*|**|*" in i:
            que_audio = i.split("*|**|*")
            if que_audio:
                result_string += '<tr><td colspan="2">' + str(que_audio[0]) \
                                + survey_audio_recording(str(que_audio[1])) \
                                + '</td></tr>'
        else:
            que_res = i.split("*|*")
            result_string += '<tr><td>' + str(que_res[0])\
                             + '</td><td class="survey_result_key">' \
                             + str(que_res[1]) + '</td></tr>'

    result_string += '</table>'
    return result_string



register.filter('profit_amount', profit_amount)
register.filter('adjust_for_pagination', adjust_for_pagination)
register.filter('month_int', month_int)
register.filter('month_name', month_name)
register.filter('cal_width', cal_width)
register.filter('contact_status', contact_status)
register.filter('campaign_status', campaign_status)
register.filter('leg_type_name', leg_type_name)
register.filter('que_res_string', que_res_string)
register.filter('action_type_name', action_type_name)

