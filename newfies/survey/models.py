from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from tagging.fields import TagField
from dialer_campaign.models import Campaign
from audiofield.models import AudioFile
from adminsortable.models import Sortable



from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^tagging.fields.TagField"])


TTS_CHOICES = (
    ('us-Callie-8Hz',   u'us-Callie-8Hz'),
    ('us-Allison-8Hz',   u'us-Allison-8Hz'),
)

MESSAGE_TYPE = (
    (1,             u'Audio File'),
    (2,             u'Text2Speech'),
)

"""
class Text2speechMessage(models.Model):
    name = models.CharField(max_length=150, blank=False, verbose_name="Name")
    tts_message = models.TextField(max_length=1500, blank=True, verbose_name="Text2Speech Message", help_text = 'Define the text2speech message')
    tts_engine = models.CharField(choices=TTS_CHOICES, max_length=120, blank=True, verbose_name="TTS Engine")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    #code_language = models.ForeignKey(Language, verbose_name="Language")
    
    #link to user
    user = models.ForeignKey('auth.User', related_name='TTS Message owner')
    
    def __unicode__(self):
        return '[%s] %s' %(self.id, self.name)
"""        


class SurveyApp(Sortable):
    """SurveyApp"""
    name = models.CharField(max_length=90, verbose_name='Name')
    description = models.TextField(null=True, blank=True, 
                         verbose_name='Description',
                         help_text=_("Survey Description"))
    user = models.ForeignKey('auth.User', related_name='owner')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Survey")
        verbose_name_plural = _("Surveys")
    
    def __unicode__(self):
            return u"%s" % self.name



class SurveyQuestion(Sortable):
    """Survey Question"""
    class Meta(Sortable.Meta):
        ordering = Sortable.Meta.ordering + ['surveyapp']
    
    question = models.CharField(max_length=500,
                                help_text=_('Enter your question')) # What is your prefered fruit?
    tags = TagField(blank=True, max_length=1000)
    user = models.ForeignKey('auth.User', related_name='Survey owner')
    surveyapp = models.ForeignKey(SurveyApp, verbose_name=_("SurveyApp"))
    
    audio_message = models.ForeignKey(AudioFile, null=True, blank=True,
                                      verbose_name=_("Audio File"))
    message_type = models.IntegerField(max_length=20, choices=MESSAGE_TYPE, default='1',
                                        blank=True, null=True, verbose_name=_('Message type'))
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    sortable_by = SurveyApp
    
    def __unicode__(self):
        return self.question
    

class SurveyResponse(models.Model):
    """SurveyResponse"""
    key = models.CharField(max_length=9, blank=False, verbose_name=_("Key Digit"),
                           help_text=_('Define the key link to the response')) # 1 ; 2
    keyvalue = models.CharField(max_length=150, blank=True, verbose_name=_("Key Value")) # Orange ; Kiwi
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    surveyquestion = models.ForeignKey(SurveyQuestion, related_name='SurveyQuestion')
    goto_surveyquestion = models.ForeignKey(SurveyQuestion, null=True, blank=True, related_name='Goto SurveyQuestion')
    
    class Meta:
        unique_together = ("key", "surveyquestion")
    
    def __unicode__(self):
        return '[%s] %s' %(self.id, self.keyvalue)


class SurveyCampaignResult(models.Model):
    """SurveyCampaignResult
    
    That will be difficult to scale for reporting
    One big issue is when the user update the survey in time, we need to keep an history somehow of the question/response
    
    Idealy we can try to build 2 other table, survey_track_question (id, question_text), survey_track_response (id, response_text)
    Where question_text / response_text is unique
    """
    campaign = models.ForeignKey(Campaign, null=True, blank=True)
    
    surveyapp = models.ForeignKey(SurveyApp, related_name='SurveyApp')
    callid = models.CharField(max_length=120, help_text=_("VoIP Call-ID"))
    
    question = models.CharField(max_length=500, blank=False) # What is your prefered fruit?
    response = models.CharField(max_length=150, blank=False) # Orange ; Kiwi
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return '[%s] %s = %s' %(self.id, self.question, self.response)
    