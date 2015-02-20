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
from django.conf.urls import patterns, url

urlpatterns = patterns('appointment.views',

                       url(r'^module/calendar_user/$', 'calendar_user_list', name='calendar_user_list'),
                       url(r'^module/calendar_user/add/$', 'calendar_user_add', name='calendar_user_add'),
                       url(r'^module/calendar_user/del/(.+)/$', 'calendar_user_del', name='calendar_user_del'),
                       url(r'^module/calendar_user/password/(.+)/$', 'calendar_user_change_pw', name='calendar_user_change_pw'),
                       url(r'^module/calendar_user/(.+)/$', 'calendar_user_change', name='calendar_user_change'),

                       # Calendars urls
                       url(r'^module/calendar/$', 'calendar_list', name='calendar_list'),
                       url(r'^module/calendar/add/$', 'calendar_add', name='calendar_add'),
                       url(r'^module/calendar/del/(.+)/$', 'calendar_del', name='calendar_del'),
                       url(r'^module/calendar/(.+)/$', 'calendar_change', name='calendar_change'),

                       # Calendar settings urls
                       url(r'^module/calendar_setting/$', 'calendar_setting_list', name='calendar_setting_list'),
                       url(r'^module/calendar_setting/add/$', 'calendar_setting_add', name='calendar_setting_add'),
                       url(r'^module/calendar_setting/del/(.+)/$', 'calendar_setting_del', name='calendar_setting_del'),
                       url(r'^module/calendar_setting/(.+)/$', 'calendar_setting_change', name='calendar_setting_change'),

                       # Events urls
                       url(r'^module/event/$', 'event_list', name='event_list'),
                       url(r'^module/event/add/$', 'event_add', name='event_add'),
                       url(r'^module/event/del/(.+)/$', 'event_del', name='event_del'),
                       url(r'^module/event/(.+)/$', 'event_change', name='event_change'),

                       # Alarms urls
                       url(r'^module/alarm/$', 'alarm_list', name='alarm_list'),
                       url(r'^module/alarm/add/$', 'alarm_add', name='alarm_add'),
                       url(r'^module/alarm/del/(.+)/$', 'alarm_del', name='alarm_del'),
                       url(r'^module/alarm/(.+)/$', 'alarm_change', name='alarm_change'),
                       )
