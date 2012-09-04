# -*- coding: utf-8 -*-
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

from django.contrib import admin
from survey.models import SurveyApp, SurveyQuestion, \
                          SurveyResponse, SurveyCampaignResult
from adminsortable.admin import SortableAdmin, SortableTabularInline


class SurveyQuestionInline(SortableTabularInline):

    model = SurveyQuestion


class SurveyAppAdmin(SortableAdmin):

    """Allows the administrator to view and modify survey."""

    inlines = [SurveyQuestionInline]
    list_display = ('id', 'name', 'created_date')
    list_display_links = ('id', 'name')

admin.site.register(SurveyApp, SurveyAppAdmin)


class SurveyResponseAdmin(admin.ModelAdmin):

    """
    Allows the administrator to view and modify attributes
    of a survey response.
    """

    list_display = ('key', 'keyvalue', 'created_date')
    search_fields = ['key', 'keyvalue']

admin.site.register(SurveyResponse, SurveyResponseAdmin)


class SurveyResponseInline(admin.TabularInline):

    model = SurveyResponse
    fk_name = 'surveyquestion'
    extra = 1


class SurveyQuestionAdmin(SortableAdmin):

    """Allows the administrator to view and modify survey question."""

    inlines = [SurveyResponseInline]
    list_display = ('id', 'user', 'surveyapp', 'question', 'audio_message',
                    'type', 'gateway', 'created_date')
    search_fields = ['question']
    list_display_links = ('question', )
    list_filter = ['created_date', 'surveyapp']

admin.site.register(SurveyQuestion, SurveyQuestionAdmin)


class SurveyCampaignResultAdmin(admin.ModelAdmin):

    """Allows the administrator to view and modify survey campaign result."""

    list_display = ('id', 'campaign', 'surveyapp', 'callid', 'question',
                    'response', 'record_file', 'recording_duration',
                    'created_date')
    search_fields = ['campaign', 'surveyapp', 'question']
    list_filter = ['created_date', 'surveyapp']
    list_display_links = ('id', 'question', )
    ordering = ('id', )

admin.site.register(SurveyCampaignResult, SurveyCampaignResultAdmin)
