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

from django.db.models import get_model
from django.template.defaultfilters import register
from django.conf import settings
from dialer_campaign.constants import CAMPAIGN_STATUS
from dialer_campaign.views import make_duplicate_campaign
from dialer_cdr.constants import LEG_TYPE
from voice_app.constants import VOICEAPP_TYPE
from dialer_campaign.function_def import get_campaign_status_name
from dialer_campaign.views import get_campaign_survey_view, get_url_campaign_status
import os.path


@register.simple_tag(name='percentage_tag')
def percentage_tag(fraction, population):
    """Usage: {% percentage_tag fraction population %}"""
    try:
        return "%.2f%%" % ((float(fraction) / float(population)) * 100)
    except:
        return "0.00%"


@register.filter(name='contact_status')
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


@register.filter(name='leg_type_name')
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


@register.filter(name='voiceapp_type')
def voiceapp_type(value):
    """
    >>> voiceapp_type(1)
    'DIAL'
    """
    if not value:
        return ''
    TYPE = dict(VOICEAPP_TYPE)
    try:
        status = TYPE[value]
    except:
        status = ''

    return str(status)


@register.filter(name='running_total')
def running_total(running_list, field_name):
    return sum(d[field_name] for d in running_list)


@register.filter(name='get_file_basename')
def get_file_basename(val):
    if val:
        file_url = settings.MEDIA_URL + str(val)
        return os.path.basename(file_url)
    return ''
