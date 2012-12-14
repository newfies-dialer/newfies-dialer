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


urlpatterns = patterns('survey.views',
    # Survey urls
    (r'^survey/$', 'survey_list'),
    (r'^survey/add/$', 'survey_add'),
    (r'^survey_view/(.+)/$', 'survey_view'),
    (r'^survey/del/(.+)/$', 'survey_del'),
    (r'^survey/(.+)/$', 'survey_change'),
    (r'^export_survey/(.+)/$', 'export_survey'),
    (r'^import_survey/(.+)/$', 'import_survey'),


    # Section urls
    (r'^section/add/$', 'section_add'),
    (r'^section/branch/add/$', 'section_branch_add'),
    (r'^section/delete/(?P<id>\w+)/$', 'section_delete'),
    (r'^section/(?P<id>\w+)/$', 'section_change'),
    (r'^section/script/(?P<id>\w+)/$', 'section_script_change'),
    (r'^section/script_play/(?P<id>\w+)/$', 'section_script_play'),
    (r'^section/branch/(?P<id>\w+)/$', 'section_branch_change'),

    # Survey FSM urls
    (r'^survey_finitestatemachine/$', 'survey_finitestatemachine'),
    # Survey Report urls
    (r'^survey_report/$', 'survey_report'),
    (r'^export_surveycall_report/$', 'export_surveycall_report'),
    (r'^survey_campaign_result/(?P<id>\w+)/$', 'survey_campaign_result'),
)
