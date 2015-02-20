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

from django.template.defaultfilters import register
from appointment.constants import EVENT_STATUS, ALARM_STATUS, ALARM_METHOD
from mod_utils.function_def import get_status_value


@register.filter(name='event_status')
def event_status(value):
    """Event Status Templatetag"""
    return get_status_value(value, EVENT_STATUS)


@register.filter(name='alarm_status')
def alarm_status(value):
    """Alarm Status Templatetag"""
    return get_status_value(value, ALARM_STATUS)


@register.filter(name='alarm_method')
def alarm_method(value):
    """Alarm Method Templatetag"""
    return get_status_value(value, ALARM_METHOD)
