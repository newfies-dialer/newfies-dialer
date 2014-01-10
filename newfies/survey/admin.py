# -*- coding: utf-8 -*-
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

from django.contrib import admin
# from django.utils.translation import ugettext as _
from survey.models import Survey, Section, Branching, \
    Survey_template, Section_template, Branching_template, \
    Result, ResultAggregate
from adminsortable.admin import SortableAdmin, SortableTabularInline
# from common.app_label_renamer import AppLabelRenamer

# AppLabelRenamer(native_app_label=u'survey', app_label=_('Survey')).main()


#Templates Section, Survey and Branching for Admin
class SectionTemplateInline(SortableTabularInline):
    """
    Inline Section Template
    """
    model = Section_template


class SurveyTemplateAdmin(admin.ModelAdmin):
    """
    Allows the administrator to view and modify survey.
    """
    inlines = [SectionTemplateInline]
    list_display = ('id', 'name', 'created_date', 'tts_language')
    list_display_links = ('id', 'name')

admin.site.register(Survey_template, SurveyTemplateAdmin)


class BranchingTemplateAdmin(admin.ModelAdmin):
    """
    Allows the administrator to view and modify branching.
    """
    list_display = ('id', 'keys', 'section', 'goto', 'created_date')
    search_fields = ['keys']
    list_filter = ['created_date', 'section']

admin.site.register(Branching_template, BranchingTemplateAdmin)


#Section, Survey and Branching for Admin
class SectionInline(SortableTabularInline):
    """
    Inline Section
    """
    model = Section


class SurveyAdmin(admin.ModelAdmin):

    """Allows the administrator to view and modify survey."""

    inlines = [SectionInline]
    list_display = ('id', 'name', 'created_date', 'tts_language')
    list_display_links = ('id', 'name')

admin.site.register(Survey, SurveyAdmin)


class SectionTemplateAdmin(SortableAdmin):

    """Allows the administrator to view and modify survey question."""

    list_display = ('id', 'survey', 'created_date')
    search_fields = ['question']
    list_filter = ['created_date', 'survey']

admin.site.register(Section_template, SectionTemplateAdmin)


class SectionAdmin(SortableAdmin):

    """Allows the administrator to view and modify survey question."""

    list_display = ('id', 'survey', 'created_date')
    search_fields = ['question']
    list_filter = ['created_date', 'survey']

admin.site.register(Section, SectionAdmin)


class BranchingAdmin(admin.ModelAdmin):

    """Allows the administrator to view and modify branching."""

    list_display = ('id', 'keys', 'section', 'goto', 'created_date')
    search_fields = ['keys']
    list_filter = ['created_date', 'section']

admin.site.register(Branching, BranchingAdmin)


#Result
class ResultAdmin(admin.ModelAdmin):

    """Allows the administrator to view and modify survey results."""

    list_display = ('id', 'callrequest', 'section', 'response',
                    'record_file', 'created_date')
    search_fields = ['campaign']
    list_filter = ['created_date']
    list_display_links = ('id',)
    ordering = ('id', )

admin.site.register(Result, ResultAdmin)


class ResultAggregateAdmin(admin.ModelAdmin):

    """Allows the administrator to view and modify survey aggregated result."""

    list_display = ('id', 'survey', 'section', 'response',
                    'count', 'created_date')
    search_fields = ['survey']
    list_filter = ['created_date', 'survey']
    list_display_links = ('id',)
    ordering = ('id', )

admin.site.register(ResultAggregate, ResultAggregateAdmin)
