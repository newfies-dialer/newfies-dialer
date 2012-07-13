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

from django.db import models
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField
from dialer_campaign.models import Campaign
from dialer_gateway.models import Gateway
from audiofield.models import AudioFile
from adminsortable.models import Sortable

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^tagging.fields.TagField"])
add_introspection_rules([], ["^audiofield.fields.AudioField"])


TTS_CHOICES = (
    ('us-Callie-8Hz',   u'us-Callie-8Hz'),
    ('us-Allison-8Hz',   u'us-Allison-8Hz'),
)

MESSAGE_TYPE = (
    (1, u'Audio File'),
    (2, u'Text2Speech'),
)

APP_TYPE = (
    (0, u'MENU'),
    (1, u'HANGUP'),
    (2, u'DIAL'),
    #(3, u'PLAYAUDIO'),
    (4, u'CONFERENCE'),
    #(5, u'SPEAK'),
    (6, u'RECORDING'),
)


"""
class Text2speechMessage(models.Model):
    name = models.CharField(max_length=150, blank=False, verbose_name="Name")
    tts_message = models.TextField(max_length=1500, blank=True,
                        verbose_name="Text2Speech Message",
                        help_text = 'Define the text2speech message')
    tts_engine = models.CharField(choices=TTS_CHOICES, max_length=120,
                        blank=True, verbose_name="TTS Engine")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    #code_language = models.ForeignKey(Language, verbose_name="Language")

    #link to user
    user = models.ForeignKey('auth.User', related_name='TTS Message owner')

    def __unicode__(self):
        return '[%s] %s' %(self.id, self.name)
"""


class SurveyApp(Sortable):
    """This defines the Survey

    **Attributes**:

        * ``name`` - survey name.
        * ``description`` - description about the survey.

    **Relationships**:

        * ``user`` - Foreign key relationship to the User model.\
        Each survey is assigned to a User

    **Name of DB table**: surveyapp
    """
    name = models.CharField(max_length=90, verbose_name=_('Name'))
    description = models.TextField(null=True, blank=True,
                        verbose_name=_('Description'),
                        help_text=_("Survey Description"))
    user = models.ForeignKey('auth.User', related_name='owner')
    created_date = models.DateTimeField(auto_now_add=True,
                        verbose_name=_('Date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Survey")
        verbose_name_plural = _("Surveys")

    def __unicode__(self):
            return u"%s" % self.name


class SurveyQuestion(Sortable):
    """This defines the question for survey

    **Attributes**:

        * ``question`` - survey name.
        * ``tags`` -
        * ``message_type`` -

    **Relationships**:

        * ``user`` - Foreign key relationship to the User model.\
        Each survey question is assigned to a User
        * ``surveyapp`` - Foreign key relationship to the SurveyApp model.\
        Each survey question is assigned to a SurveyApp
        * ``audio_message`` - Foreign key relationship to the AudioFile model.

    **Name of DB table**: survey_question
    """
    class Meta(Sortable.Meta):
        ordering = Sortable.Meta.ordering + ['surveyapp']

    question = models.CharField(max_length=500,
                    verbose_name=_("Question"),
                    help_text=_('Enter your question'))
    tags = TagField(blank=True, max_length=1000)
    user = models.ForeignKey('auth.User', related_name='Survey owner')
    surveyapp = models.ForeignKey(SurveyApp, verbose_name=_("SurveyApp"))
    audio_message = models.ForeignKey(AudioFile, null=True, blank=True,
                    verbose_name=_("Audio File"))
    message_type = models.IntegerField(max_length=20,
                    choices=MESSAGE_TYPE,
                    default='1', blank=True, null=True,
                    verbose_name=_('Message type'))

    type = models.IntegerField(max_length=20, choices=APP_TYPE,
           blank=True, null=True, verbose_name=_('Action type'))
    gateway = models.ForeignKey(Gateway, null=True, blank=True,
                    verbose_name=_('B-Leg'),
                    help_text=_("Gateway used if we redirect the call"))
    data = models.CharField(max_length=500, blank=True,
                    help_text=_("The value of 'data' depends on the type of voice application :<br/>"\
                    "- Dial : The phone number to dial<br/>"\
                    "- Conference : Conference room name or number<br/>"))

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    sortable_by = SurveyApp

    def __unicode__(self):
        return self.question


class SurveyResponse(models.Model):
    """This defines the response for survey question

    **Attributes**:

        * ``key`` - Key digit.
        * ``keyvalue`` - Key Value

    **Relationships**:

        * ``surveyquestion`` - Foreign key relationship to the SurveyQuestion.\
        Each survey response is assigned to a SurveyQuestion

    **Name of DB table**: survey_response
    """
    key = models.CharField(max_length=9, blank=False,
                    verbose_name=_("Key Digit"),
                    help_text=_('Define the key link to the response'))  # 1;2
    keyvalue = models.CharField(max_length=150, blank=True,
                    verbose_name=_("Key Value"))  # Orange ; Kiwi
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    surveyquestion = models.ForeignKey(SurveyQuestion,
                    related_name='SurveyQuestion')
    goto_surveyquestion = models.ForeignKey(SurveyQuestion, null=True,
                    blank=True, related_name='Goto SurveyQuestion')

    class Meta:
        unique_together = ("key", "surveyquestion")

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.keyvalue)


class SurveyCampaignResult(models.Model):
    """This gives survey result

    That will be difficult to scale for reporting
    One big issue is when the user update the survey in time, we need to keep
    an history somehow of the question/response

    Ideally we can try to build 2 other table, survey_track_question
    (id, question_text), survey_track_response (id, response_text)
    Where question_text / response_text is unique

    **Attributes**:

        * ``callid`` - VoIP Call-ID
        * ``question`` - survey question
        * ``response`` - survey question's response

    **Relationships**:

        * ``campaign`` - Foreign key relationship to the Campaign model.\
        Each survey result is belonged to a Campaign
        * ``surveyapp`` - Foreign key relationship to the SurveyApp model.\
        Each survey question is assigned to a SurveyApp

    **Name of DB table**: survey_campaign_result
    """
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                    verbose_name=_("Campaign"))

    surveyapp = models.ForeignKey(SurveyApp, related_name='SurveyApp')
    callid = models.CharField(max_length=120, help_text=_("VoIP Call-ID"),
                    verbose_name=_("Call-ID"))

    question = models.CharField(max_length=500, blank=False,
                    verbose_name=_("Question"))  # What is your prefered fruit?
    response = models.CharField(max_length=150, blank=False,
                    verbose_name=_("Response"))  # Orange ; Kiwi

    created_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '[%s] %s = %s' % (self.id, self.question, self.response)
