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

from django.template.defaultfilters import register
from appointment.constants import EVENT_STATUS, ALARM_STATUS, ALARM_METHOD


@register.filter(name='event_status')
def event_status(value):
    """Event Status Templatetag"""
    if not value:
        return ''
    STATUS = dict(EVENT_STATUS)
    try:
        return STATUS[value].encode('utf-8')
    except:
        return ''


@register.filter(name='alarm_status')
def alarm_status(value):
    """Alarm Status Templatetag"""
    if not value:
        return ''
    STATUS = dict(ALARM_STATUS)
    try:
        return STATUS[value].encode('utf-8')
    except:
        return ''


@register.filter(name='alarm_method')
def alarm_method(value):
    """Alarm Method Templatetag"""
    if not value:
        return ''
    METHOD = dict(ALARM_METHOD)
    try:
        return METHOD[value].encode('utf-8')
    except:
        return ''
