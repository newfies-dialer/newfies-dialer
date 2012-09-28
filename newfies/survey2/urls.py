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

from django.conf.urls import patterns


urlpatterns = patterns('survey2.views',
    # Survey urls
    (r'^survey2/$', 'survey_list'),
    (r'^survey2_grid/$', 'survey_grid'),
    (r'^survey2/add/$', 'survey_add'),
    (r'^survey2/del/(.+)/$', 'survey_del'),
    (r'^survey2/(.+)/$', 'survey_change'),

    # Section urls
    (r'^section/add/$', 'section_add'),
    (r'^section/branch/add/$', 'section_branch_add'),
    (r'^section/delete/(?P<id>\w+)/$', 'section_delete'),
    (r'^section/(?P<id>\w+)/$', 'section_change'),
    (r'^section/phrasing/(?P<id>\w+)/$', 'section_phrasing_change'),
    (r'^section/phrasing_play/(?P<id>\w+)/$', 'section_phrasing_play'),
    (r'^section/branch/(?P<id>\w+)/$', 'section_branch_change'),

    # Survey FSM urls
    (r'^survey_finestatemachine/$', 'survey_finestatemachine'),
    # Survey Report urls
    (r'^survey2_report/$', 'survey_report'),
    (r'^export2_surveycall_report/$', 'export_surveycall_report'),
)
