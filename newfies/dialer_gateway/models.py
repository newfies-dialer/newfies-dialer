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
        * ``gateways`` - "user/,user", # Gateway string to try dialing \
        separated by comma. First in list will be tried first
        * ``gateway_codecs`` - "'PCMA,PCMU','PCMA,PCMU'", \
        # Codec string as needed by FS for each gateway separated by comma
        * ``gateway_timeouts`` - "10,10", \
        # Seconds to timeout in string for each gateway separated by comma
        * ``gateway_retries`` - "2,1", \
        # Retry String for Gateways separated by comma, \
        on how many times each gateway should be retried
        * ``originate_dial_string`` - originate_dial_string
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
                            help_text=_("Gateway name"))
    status = models.IntegerField(choices=GATEWAY_STATUS, default='1',
                verbose_name="Gateway Status", blank=True, null=True)
    description = models.TextField(verbose_name='Description', blank=True,
                               help_text=_("Gateway provider notes"))
    addprefix = models.CharField(verbose_name=_('Add prefix'),
                max_length=60, blank=True)
    removeprefix = models.CharField(verbose_name=_('Remove prefix'),
                   max_length=60, blank=True)
    gateways = models.CharField(max_length=500,
                   help_text=_('"user,user", # Gateway string to try dialing\
                   separated by comma. First in list will be tried first'))
    gateway_codecs = models.CharField(max_length=500, blank=True,
                   help_text=_('"\'PCMA,PCMU\',\'PCMA,PCMU\'", # Codec string\
                   as needed by FS for each gateway separated by comma'))
    gateway_timeouts = models.CharField(max_length=500, blank=True,
                   help_text=_('"10,10", # Seconds to timeout in string for\
                   each gateway separated by comma'))
    gateway_retries = models.CharField(max_length=500, blank=True,
                   help_text=_('"2,1", # Retry String for Gateways separated\
                  by comma, on how many times each gateway should be retried'))
    originate_dial_string = models.CharField(max_length=500, blank=True,
                   help_text=_('originate_dial_string'))
    secondused = models.IntegerField(null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    failover = models.ForeignKey('self', null=True, blank=True,
                related_name="Failover Gateway", help_text=_("Select Gateway"))
    addparameter = models.CharField(verbose_name=_('Add parameter'),
                   max_length=360, blank=True)
    count_call = models.IntegerField(null=True, blank=True)
    count_in_use = models.IntegerField(null=True, blank=True)
    maximum_call = models.IntegerField(verbose_name=_('Max concurrent calls'),
                   null=True, blank=True)
    #gatewaygroup = models.ManyToManyField(GatewayGroup)

    class Meta:
        db_table = u'dialer_gateway'
        verbose_name = _("Dialer Gateway")
        verbose_name_plural = _("Dialer Gateways")

    def __unicode__(self):
            return u"%s" % self.name
