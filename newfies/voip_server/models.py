from django.db import models
from django.utils.translation import ugettext as _
from common.intermediate_model_base_class import Model


SERVER_STATUS = (
    (1, u'ACTIVE'),
    (0, u'INACTIVE'),
)

SERVER_TYPE = (
    ('freeswitch', u'Freeswitch'),
    ('asterisk', u'Asterisk'),
)


class VoipServerGroup(Model):
    """This defines the Voip Server Group

    **Attributes**:

        * ``name`` - VoIP Server Group name.
        * ``description`` - description about Server Group.

    **Name of DB table**: voip_server_group
    """
    name = models.CharField(max_length=90)
    description = models.TextField(null=True, blank=True,
                               help_text=_("Additional information about \
                               the Voip Server Group"))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'voip_server_group'
        verbose_name = _("VoIP Server Group")
        verbose_name_plural = _("VoIP Server Groups")

    def __unicode__(self):
            return u"%s" % self.name


class VoipServer(Model):
    """This defines the Voip Server used by the Dialer

    **Attributes**:

        * ``name`` - VoIP Server name.
        * ``serverip`` - Server IP.
        * ``username`` - Server Username.
        * ``password`` - Server Password.
        * ``port`` - Server port.
        * ``status`` -
        * ``type`` -

    Relationships:

        * ``voipservergroup`` - ManyToMany relationship.

    **Name of DB table**: voip_server
    """
    name = models.CharField(max_length=90)
    description = models.TextField(null=True, blank=True,
                        help_text=_("Short description about the Server"))
    serverip = models.CharField(max_length=90, verbose_name='IP/Hostname',
                        help_text=_("Define the IP or hostname of the server"))
    username = models.CharField(max_length=90)
    password = models.CharField(max_length=90)
    port = models.CharField(max_length=10)
    status = models.IntegerField(choices=SERVER_STATUS, default='1',
                verbose_name="Status", blank=True, null=True)
    type = models.CharField(max_length=20, choices=SERVER_TYPE,
                            default='freeswitch', blank=True, null=True)
    voipservergroup = models.ManyToManyField(VoipServerGroup)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'voip_server'
        verbose_name = _("VoIP Server")
        verbose_name_plural = _("VoIP Servers")

    def __unicode__(self):
            return u"%s" % self.name
