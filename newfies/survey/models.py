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

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from dialer_campaign.models import Campaign
from dialer_cdr.models import Callrequest
from survey.constants import SECTION_TYPE
from audiofield.models import AudioFile, AudioField
from common.language_field import LanguageField
from adminsortable.models import Sortable
from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^common\.language_field\.LanguageField"])
add_introspection_rules([], ["^audiofield\.fields\.AudioField"])
add_introspection_rules([
    (
        [AudioField],  # Class(es) these apply to
        [],  # Positional arguments (not used)
        {
            "ext_whitelist": ["ext_whitelist", {"default": ""}],
        },  # Keyword argument
    ),
], ["^audiofield\.fields\.AudioField"])


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
    name = models.CharField(max_length=90, verbose_name=_('name'))
    tts_language = LanguageField(blank=True, null=True, default='en',
                                 verbose_name=_('Text-to-Speech language'))
    description = models.TextField(null=True, blank=True,
                                   verbose_name=_('description'))
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date'))
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
            ("view_survey_template", _('can see survey template')),
        )
        verbose_name = _("survey template")
        verbose_name_plural = _("survey templates")

    def copy_survey_template(self, campaign_id=None):
        """
        copy survey template to survey when starting campaign
        """
        new_survey_obj = Survey.objects.create(
            name=self.name,
            tts_language=self.tts_language,
            description=self.description,
            user=self.user,
            campaign_id=campaign_id)

        if campaign_id:
            # updated campaign content_type & object_id with new survey object
            survey_id = ContentType.objects.get(model='survey').id

            campaign_obj = Campaign.objects.get(id=campaign_id)
            campaign_obj.content_type_id = survey_id
            campaign_obj.object_id = new_survey_obj.id
            campaign_obj.save()

        # Copy Sections
        section_template = Section_template.objects.filter(survey=self)
        for section_temp in section_template:
            section_temp.copy_section_template(new_survey_obj)

        # Copy Sections Branching
        for section_temp in section_template:
            #get the new created section
            section = Section.objects.get(section_template=section_temp.id, survey=new_survey_obj)
            #Now add the branching for this section
            section_temp.copy_section_branching_template(section, new_survey_obj)

        return True


class Survey(Survey_abstract):
    """
    This defines the Survey
    """
    user = models.ForeignKey('auth.User', related_name='survey_user')
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                                 verbose_name=_("campaign"))

    class Meta:
        permissions = (
            ("view_survey", _('can see survey')),
            ("view_sealed_survey", _('can see sealed survey')),
            ("seal_survey", _('can seal survey')),
            ("export_survey", _('can export survey')),
            ("import_survey", _('can import survey')),
            ("view_survey_report", _('can see survey report'))
        )
        verbose_name = _("survey")
        verbose_name_plural = _("surveys")

    def __unicode__(self):
        if self.campaign:
            return u"%s (campaign: %s)" % (self.name, self.campaign)
        else:
            return u"%s" % self.name


