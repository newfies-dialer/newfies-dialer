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

from django.conf.urls.defaults import *
from django.conf import settings
from survey.views import *


urlpatterns = patterns('',
    (r'^survey/question_list/$', 'survey.views.survey_question_list'),
    # Survey urls
    (r'^survey/$', 'survey.views.survey_list'),
    (r'^survey_grid/$', 'survey.views.survey_grid'),
    (r'^survey/add/$', 'survey.views.survey_add'),
    (r'^survey/del/(.+)/$', 'survey.views.survey_del'),
    (r'^survey/(.+)/$', 'survey.views.survey_change'),
    (r'^survey_finestatemachine/$', 'survey.views.survey_finestatemachine'),

    (r'^survey_report/$', 'survey.views.survey_report'),



    # Audio urls
    (r'^audio/$', 'survey.views.audio_list'),
    (r'^audio_grid/$', 'survey.views.audio_grid'),
    (r'^audio/add/$', 'survey.views.audio_add'),
    (r'^audio/del/(.+)/$', 'survey.views.audio_del'),
    (r'^audio/(.+)/$', 'survey.views.audio_change'),
)

