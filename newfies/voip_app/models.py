from django.db import models
from django.utils.translation import ugettext as _
from dialer_gateway.models import Gateway
from common.intermediate_model_base_class import Model


APP_STATUS = (
    (1, u'ACTIVE'),
    (0, u'INACTIVE'),
)

APP_TYPE = (
    (1, u'REDIRECT'),
    (2, u'PLAYAUDIO'),
    (3, u'CONFERENCE'),
)


class VoipApp(Model):
    """VoipApp are VoIP application that are defined on the platform, you can
    have different type of application, some as simple as redirecting a call
    and some as complex as starting a complexe application call flow.

    Right now, only the redirection is implemented but this allow you to create
    the application you want on your server and redirect the user to it easily.

    **Attributes**:

        * ``name`` - VoIP application name.
        * ``description`` - description about VoIP application.
        * ``type`` - Application type

    Relationships:

        * ``gateway`` - Foreign key relationship to the Gateway model.

    **Name of DB table**: dialer_phonebook
    """
    name = models.CharField(max_length=90)
    description = models.TextField(null=True, blank=True,
                         help_text=_("Description about the Voip Application"))
    type = models.IntegerField(max_length=20, choices=APP_TYPE, default='1',
           blank=True, null=True)
    gateway = models.ForeignKey(Gateway, null=True, blank=True,
                    help_text=_("Gateway used if we redirect the call"))
    user = models.ForeignKey('auth.User', related_name='VoIP App owner')
    #extension = models.CharField(max_length=40,
    #               help_text=_("Extension to call when redirection the call"))

    #audiofile = models.CharField(max_length=200,
    #                help_text=_("If PLAYAUDIO, define the audio to play"))
    #room = models.CharField(max_length=200,
    #                help_text=_("If CONFERENCE, define here the room number"))

    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'voip_app'
        verbose_name = _("VoIP Application")
        verbose_name_plural = _("VoIP Applications")

    def __unicode__(self):
            return u"%s" % self.name

def get_voipapp_type_name(id):
    """To get name from voip APP_TYPE"""
    for i in APP_TYPE:
        if i[0] == id:
            return i[1]
