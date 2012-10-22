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
from django.contrib.contenttypes.models import ContentType
from dialer_campaign.models import Campaign
from dialer_gateway.models import Gateway
from voice_app.constants import VOICEAPP_TYPE
from user_profile.fields import LanguageField
from south.modelsinspector import add_introspection_rules

#add introspection rules
add_introspection_rules([], ["^user_profile.fields.LanguageField"])


class VoiceApp_abstract(models.Model):
    """VoiceApp_abstract are VoIP application that are defined on the platform, you can
    have different type of application, some as simple as redirecting a call
    and some as complex as starting a complex application call flow.

    Right now, only the redirection is implemented but this allow you to create
    the application you want on your server and redirect the user to it easily.

    **Attributes**:

        * ``name`` - Voice application name.
        * ``description`` - description about Voice application.
        * ``type`` - Application type

    **Relationships**:

        * ``gateway`` - Foreign key relationship to the Gateway model.
        * ``user`` - Foreign key relationship to the User model.\
        Each voice app assigned to User

    **Name of DB table**: voip_app
    """
    name = models.CharField(max_length=90, verbose_name=_("Name"))
    description = models.TextField(null=True, blank=True,
                    verbose_name=_("Description"),
                    help_text=_("Voice Application Description"))
    type = models.IntegerField(max_length=20, choices=list(VOICEAPP_TYPE), default=1,
           blank=True, null=True, verbose_name=_('Type'))
    gateway = models.ForeignKey(Gateway, null=True, blank=True,
                    verbose_name=_('B-Leg'),
                    help_text=_("Gateway used if we redirect the call"))
    data = models.CharField(max_length=500, blank=True,
                    help_text=_("The value of 'data' depends on the type of voice application :<br/>"\
                    "- Dial : The phone number to dial<br/>"\
                    "- Conference : Conference room name or number<br/>"\
                    "- Playaudio : Audio file URL<br/>"\
                    "- Speak : The text to speak using TTS"))
    tts_language = LanguageField(blank=True, null=True,
                    verbose_name=_('Text-to-Speech Language'),
                    help_text=_("Set the Text-to-Speech Engine"))

    created_date = models.DateTimeField(auto_now_add=True,
        verbose_name=_('Date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u"%s" % self.name

    def set_name(self, name):
        self.name = name


class VoiceApp_template(VoiceApp_abstract):
    """
    This defines the VoiceApp template
    """
    user = models.ForeignKey('auth.User', related_name='voiceapp_template_user')

    class Meta:
        permissions = (
            ("view_voiceapp_template", _('Can see Voiceapp Template')),
        )
        verbose_name = _("Voice Application Template")
        verbose_name_plural = _("Voice Applications Templates")

    def copy_voiceapp_template(self, campaign_obj):
        try:
            record_count = VoiceApp.objects.filter(
                name=self.name,
                description=self.description,
                type=self.type,
                gateway_id=self.gateway_id,
                data=self.data,
                tts_language=self.tts_language,
                user_id=self.user.id,
                campaign_id=campaign_obj.id,
            ).count()

            if record_count == 0:
                new_voiceapp_obj = VoiceApp.objects.create(
                    name=self.name,
                    description=self.description,
                    type=self.type,
                    gateway=self.gateway,
                    data=self.data,
                    tts_language=self.tts_language,
                    user=self.user,
                    campaign=campaign_obj)

                # updated campaign content_type & object_id with new survey object
                campaign_obj.content_type_id =\
                    ContentType.objects.get(model='voiceapp').id
                campaign_obj.object_id = new_voiceapp_obj.id
                campaign_obj.save()
        except:
            raise

        return True


class VoiceApp(VoiceApp_abstract):
    """
    This defines the VoiceApp
    """
    user = models.ForeignKey('auth.User', related_name='voiceapp_user')
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
        verbose_name=_("Campaign"))

    class Meta:
        permissions = (
            ("view_voiceapp", _('Can see Voice App')),
        )
        db_table = u'voice_app'
        verbose_name = _("Voice Application")
        verbose_name_plural = _("Voice Applications")

    def set_name(self, name):
        self.name = name

    def __unicode__(self):
        return u"%s" % self.name


def get_voiceapp_type_name(id):
    """To get name from voice APP_TYPE"""
    for i in VOICEAPP_TYPE:
        if i[0] == id:
            return i[1]
