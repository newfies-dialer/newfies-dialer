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

from django.template.defaultfilters import register
from sms_module.constants import SMS_CAMPAIGN_STATUS
from sms_module.function_def import get_sms_campaign_status_name
from sms_module.views import get_url_sms_campaign_status, make_duplicate_sms_campaign,\
    sms_campaign_textmessage


@register.filter(name='sms_campaign_status')
def sms_campaign_status(value):
    """SMS Campaign Status

    >>> sms_campaign_status(1)
    'START'

    >>> sms_campaign_status(2)
    'PAUSE'

    >>> sms_campaign_status(3)
    'ABORT'

    >>> sms_campaign_status(4)
    'END'

    >>> sms_campaign_status(0)
    ''
    """
    if not value:
        return ''
    STATUS = dict(SMS_CAMPAIGN_STATUS)
    try:
        status = STATUS[value]
    except:
        status = ''

    return str(status)


@register.filter(name='get_sms_campaign_status')
def get_sms_campaign_status(id):
    return get_sms_campaign_status_name(id)


@register.simple_tag(name='get_sms_campaign_status_url')
def get_sms_campaign_status_url(id, status):
    return get_url_sms_campaign_status(id, status)


@register.filter(name='create_duplicate_sms_campaign')
def create_duplicate_sms_campaign(id):
    link = make_duplicate_sms_campaign(id)
    return link


@register.filter(name='get_sms_campaign_textmessage')
def get_sms_campaign_textmessage(id):
    link = sms_campaign_textmessage(id)
    return link
