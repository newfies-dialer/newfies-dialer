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
from django.conf.urls import patterns

urlpatterns = patterns('appointment.views',

    (r'^module/calendar_user/$', 'calendar_user_list'),
    (r'^module/calendar_user/add/$', 'calendar_user_add'),
    (r'^module/calendar_user/del/(.+)/$', 'calendar_user_del'),
    (r'^module/calendar_user/password/(.+)/$', 'calendar_user_change_password'),
    (r'^module/calendar_user/(.+)/$', 'calendar_user_change'),

    # Calendars urls
    (r'^module/calendar/$', 'calendar_list'),
    (r'^module/calendar/add/$', 'calendar_add'),
    (r'^module/calendar/del/(.+)/$', 'calendar_del'),
    (r'^module/calendar/(.+)/$', 'calendar_change'),

    # Calendar settings urls
    (r'^module/calendar_setting/$', 'calendar_setting_list'),
    (r'^module/calendar_setting/add/$', 'calendar_setting_add'),
    (r'^module/calendar_setting/del/(.+)/$', 'calendar_setting_del'),
    (r'^module/calendar_setting/(.+)/$', 'calendar_setting_change'),

    # Events urls
    (r'^module/event/$', 'event_list'),
    (r'^module/event/add/$', 'event_add'),
    (r'^module/event/del/(.+)/$', 'event_del'),
    (r'^module/event/(.+)/$', 'event_change'),

    # Alarms urls
    (r'^module/alarm/$', 'alarm_list'),
    (r'^module/alarm/add/$', 'alarm_add'),
    (r'^module/alarm/del/(.+)/$', 'alarm_del'),
    (r'^module/alarm/(.+)/$', 'alarm_change'),
)
