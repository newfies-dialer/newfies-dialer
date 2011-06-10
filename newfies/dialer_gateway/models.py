from django.db import models
from django.utils.translation import ugettext as _
from datetime import *
from common.intermediate_model_base_class import Model

GATEWAY_STATUS = (
    (1, u'ACTIVE'),
    (0, u'INACTIVE'),
)

GATEWAY_PROTOCOL = (
    ('SIP', u'SIP'),
    ('LOCAL', u'LOCAL'),
    ('GSM', u'GSM'),
    ('SKINNY', u'SKINNY'),
    ('JINGLE', u'JINGLE'),
)

"""
class GatewayGroup(Model):
    name = models.CharField(max_length=90)
    description = models.TextField(null=True, blank=True,
                               help_text=_("Short description \
                               about the Gateway Group"))

    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'dialer_gateway_group'
        verbose_name = _("Dialer Gateway Group")
        verbose_name_plural = _("Dialer Gateway Groups")

    def __unicode__(self):
            return u"%s" % self.name
"""


class Gateway(Model):
    """This defines the trunk to deliver the Voip Calls.
    Each Gateway are route that support different protocol and different
    set of rules to alter the dialed number

    **Attributes**:

        * ``name`` - Gateway name.
        * ``description`` - Description about Gateway.
        * ``addprefix`` - Add prefix.
        * ``removeprefix`` - Remove prefix.
        * ``protocol`` - VoIP protocol
        * ``hostname`` - Hostname
        * ``secondused`` -
        * ``failover`` -
        * ``addparameter`` -
        * ``count_call`` -
        * ``count_in_use`` -
        * ``maximum_call`` -
        * ``status`` - Gateway status

    **Name of DB table**: dialer_gateway
    """
    name = models.CharField(unique=True, max_length=255, verbose_name='Name',
                            help_text=_("Enter Gateway Name"))
    description = models.TextField(verbose_name='Description', blank=True,
                               help_text=_("Short description about Provider"))
    addprefix = models.CharField(max_length=60, blank=True)
    removeprefix = models.CharField(max_length=60, blank=True)
    protocol = models.CharField(max_length=60, choices=GATEWAY_PROTOCOL,
                                default='SIP')
    hostname = models.CharField(max_length=240)
    secondused = models.IntegerField(null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    failover = models.ForeignKey('self', null=True, blank=True,
                related_name="Failover Gateway", help_text=_("Select Gateway"))
    addparameter = models.CharField(max_length=360, blank=True)
    count_call = models.IntegerField(null=True, blank=True)
    count_in_use = models.IntegerField(null=True, blank=True)
    maximum_call = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(choices=GATEWAY_STATUS, default='1',
                verbose_name="Gateway Status", blank=True, null=True)
    #gatewaygroup = models.ManyToManyField(GatewayGroup)

    class Meta:
        db_table = u'dialer_gateway'
        verbose_name = _("Dialer Gateway")
        verbose_name_plural = _("Dialer Gateways")

    def __unicode__(self):
            return u"%s" % self.name
