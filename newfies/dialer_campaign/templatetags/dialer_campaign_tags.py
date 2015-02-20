#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.db.models import get_model
from django.template.defaultfilters import register
from dialer_campaign.constants import CAMPAIGN_STATUS, CAMPAIGN_STATUS_COLOR
from django.utils.translation import ugettext as _
from dialer_campaign.function_def import get_subscriber_disposition, get_subscriber_status
from mod_utils.function_def import get_common_campaign_status_url, get_common_campaign_status,\
    get_status_value


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
    return get_status_value(value, CAMPAIGN_STATUS)


@register.filter(name='get_campaign_status')
def get_campaign_status(id):
    """To get status name from CAMPAIGN_STATUS

    >>> get_campaign_status(1)
    '<font color="green">STARTED</font>'

    >>> get_campaign_status(2)
    '<font color="blue">PAUSED</font>'

    >>> get_campaign_status(3)
    '<font color="orange">ABORTED</font>'

    >>> get_campaign_status(4)
    '<font color="red">STOPPED</font>'
    """
    return get_common_campaign_status(id, CAMPAIGN_STATUS, CAMPAIGN_STATUS_COLOR)


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
    """Create link to make duplicate campaign"""
    link = '<a href="#campaign-duplicate"  url="/campaign_duplicate/%s/" class="campaign-duplicate" data-toggle="modal" data-controls-modal="campaign-duplicate" title="%s"><i class="fa fa-copy"></i></a>' \
           % (camp_id, _('Duplicate this campaign'))
    return link


def _return_link(app_name, obj_id):
    """
    Return link on campaign listing view
    """
    link = ''
    # Object view links
    if app_name == 'survey':
        link = '<a id="id_survey_seal_%s" href="#sealed-survey" url="/module/sealed_survey_view/%s/" title="%s" data-toggle="modal" data-controls-modal="sealed-survey"><i class="fa fa-search"></i></a>' % \
            (obj_id, obj_id, _('View Sealed Survey'))

    # Object edit links
    if app_name == 'survey_template':
        link = '<a href="/module/survey/%s/" target="_blank" title="%s"><i class="fa fa-search"></i></a>' % \
            (obj_id, _('Edit Survey'))

    return link


@register.simple_tag(name='get_campaign_app_view')
def get_campaign_app_view(campaign_object):
    link = ''
    if campaign_object.status and int(campaign_object.status) == CAMPAIGN_STATUS.START:
        if campaign_object.content_type.model == 'survey':
            link = _return_link('survey', campaign_object.object_id)
    if campaign_object.status and int(campaign_object.status) != CAMPAIGN_STATUS.START:
        if campaign_object.content_type.model == 'survey_template':
            link = _return_link('survey_template', campaign_object.object_id)
        if campaign_object.content_type.model == 'survey':
            link = _return_link('survey', campaign_object.object_id)
    return link


@register.simple_tag(name='get_campaign_status_url')
def get_campaign_status_url(id, status):
    """
    Helper to display campaign status button on the grid
    """
    return get_common_campaign_status_url(id, status, 'update_campaign_status_cust/', CAMPAIGN_STATUS)


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
