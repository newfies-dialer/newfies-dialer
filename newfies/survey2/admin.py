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
from survey2.models import Survey, Section, Result
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
    list_display = ('id', 'user', 'survey', 'created_date')
    search_fields = ['question']
    #list_display_links = ('question', )
    list_filter = ['created_date', 'survey']

admin.site.register(Section, SectionAdmin)


class ResultAdmin(admin.ModelAdmin):

    """Allows the administrator to view and modify survey campaign result."""

    list_display = ('id', 'campaign', 'survey', 'callid', 'created_date')
    search_fields = ['campaign', 'survey', 'question']
    list_filter = ['created_date', 'survey']
    list_display_links = ('id',)
    ordering = ('id', )

admin.site.register(Result, ResultAdmin)
