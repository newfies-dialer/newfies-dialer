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

from django.db.models import get_model
from django.template.defaultfilters import register
from dialer_campaign.constants import CAMPAIGN_STATUS
from dialer_campaign.views import make_duplicate_campaign
from dialer_campaign.function_def import get_campaign_status_name, get_subscriber_disposition, \
    get_subscriber_status
from dialer_campaign.views import get_campaign_survey_view, get_url_campaign_status


@register.filter(name='campaign_status')
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
        status = STATUS[value].encode('utf-8')
    except:
        status = ''

    return str(status)


@register.filter(name='get_campaign_status')
def get_campaign_status(id):
    return get_campaign_status_name(id)


@register.simple_tag(name='get_app_name')
def get_app_name(app_label, model_name, object_id):
    """To get app name from app_label, model_name & object_id
    Usage: {% get_app_name app_label model_name object_id %}
    """
    try:
        return get_model(app_label, model_name).objects.get(pk=object_id)
    except:
        return '-'


@register.filter(name='create_duplicate_campaign')
def create_duplicate_campaign(camp_id):
    link = make_duplicate_campaign(camp_id)
    return link


@register.simple_tag(name='get_campaign_app_view')
def get_campaign_app_view(campaign_object):
    return get_campaign_survey_view(campaign_object)


@register.simple_tag(name='get_campaign_status_url')
def get_campaign_status_url(id, status):
    return get_url_campaign_status(id, status)


@register.filter(name='subscriber_status')
def subscriber_status(value):
    """Subscriber Status

    >>> subscriber_status(1)
    'PENDING'
    """
    return get_subscriber_status(value)


@register.simple_tag(name='subscriber_disposition')
def subscriber_disposition(campaign_id, val):
    """To get subscriber disposition name from campaign's
    lead_disposition string"""
    return get_subscriber_disposition(campaign_id, val)


@register.filter(name='check_url_for_template_width')
def check_url_for_template_width(current_url):
    """"""
    full_width_on_requested_path = [
        '/dashboard/', '/sms_dashboard/', '/campaign/', '/sms_campaign/',
        'user_detail_change', '/audio/', '/user_notification/',
    ]
    if current_url == '/':
        return True
    else:
        current_url = str(current_url)
        for path in full_width_on_requested_path:
            if path in current_url:
                return True
        return False
