from django.contrib import admin
from survey.models import *
from django import forms
from adminsortable.admin import SortableAdmin, SortableTabularInline, SortableStackedInline

"""
class Text2speechMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'tts_message', 'tts_engine', 'created_date',)
    search_fields = ['name', 'tts_message',]
admin.site.register(Text2speechMessage, Text2speechMessageAdmin)
"""

class SurveyQuestionInline(SortableTabularInline):
    model = SurveyQuestion


class SurveyAppAdmin(SortableAdmin):
    inlines = [SurveyQuestionInline,]
    list_display = ('id', 'name', 'created_date',)
    list_display_links = ('id', 'name', )
admin.site.register(SurveyApp, SurveyAppAdmin)


class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('key', 'keyvalue', 'created_date',)
    search_fields = ['key', 'keyvalue',]
admin.site.register(SurveyResponse, SurveyResponseAdmin)

class SurveyResponseInline(admin.TabularInline):
    model = SurveyResponse
    fk_name = 'surveyquestion'
    extra=1


class SurveyQuestionAdmin(SortableAdmin):
    inlines = [
        SurveyResponseInline,
    ]
    list_display = ('question', 'created_date',)
    search_fields = ['question', ]
    list_display_links = ('question', )
    list_filter = ['created_date',]

admin.site.register(SurveyQuestion, SurveyQuestionAdmin)


class SurveyCampaignResultAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'surveyapp', 'callid', 'question', 'response', 'created_date',)
    search_fields = ['campaign', 'surveyapp', 'question', ]
admin.site.register(SurveyCampaignResult, SurveyCampaignResultAdmin)