class Section_abstract(Sortable):
    """This defines the question for survey

    **Attributes**:

        * ``type`` - section type
        * ``question`` - question
        * ``script`` - text that will be used for TTS
        * ``audiofile`` - audio file to be use instead of TTS
        * ``invalid_audiofile`` - audio to play when input is invalid
        * ``retries`` - amount of time to retry to get a valid input
        * ``timeout`` - time to wait for user input
        * ``key_0`` - on multi choice section, text for result on key 0
        * ``key_1`` - on multi choice section, text for result on key 1
        * ``key_2`` - on multi choice section, text for result on key 2
        * ``key_3`` - on multi choice section, text for result on key 3
        * ``key_4`` - on multi choice section, text for result on key 4
        * ``key_5`` - on multi choice section, text for result on key 5
        * ``key_6`` - on multi choice section, text for result on key 6
        * ``key_7`` - on multi choice section, text for result on key 7
        * ``key_8`` - on multi choice section, text for result on key 8
        * ``key_9`` - on multi choice section, text for result on key 9
        * ``rating_laps`` - From 1 to X, value to accept rating input
        * ``validate_number`` - check if we want to valid the input on Enter Number section
        * ``number_digits`` - Number of digits to wait for on Enter Number section
        * ``min_number`` - if validate_number the minimum number accepted
        * ``max_number`` - if validate_number the maximum number accepted
        * ``phonenumber`` - phonenumber to dialout / call transfer
        * ``completed`` - reaching this section will mark the subscriber as completed
        * ``conference`` - Conference Room
        * ``sms_text`` - text to send via SMS

    **Relationships**:

        * ``survey`` - Foreign key relationship to the Survey model.\
        Each survey question is assigned to a Survey
        * ``audio_message`` - Foreign key relationship to the AudioFile model.

    **Name of DB table**: survey_question
    """
    # select section
    type = models.IntegerField(max_length=20, choices=list(SECTION_TYPE),
                               default=SECTION_TYPE.PLAY_MESSAGE,
                               #blank=True, null=True,
                               verbose_name=_('section type'))
    # Question is the section label, this is used in the reporting
    question = models.CharField(max_length=500, blank=False,
                                verbose_name=_("question"),
                                help_text=_('Example: hotel service rating'))
    # Script will be used by TTS
    script = models.CharField(max_length=1000, null=True, blank=True,
        help_text=_('Example: Press a key between 1 to 5, press pound key when done or Hello {first_name} {last_name}, please press a key between 1 to 5'))
    audiofile = models.ForeignKey(AudioFile, null=True, blank=True,
                                  verbose_name=_("audio File"))
    retries = models.IntegerField(max_length=1, null=True, blank=True,
                                  verbose_name=_("retries"), default=0,
                                  help_text=_('retries until valid input'))
    timeout = models.IntegerField(max_length=2, null=True, blank=True,
                                  verbose_name=_("timeout"), default=5,
                                  help_text=_('timeout in seconds'))
    # Multi-choice
    key_0 = models.CharField(max_length=100, null=True, blank=True,
                             verbose_name=_("key") + " 0")
    key_1 = models.CharField(max_length=100, null=True, blank=True,
                             verbose_name=_("key") + " 1")
    key_2 = models.CharField(max_length=100, null=True, blank=True,
                             verbose_name=_("key") + " 2")
    key_3 = models.CharField(max_length=100, null=True, blank=True,
                             verbose_name=_("key") + " 3")
    key_4 = models.CharField(max_length=100, null=True, blank=True,
                             verbose_name=_("key") + " 4")
    key_5 = models.CharField(max_length=100, null=True, blank=True,
                             verbose_name=_("key") + " 5")
    key_6 = models.CharField(max_length=100, null=True, blank=True,
                             verbose_name=_("key") + " 6")
    key_7 = models.CharField(max_length=100, null=True, blank=True,
                             verbose_name=_("key") + " 7")
    key_8 = models.CharField(max_length=100, null=True, blank=True,
                             verbose_name=_("key") + " 8")
    key_9 = models.CharField(max_length=100, null=True, blank=True,
                             verbose_name=_("key") + " 9")
    #Rating question
    rating_laps = models.IntegerField(max_length=1, default=9,
                                      null=True, blank=True,
                                      verbose_name=_("from 1 to X"))
    #Capture Digits
    validate_number = models.BooleanField(default=True,
                                          verbose_name=_('check validity'))
    number_digits = models.IntegerField(max_length=2, null=True, blank=True,
                                        default="2",
                                        verbose_name=_("number of digits"))
    min_number = models.BigIntegerField(max_length=50, null=True, blank=True,
                                  default=0, verbose_name=_("minimum"))
    max_number = models.BigIntegerField(max_length=50, null=True, blank=True,
                                  default=99, verbose_name=_("maximum"))
    #Call Transfer
    phonenumber = models.CharField(max_length=50,
                                   null=True, blank=True,
                                   verbose_name=_("Phone Number / SIP URI"))
    #Conference Room
    conference = models.CharField(max_length=50,
                                  null=True, blank=True,
                                  verbose_name=_("conference number"))

    sms_text = models.CharField(max_length=200,
                                null=True, blank=True,
                                help_text=_('text that will be send via SMS to the contact'))

    # if the current section means that the survey is completed
    completed = models.BooleanField(default=False,
                                    verbose_name=_('survey complete'))
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
        branching_count = Branching_template.objects\
            .filter(section_id=self.id).count()
        return branching_count

    def build_dtmf_filter(self):
        """Build the dtmf filter to capture digits"""
        dtmffilter = ''
        if self.key_0 and len(self.key_0) > 0:
            dtmffilter = dtmffilter + '0'
        if self.key_1 and len(self.key_1) > 0:
            dtmffilter = dtmffilter + '1'
        if self.key_2 and len(self.key_2) > 0:
            dtmffilter = dtmffilter + '2'
        if self.key_3 and len(self.key_3) > 0:
            dtmffilter = dtmffilter + '3'
        if self.key_4 and len(self.key_4) > 0:
            dtmffilter = dtmffilter + '4'
        if self.key_5 and len(self.key_5) > 0:
            dtmffilter = dtmffilter + '5'
        if self.key_6 and len(self.key_6) > 0:
            dtmffilter = dtmffilter + '6'
        if self.key_7 and len(self.key_7) > 0:
            dtmffilter = dtmffilter + '7'
        if self.key_8 and len(self.key_8) > 0:
            dtmffilter = dtmffilter + '8'
        if self.key_9 and len(self.key_9) > 0:
            dtmffilter = dtmffilter + '9'
        return dtmffilter


