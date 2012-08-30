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

from django.template.defaultfilters import *
from survey.views import survey_audio_recording
from dialer_campaign.models import CAMPAIGN_STATUS
from dialer_cdr.models import LEG_TYPE
from survey.models import APP_TYPE


@register.filter()
def contact_status(value):
    """Contact status

    >>> contact_status(1)
    'ACTIVE'

    >>> contact_status(2)
    'INACTIVE'
    """
    if value == 1:
        return str('ACTIVE')
    else:
        return str('INACTIVE')


@register.filter()
def campaign_status(value):
    """Campaign Status

    >>> campaign_status(1)
    'START'

    >>> campaign_status(2)
    'PAUSE'

    >>> campaign_status(3)
    'ABORT'

    >>> campaign_status(4)
    'END'

    >>> campaign_status(0)
    ''
    """
    if not value:
        return ''
    STATUS = dict(CAMPAIGN_STATUS)
    try:
        status = STATUS[value]
    except:
        status = ''
    return str(status)


@register.filter()
def leg_type_name(value):
    """leg type

    >>> leg_type_name(1)
    u'A-Leg'

    >>> leg_type_name(2)
    u'B-Leg'

    >>> leg_type_name(0)
    ''
    """
    if not value:
        return ''
    TYPE = dict(LEG_TYPE)
    try:
        status = TYPE[value]
    except:
        status = ''
    return unicode(status)


@register.filter()
def action_type_name(value):
    """action type name

    >>> action_type_name(1)
    'MENU'

    >>> action_type_name(2)
    'HANGUP'

    >>> action_type_name(0)
    ''
    """
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
    """Modify survey result string for display

    >>> val = 'qst_1*|*ans_1'

    >>> que_res_string(val)
    '<table class="table table-striped table-bordered table-condensed"><tr><td>qst_1</td><td class="survey_result_key">ans_1</td></tr></table>'
    """
    if not val:
        return ''

    val_list = val.split("-|-")
    result_string = '<table class="table table-striped table-bordered '\
                    'table-condensed">'

    for i in val_list:
        if "*|**|*" in i:
            que_audio = i.split("*|**|*")
            if que_audio:
                new_string = '<tr><td colspan="2">' + str(que_audio[0]) \
                                + survey_audio_recording(str(que_audio[1])) \
                                + '</td></tr>'
                result_string += new_string.encode('utf-8')
        else:
            que_res = i.split("*|*")
            result_string += '<tr><td>' + que_res[0].encode('utf-8') \
                                + '</td><td class="survey_result_key">' \
                                + que_res[1].encode('utf-8') + '</td></tr>'

    result_string += '</table>'
    return result_string


register.filter('contact_status', contact_status)
register.filter('campaign_status', campaign_status)
register.filter('leg_type_name', leg_type_name)
register.filter('que_res_string', que_res_string)
register.filter('action_type_name', action_type_name)
