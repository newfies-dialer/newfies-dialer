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

from django.conf.urls.defaults import patterns


urlpatterns = patterns('survey.views',
    # Survey urls
    (r'^survey/$', 'survey_list'),
    (r'^survey_grid/$', 'survey_grid'),
    (r'^survey/add/$', 'survey_add'),
    (r'^survey/del/(.+)/$', 'survey_del'),
    (r'^survey/question_list/$', 'survey_question_list'),
    (r'^survey/(.+)/$', 'survey_change'),

    (r'^survey_question/add/$', 'survey_question_add'),
    (r'^survey_question/(?P<id>\w+)/$', 'survey_question_change'),

    (r'^survey_response/add/$', 'survey_response_add'),
    (r'^survey_response/(?P<id>\w+)/$', 'survey_response_change'),

    (r'^survey_finestatemachine/$', 'survey_finestatemachine'),

    (r'^survey_report/$', 'survey_report'),
    (r'^export_surveycall_report/$', 'export_surveycall_report'),

)
