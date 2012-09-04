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
from dialer_gateway.models import Gateway
from common.intermediate_model_base_class import Model
from user_profile.fields import LanguageField

APP_STATUS = (
    (1, _('ACTIVE')),
    (0, _('INACTIVE')),
)

APP_TYPE = (
    (1, u'DIAL'),
    (2, u'PLAYAUDIO'),
    (3, u'CONFERENCE'),
    (4, u'SPEAK'),
)


from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^user_profile.fields.LanguageField"])


class VoiceApp(Model):
    """VoiceApp are VoIP application that are defined on the platform, you can
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
    type = models.IntegerField(max_length=20, choices=APP_TYPE, default='1',
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

    user = models.ForeignKey('auth.User', related_name='VoIP App owner')
    #extension = models.CharField(max_length=40,
    #               help_text=_("Extension to call when redirection the call"))

    #audiofile = models.CharField(max_length=200,
    #                help_text=_("If PLAYAUDIO, define the audio to play"))
    #room = models.CharField(max_length=200,
    #                help_text=_("If CONFERENCE, define here the room number"))

    created_date = models.DateTimeField(auto_now_add=True,
                    verbose_name=_('Date'))
    updated_date = models.DateTimeField(auto_now=True)

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
    for i in APP_TYPE:
        if i[0] == id:
            return i[1]
