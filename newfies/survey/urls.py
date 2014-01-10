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


urlpatterns = patterns('survey.views',
    # Survey urls
    (r'^module/survey/$', 'survey_list'),
    (r'^module/survey/add/$', 'survey_add'),
    (r'^module/sealed_survey_view/(.+)/$', 'sealed_survey_view'),
    (r'^module/survey/del/(.+)/$', 'survey_del'),
    (r'^module/survey/(.+)/$', 'survey_change'),
    (r'^module/export_survey/(.+)/$', 'export_survey'),
    (r'^module/import_survey/$', 'import_survey'),
    (r'^module/sealed_survey/$', 'sealed_survey_list'),
    (r'^module/seal_survey/(.+)/$', 'seal_survey'),

    # Section urls
    (r'^section/add/$', 'section_add'),
    (r'^section/branch/add/$', 'section_branch_add'),
    (r'^section/delete/(?P<id>\w+)/$', 'section_delete'),
    (r'^section/(?P<id>\w+)/$', 'section_change'),
    (r'^section/script/(?P<id>\w+)/$', 'section_script_change'),
    (r'^section/script_play/(?P<id>\w+)/$', 'section_script_play'),
    (r'^section/branch/(?P<id>\w+)/$', 'section_branch_change'),

    # Survey Report urls
    (r'^survey_report/$', 'survey_report'),
    (r'^export_surveycall_report/$', 'export_surveycall_report'),
    (r'^survey_campaign_result/(?P<id>\w+)/$', 'survey_campaign_result'),
)
