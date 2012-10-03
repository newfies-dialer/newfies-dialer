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
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from dialer_campaign.models import Campaign
from dialer_cdr.models import Callrequest

from adminsortable.models import Sortable
from audiofield.models import AudioFile
from survey2.constants import SECTION_TYPE
#from tagging.fields import TagField



class Survey_abstract(models.Model):
    """This defines the Survey template

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
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('Date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __unicode__(self):
            return u"%s" % self.name


class Survey_template(Survey_abstract):
    """
    This defines the Survey template
    """
    user = models.ForeignKey('auth.User', related_name='survey_template_user')

    class Meta:
        permissions = (
            ("view_survey_template", _('Can see Survey Template')),
        )
        verbose_name = _("Survey template")
        verbose_name_plural = _("Survey templates")

    def copy_survey_template(self, campaign_obj):
        try:
            #survey_obj = Survey.objects.create(**self.__dict__)
            survey_obj = Survey.objects.create(name=self.name,
                description=self.description,
                user=self.user,
                campaign=campaign_obj)

            # Copy Section
            section_template = Section_template.objects.filter(survey=self)
            for section_temp in section_template:
                section_temp.copy_section_template()
        except:
            raise
        return True


class Survey(Survey_abstract):
    """
    This defines the Survey
    """
    user = models.ForeignKey('auth.User', related_name='survey_user')
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                                 verbose_name=_("Campaign"))

    class Meta:
        permissions = (
            ("view_survey", _('Can see Survey')),
            ("view_survey_report", _('Can see Survey Report'))
        )
        verbose_name = _("Survey")
        verbose_name_plural = _("Surveys")


class Section_abstract(Sortable):
    """This defines the question for survey

    **Attributes**:

        * ``type`` - survey name.
        * ``question`` -
        * ``phrasing`` -
        * ``audiofile`` -
        * ``invalid_audiofile`` -
        * ``retries`` -
        * ``timeout`` -
        * ``key_0`` -
        * ``key_1`` -
        * ``key_2`` -
        * ``key_3`` -
        * ``key_4`` -
        * ``key_5`` -
        * ``key_6`` -
        * ``key_7`` -
        * ``key_8`` -
        * ``key_9`` -
        * ``rating_laps`` -
        * ``validate_number`` -
        * ``number_digits`` -
        * ``min_number`` -
        * ``max_number`` -
        * ``dial_phonenumber`` -
        * ``continue_survey`` -

    **Relationships**:

        * ``survey`` - Foreign key relationship to the Survey model.\
        Each survey question is assigned to a Survey
        * ``audio_message`` - Foreign key relationship to the AudioFile model.

    **Name of DB table**: survey_question
    """
    # select section
    type = models.IntegerField(max_length=20, choices=list(SECTION_TYPE),
                               default='1', blank=True, null=True,
                               verbose_name=_('section type'))
    # Question is the section label, this is used in the reporting
    question = models.CharField(max_length=500, blank=False,
                                verbose_name=_("Question"),
                                help_text=_('Example : Hotel Service Rating'))
    # Phrasing is used
    phrasing = models.CharField(max_length=1000, null=True, blank=True,
                                help_text=_('Example : Enter a number between 1 to 5, press pound key when done'))
    audiofile = models.ForeignKey(AudioFile, null=True, blank=True,
                                  verbose_name=_("Audio File"))
    retries = models.IntegerField(max_length=1, null=True, blank=True,
                                  verbose_name=_("retries"), default=0,
                                  help_text=_('Retries this section until it\'s valid'))
    timeout = models.IntegerField(max_length=2, null=True, blank=True,
                                  verbose_name=_("timeout"),
                                  help_text=_('Timeout in seconds to press the key(s)'))
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

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    sortable_by = Survey

    class Meta(Sortable.Meta):
        ordering = Sortable.Meta.ordering + ['survey']
        abstract = True

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.question)

    def get_branching_count_per_section(self):
        """Get branching count per section"""
        branching_count =\
            Branching.objects.filter(section_id=self.id).count()
        return branching_count


class Section_template(Section_abstract):
    """
    This defines the question for survey section template
    """
    survey = models.ForeignKey(Survey_template, verbose_name=_("Survey"))
    invalid_audiofile = models.ForeignKey(AudioFile, null=True, blank=True,
                                          verbose_name=_("Invalid Audio File digits"),
                                          related_name='survey_template_invalid_audiofile')

    class Meta(Sortable.Meta):
        ordering = Sortable.Meta.ordering + ['survey']

    def copy_section_template(self):
        try:
            Section.objects.create(
                type=self.type,
                question=self.question,
                phrasing=self.phrasing,
                audiofile_id=self.audiofile_id,
                retries=self.retries,
                timeout=self.timeout,
                key_0=self.key_0,
                key_1=self.key_1,
                key_2=self.key_2,
                key_3=self.key_3,
                key_4=self.key_4,
                key_5=self.key_5,
                key_6=self.key_6,
                key_7=self.key_7,
                key_8=self.key_8,
                key_9=self.key_9,
                rating_laps=self.rating_laps,
                validate_number=self.validate_number,
                number_digits=self.number_digits,
                min_number=self.min_number,
                max_number=self.max_number,
                dial_phonenumber=self.dial_phonenumber,
                continue_survey=self.continue_survey,
                order=self.order,
                survey_id=self.survey_id,
                invalid_audiofile_id=self.invalid_audiofile_id
            )

            # Copy Branching
            branching_template =\
                Branching_template.objects.filter(section=self)
            for branching_temp in branching_template:
                branching_temp.copy_branching_template()
        except:
            raise
        return True

class Section(Section_abstract):
    """
    This defines the question for survey section
    """
    survey = models.ForeignKey(Survey, verbose_name=_("Survey"))
    invalid_audiofile = models.ForeignKey(AudioFile, null=True, blank=True,
                                          verbose_name=_("Invalid Audio File digits"),
                                          related_name='survey_invalid_audiofile')

    class Meta(Sortable.Meta):
        ordering = Sortable.Meta.ordering + ['survey']


class Branching_abstract(models.Model):
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

    class Meta:
        unique_together = ("keys", "section")
        abstract = True

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.keys)


class Branching_template(Branching_abstract):
    """
    This defines the response of the survey section
    """
    section = models.ForeignKey(Section_template, related_name='Branching Section')
    # '' to goto hangup
    goto = models.ForeignKey(Section_template, null=True,
                             blank=True, related_name='Goto Section')

    def copy_branching_template(self):
        try:
            Branching.objects.create(
                keys=self.keys,
                section_id=self.section_id,
                goto_id=self.goto_id
            )
        except:
            raise
        return True


class Branching(Branching_abstract):
    """
    This defines the response of the survey section
    """
    section = models.ForeignKey(Section, related_name='Branching Section')
    # '' to goto hangup
    goto = models.ForeignKey(Section, null=True,
                             blank=True, related_name='Goto Section')


class Result(models.Model):
    """This gives survey result

    That will be difficult to scale for reporting
    One big issue is when the user update the survey in time, we need to keep
    an history somehow of the question/response

    Ideally we can try to build 2 other table, survey_track_question
    (id, question_text), survey_track_response (id, response_text)
    Where question_text / response_text is unique

    **Attributes**:

        * ``callrequest`` - Call Request
        * ``section`` - survey question
        * ``response`` - survey question's response

    **Relationships**:

        * ``campaign`` - Foreign key relationship to the Campaign model.\
        Each survey result is belonged to a Campaign
        * ``survey`` - Foreign key relationship to the Survey model.\
        Each survey question is assigned to a Survey
        * ``section`` - Foreign key relationship to the Section model.\
        Each result is assigned to a Section

    **Name of DB table**: result
    """
    callrequest = models.ForeignKey(Callrequest,
                                    blank=True, null=True,
                                    related_name='survey_callrequest')
    section = models.ForeignKey(Section, related_name='Result Section')
    response = models.CharField(max_length=150, blank=False,
                                verbose_name=_("Response"))
    record_file = models.CharField(max_length=200, blank=True, default='',
                                   verbose_name=_("Record File"))
    recording_duration = models.IntegerField(max_length=10, blank=True,
                                             default=0, null=True,
                                             verbose_name=_('Recording Duration'))
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("callrequest", "section")

    def __unicode__(self):
        return '[%s] %s = %s' % (self.id, self.section, self.response)


class ResultAggregate(models.Model):
    """This gives survey result aggregate, used to display survey
    result in a more efficient way

    **Name of DB table**: result_aggregate
    """
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                                 verbose_name=_("Campaign"))
    survey = models.ForeignKey(Survey, related_name='ResultSum Survey')
    section = models.ForeignKey(Section, related_name='ResultSum Section')
    response = models.CharField(max_length=150, blank=False, db_index=True,
                                verbose_name=_("Response"))  # Orange ; Kiwi
    count = models.IntegerField(max_length=20, default=0,
                                verbose_name=_("Result count"))

    created_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '[%s] %s = %s' % (self.id, self.section, self.response)


def post_save_add_phrasing(sender, **kwargs):
    """A ``post_save`` signal is sent by the Contact model instance whenever
    it is going to save.

    **Logic Description**:

        * When new section is added into ``Section`` model, save the
          question & phrasing field.
    """
    if kwargs['created']:
        obj = kwargs['instance']
        obj.phrasing = kwargs['instance'].question
        obj.save()

post_save.connect(post_save_add_phrasing, sender=Section)
