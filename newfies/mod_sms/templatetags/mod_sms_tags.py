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
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.template.defaultfilters import register
from django.utils.translation import ugettext as _
from mod_sms.constants import SMS_CAMPAIGN_STATUS, SMS_CAMPAIGN_STATUS_COLOR
from mod_utils.function_def import get_common_campaign_status_url, get_common_campaign_status,\
    get_status_value


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
    return get_status_value(value, SMS_CAMPAIGN_STATUS)


@register.filter(name='get_sms_campaign_status')
def get_sms_campaign_status(id):
    return get_common_campaign_status(id, SMS_CAMPAIGN_STATUS, SMS_CAMPAIGN_STATUS_COLOR)


@register.simple_tag(name='get_sms_campaign_status_url')
def get_sms_campaign_status_url(id, status):
    return get_common_campaign_status_url(
        id, status, 'update_sms_campaign_status_cust/', SMS_CAMPAIGN_STATUS)


@register.filter(name='create_duplicate_sms_campaign')
def create_duplicate_sms_campaign(sms_campaign_id):
    """Create link to make duplicate campaign"""
    link = '<a href="#sms-campaign-duplicate"  url="/sms_campaign/duplicate/%s/" class="sms-campaign-duplicate" data-toggle="modal" data-controls-modal="sms-campaign-duplicate" title="%s"><i class="fa fa-copy"></i></a>' \
           % (sms_campaign_id, _('Duplicate this sms campaign'))
    return link


@register.filter(name='get_sms_campaign_textmessage')
def get_sms_campaign_textmessage(sms_campaign_id):
    """Create link to get sms campaign's text-message"""
    link = '<a href="#sms-campaign-textmessage"  url="/sms_campaign/text_message/%s/" class="sms-campaign-textmessage" data-toggle="modal" data-controls-modal="sms-campaign-textmessage" title="%s"><i class="fa fa-search"></i></a>' \
           % (sms_campaign_id, _('Get text-message of this sms campaign'))
    return link
