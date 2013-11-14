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
from django.conf.urls import patterns


urlpatterns = patterns('appointment.views',

    (r'^calendar_user/$', 'calendar_user_list'),
    (r'^calendar_user/add/$', 'calendar_user_add'),
    (r'^calendar_user/del/(.+)/$', 'calendar_user_del'),
    (r'^calendar_user/password/(.+)/$', 'calendar_user_change_password'),
    (r'^calendar_user/(.+)/$', 'calendar_user_change'),

    # Calendars urls
    (r'^calendar/$', 'calendar_list'),
    (r'^calendar/add/$', 'calendar_add'),
    (r'^calendar/del/(.+)/$', 'calendar_del'),
    (r'^calendar/(.+)/$', 'calendar_change'),

    # Events urls
    (r'^event/$', 'event_list'),
    (r'^event/add/$', 'event_add'),
    (r'^event/del/(.+)/$', 'event_del'),
    (r'^event/(.+)/$', 'event_change'),

    # Alarms urls
    (r'^alarm/$', 'alarm_list'),
    (r'^alarm/add/$', 'alarm_add'),
    (r'^alarm/del/(.+)/$', 'alarm_del'),
    (r'^alarm/(.+)/$', 'alarm_change'),
)