class Section_template(Section_abstract):
    """
    This defines the question for survey section template
    """
    survey = models.ForeignKey(Survey_template, verbose_name=_("survey"))
    invalid_audiofile = models.ForeignKey(AudioFile, null=True, blank=True,
                                          verbose_name=_("audio invalid input"),
                                          related_name='survey_template_invalid_audiofile')

    class Meta(Sortable.Meta):
        ordering = Sortable.Meta.ordering + ['survey']
        verbose_name = _("section template")
        verbose_name_plural = _("section templates")

    def copy_section_template(self, new_survey_obj):
        """
        copy section template to section when starting campaign
        """
        Section.objects.create(
            survey_id=new_survey_obj.id,  # Survey
            section_template=self.id,
            type=self.type,
            question=self.question,
            script=self.script,
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
            phonenumber=self.phonenumber,
            conference=self.conference,
            sms_text=self.sms_text,
            completed=self.completed,
            order=self.order,
            invalid_audiofile_id=self.invalid_audiofile_id,
        )
        return True

    def copy_section_branching_template(self, section, new_survey_obj):
        """
        copy section template to section when starting campaign
        """
        # Get all the Branching for this section
        branching_template = Branching_template.objects\
            .filter(section=self)
        for branching_temp in branching_template:
            #copy the brancing
            branching_temp.copy_branching_template(section, new_survey_obj)
        return True


class Section(Section_abstract):
    """
    This defines the question for survey section
    """
    survey = models.ForeignKey(Survey, verbose_name=_("survey"))
    invalid_audiofile = models.ForeignKey(AudioFile, null=True, blank=True,
                                          verbose_name=_("audio invalid input"),
                                          related_name='survey_invalid_audiofile')
    #section_template_id is used to easy duplication
    section_template = models.IntegerField(max_length=10, blank=True,
                                           default=0, null=True,
                                           verbose_name=_('section template ID'))

    class Meta(Sortable.Meta):
        ordering = Sortable.Meta.ordering + ['survey']


class Branching_abstract(models.Model):
    """This defines the response of the survey section

    **Attributes**:

        * ``keys`` - Key digit (DTMF entered by the calling party)

    **Relationships**:

        * ``section`` - Foreign key relationship to the Section.\
        Each response is assigned to a Section
    """
    keys = models.CharField(max_length=150, blank=True,
                            verbose_name=_("entered value"))
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.keys)


class Branching_template(Branching_abstract):
    """
    This defines the response of the survey section
    """
    section = models.ForeignKey(Section_template,
                                related_name='Branching Template Section')
    goto = models.ForeignKey(Section_template, null=True,
                             blank=True,
                             related_name='Goto Template Section')

    class Meta():
        unique_together = ("keys", "section")
        verbose_name = _("branching template")
        verbose_name_plural = _("branching templates")

    def copy_branching_template(self, new_section, new_survey_obj):
        """
        copy branching template to branching when starting campaign
        """
        #
        goto_section = None
        if self.goto:
            goto_section = Section.objects.get(section_template=self.goto_id, survey=new_survey_obj)

        Branching.objects.create(
            keys=self.keys,
            section=new_section,
            goto=goto_section
        )
        return True


class Branching(Branching_abstract):
    """
    This defines the response of the survey section
    """
    section = models.ForeignKey(Section, related_name='Branching Section')
    goto = models.ForeignKey(Section, null=True,
                             blank=True, related_name='Goto Section')

    class Meta():
        unique_together = ("keys", "section")
        verbose_name = _("branching")
        verbose_name_plural = _("branching")


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
                                verbose_name=_("response"))
    record_file = models.CharField(max_length=200, blank=True, default='',
                                   verbose_name=_("record File"))
    recording_duration = models.IntegerField(max_length=10, blank=True,
                                             default=0, null=True,
                                             verbose_name=_('recording duration'))
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("callrequest", "section")

    def __unicode__(self):
        return '[%s] %s = %s' % (self.id, self.section, self.response)


class ResultAggregate(models.Model):
    """
    This gives survey result aggregate, used to display survey
    result in a more efficient way

    **Name of DB table**: result_aggregate
    """
    survey = models.ForeignKey(Survey, related_name='ResultSum Survey')
    section = models.ForeignKey(Section, related_name='ResultSum Section')
    response = models.CharField(max_length=150, blank=False, db_index=True,
                                verbose_name=_("response"))  # Orange ; Kiwi
    count = models.IntegerField(max_length=20, default=0,
                                verbose_name=_("result count"))

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("survey", "section", "response")

    def __unicode__(self):
        return '[%s] %s = %s' % (self.id, self.section, self.response)


def post_save_add_script(sender, **kwargs):
    """A ``post_save`` signal is sent by the Contact model instance whenever
    it is going to save.

    **Logic Description**:

        * When new section is added into ``Section`` model, save the
          question & script field.
    """
    if kwargs['created']:
        obj = kwargs['instance']
        obj.script = kwargs['instance'].question
        obj.save()

        # Add default branching
        if (obj.type == SECTION_TYPE.PLAY_MESSAGE
           or obj.type == SECTION_TYPE.RECORD_MSG
           or obj.type == SECTION_TYPE.CALL_TRANSFER
           or obj.type == SECTION_TYPE.CONFERENCE
           or obj.type == SECTION_TYPE.SMS):
            Branching_template.objects.create(keys=0, section_id=obj.id, goto_id='')

        if obj.type == SECTION_TYPE.MULTI_CHOICE or \
            obj.type == SECTION_TYPE.CAPTURE_DIGITS or \
                obj.type == SECTION_TYPE.RATING_SECTION:
            Branching_template.objects.create(keys='timeout', section_id=obj.id, goto_id='')

post_save.connect(post_save_add_script, sender=Section_template)
