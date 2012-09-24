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
from survey2.models import Survey, Section, Branching, Result, ResultAggregate
from adminsortable.admin import SortableAdmin, SortableTabularInline


class SectionInline(SortableTabularInline):

    model = Section


class SurveyAdmin(SortableAdmin):

    """Allows the administrator to view and modify survey."""

    inlines = [SectionInline]
    list_display = ('id', 'name', 'created_date')
    list_display_links = ('id', 'name')

admin.site.register(Survey, SurveyAdmin)


class SectionAdmin(SortableAdmin):

    """Allows the administrator to view and modify survey question."""

    #inlines = [SurveyResponseInline]
    list_display = ('id', 'survey', 'created_date')
    search_fields = ['question']
    #list_display_links = ('question', )
    list_filter = ['created_date', 'survey']

admin.site.register(Section, SectionAdmin)


class BranchingAdmin(admin.ModelAdmin):

    """Allows the administrator to view and modify branching."""

    list_display = ('id', 'keys', 'section', 'goto', 'created_date')
    search_fields = ['keys']
    #list_display_links = ('keys', )
    list_filter = ['created_date', 'section']

admin.site.register(Branching, BranchingAdmin)


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

    list_display = ('id', 'campaign', 'survey', 'section', 'response',
                    'count', 'created_date')
    search_fields = ['campaign', 'survey']
    list_filter = ['created_date', 'survey']
    list_display_links = ('id',)
    ordering = ('id', )

admin.site.register(ResultAggregate, ResultAggregateAdmin)
