from django.conf.urls.defaults import *
from django.conf import settings
from survey.views import *


urlpatterns = patterns('',
    # Survey urls
    (r'^survey/$', 'survey.views.survey_list'),
    (r'^survey_grid/$', 'survey.views.survey_grid'),
    (r'^survey/add/$', 'survey.views.survey_add'),
    #(r'^survey/que/$', 'survey.views.show_survey'),
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

