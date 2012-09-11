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
from dialer_campaign.models import Campaign
from dialer_cdr.models import Callrequest

from adminsortable.models import Sortable
from audiofield.models import AudioFile
#from tagging.fields import TagField

SECTION_TYPE = (
    (1, u'Voice section'),
    (2, u'Multiple choice question'),
    (3, u'Rating question'),
    (4, u'Enter a number'),
    (5, u'Record message'),
    (6, u'Patch-through'),
)


class Survey(Sortable):
    """This defines the Survey

    **Attributes**:

        * ``name`` - survey name.
        * ``description`` - description about the survey.

    **Relationships**:

        * ``user`` - Foreign key relationship to the User model.\
        Each survey is assigned to a User

    **Name of DB table**: survey
    """
    name = models.CharField(max_length=90, verbose_name=_('Name'))
    description = models.TextField(null=True, blank=True,
                        verbose_name=_('Description'),
                        help_text=_("Survey Description"))
    user = models.ForeignKey('auth.User', related_name='survey_user')
    created_date = models.DateTimeField(auto_now_add=True,
                        verbose_name=_('Date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_survey", _('Can see Survey')),
            ("view_survey_report", _('Can see Survey Report'))
        )
        verbose_name = _("Survey")
        verbose_name_plural = _("Surveys")

    def __unicode__(self):
            return u"%s" % self.name


class Section(Sortable):
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
        ordering = Sortable.Meta.ordering + ['survey']

    # select section
    type = models.IntegerField(max_length=20, choices=SECTION_TYPE,
                default='1', blank=True, null=True,
                verbose_name=_('section type'))

    # for voice section, record message, patch-through
    phrasing = models.CharField(max_length=1000, null=True, blank=True,
        verbose_name=_('Example : Enter a number between 1 to 5, \
        press pound key when done'))

    audiofile = models.ForeignKey(AudioFile, null=True, blank=True,
                    verbose_name=_("Audio File"))
    # use audio file
    use_audiofile = models.BooleanField(default=False,
                verbose_name=_('Use audio file'),
                help_text=_('Use audio file instead of phrasing'))

    invalid_audiofile = models.ForeignKey(AudioFile, null=True, blank=True,
                    verbose_name=_("Invalid Audio File digits"),
                    related_name='survey_invalid_audiofile')

    retries = models.IntegerField(max_length=1, null=True, blank=True,
                verbose_name=_("retries"),
                help_text=_('Retries this section until it\'s valid'))

    timeout = models.IntegerField(max_length=2, null=True, blank=True,
                verbose_name=_("timeout"),
                help_text=_('Timeout in seconds to press the key(s)'))

    # multiple choice question, rating question, enter a number
    question = models.CharField(max_length=500,
                verbose_name=_("Question"))

    # multiple choice question,
    key_0 = models.CharField(max_length=100, null=True, blank=True,
                verbose_name=_("Result if the user press") + " 0")
    key_1 = models.CharField(max_length=100, null=True, blank=True,
                verbose_name=_("Result if the user press") + " 1")
    key_2 = models.CharField(max_length=100, null=True, blank=True,
                verbose_name=_("Result if the user press") + " 2")
    key_3 = models.CharField(max_length=100, null=True, blank=True,
                verbose_name=_("Result if the user press") + " 3")
    key_4 = models.CharField(max_length=100, null=True, blank=True,
                verbose_name=_("Result if the user press") + " 4")
    key_5 = models.CharField(max_length=100, null=True, blank=True,
                verbose_name=_("Result if the user press") + " 5")
    key_6 = models.CharField(max_length=100, null=True, blank=True,
                verbose_name=_("Result if the user press") + " 6")
    key_7 = models.CharField(max_length=100, null=True, blank=True,
                verbose_name=_("Result if the user press") + " 7")
    key_8 = models.CharField(max_length=100, null=True, blank=True,
                verbose_name=_("Result if the user press") + " 8")
    key_9 = models.CharField(max_length=100, null=True, blank=True,
                verbose_name=_("Result if the user press") + " 9")

    # rating question
    rating_laps = models.IntegerField(max_length=1, null=True, blank=True,
                verbose_name=_("From 1 to X"))

    # enter a number
    validate_number = models.BooleanField(default=True,
                verbose_name=_('Check for valid number'))
    number_digits = models.IntegerField(max_length=2, null=True, blank=True,
                verbose_name=_("Number limit"))

    min_number = models.IntegerField(max_length=1, null=True, blank=True,
                default=1, verbose_name=_("Minimum"))
    max_number = models.IntegerField(max_length=1, null=True, blank=True,
                default=100, verbose_name=_("Maximum"))

    # dial a phone number
    dial_phonenumber = models.CharField(max_length=50,
                null=True, blank=True,
                verbose_name=_("Dial phone number"))

    # set if we continue or just hangup after this section
    continue_survey = models.BooleanField(default=False,
                verbose_name=_('Continue survey when done'))

    user = models.ForeignKey('auth.User', related_name='survey_owner')
    survey = models.ForeignKey(Survey, verbose_name=_("Survey"))
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    sortable_by = Survey

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.question)


class Branching(models.Model):
    """This defines the response of the survey section

    **Attributes**:

        * ``keys`` - Key digit.

    **Relationships**:

        * ``section`` - Foreign key relationship to the Section.\
        Each response is assigned to a Section
    """
    keys = models.CharField(max_length=150, blank=True,
                    verbose_name=_("Entered value"))  # 1, 2, 1000
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    section = models.ForeignKey(Section, related_name='Branching Section')
    #0 to goto hangup
    goto = models.ForeignKey(Section, null=True,
                    blank=True, related_name='Goto Section')

    class Meta:
        unique_together = ("keys", "section")

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.keys)


class Result(models.Model):
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

    **Name of DB table**: result
    """
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                verbose_name=_("Campaign"))
    survey = models.ForeignKey(Survey, related_name='Survey App')
    section = models.ForeignKey(Section, related_name='Result Section')
    callrequest = models.ForeignKey(Callrequest,
                blank=True, null=True,
                related_name='survey_callrequest')
    response = models.CharField(max_length=150, blank=False,
                verbose_name=_("Response"))  # Orange ; Kiwi
    record_file = models.CharField(max_length=200, blank=True, default='',
                verbose_name=_("Record File"))
    #recording_duration = models.IntegerField(max_length=20,
    #                blank=True, default=0,
    #                null=True, verbose_name=_('Recording Duration'))

    created_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '[%s] %s = %s' % (self.id, self.question, self.response)


class ResultSum(models.Model):
    """This gives survey result summary, used to display survey
    in a more efficient way

    **Name of DB table**: result_sum
    """
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                verbose_name=_("Campaign"))
    survey = models.ForeignKey(Survey, related_name='ResultSum Survey')
    section = models.ForeignKey(Section, related_name='ResultSum Section')
    response = models.CharField(max_length=150, blank=False, db_index=True,
                verbose_name=_("Response"))  # Orange ; Kiwi
    count = models.IntegerField(max_length=20, null=True, blank=True,
                verbose_name=_("Result count"))

    created_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '[%s] %s = %s' % (self.id, self.question, self.response)
