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
from django.utils.translation import ugettext_lazy as _
from common.intermediate_model_base_class import Model
from dialer_gateway.constants import GATEWAY_STATUS


class Gateway(Model):
    """This defines the trunk to deliver the Voip Calls.
    Each of the Gateways are routes that support different protocols and
    sets of rules to alter the dialed number.

    **Attributes**:

        * ``name`` - Gateway name.
        * ``description`` - Description about the Gateway.
        * ``addprefix`` - Add prefix.
        * ``removeprefix`` - Remove prefix.
        * ``gateways`` - "user/,user/", # Gateway string to try dialing \
            separated by comma. First in the list will be tried first
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
    name = models.CharField(unique=True, max_length=255,
                verbose_name=_('name'), help_text=_("gateway name"))
    status = models.IntegerField(choices=list(GATEWAY_STATUS),
                default=GATEWAY_STATUS.ACTIVE,
                verbose_name=_("gateway status"), blank=True, null=True)
    description = models.TextField(verbose_name=_('description'), blank=True,
                               help_text=_("gateway provider notes"))
    addprefix = models.CharField(verbose_name=_('add prefix'),
                max_length=60, blank=True)
    removeprefix = models.CharField(verbose_name=_('remove prefix'),
                   max_length=60, blank=True)
    gateways = models.CharField(max_length=500, verbose_name=_("gateways"),
                help_text=_('Gateway string to dial, ie "sofia/gateway/myprovider/"'))

    gateway_codecs = models.CharField(max_length=500, blank=True,
        verbose_name=_("gateway codecs"),
        help_text=_('codec string as needed by FS, ie "PCMA,PCMU"'))

    gateway_timeouts = models.CharField(max_length=500, blank=True,
        verbose_name=_("gateway timeouts"),
        help_text=_('timeout in seconds, ie "10"'))

    gateway_retries = models.CharField(max_length=500, blank=True,
        verbose_name=_("gateway retries"),
        help_text=_('"2,1", # retry String for Gateways separated by comma, on how many times each gateway should be retried'))

    originate_dial_string = models.CharField(max_length=500, blank=True,
        verbose_name=_("originate dial string"),
        help_text=_('add channels variables : http://wiki.freeswitch.org/wiki/Channel_Variables, ie: bridge_early_media=true,hangup_after_bridge=true'))

    secondused = models.IntegerField(null=True, blank=True,
                verbose_name=_("second used"))

    created_date = models.DateTimeField(auto_now_add=True,
                verbose_name=_('date'))
    updated_date = models.DateTimeField(auto_now=True)

    failover = models.ForeignKey('self', null=True, blank=True,
                related_name="Failover Gateway", help_text=_("select gateway"))
    addparameter = models.CharField(verbose_name=_('add parameter'),
                   max_length=360, blank=True)
    count_call = models.IntegerField(null=True, blank=True,
                verbose_name=_("call count"))
    count_in_use = models.IntegerField(null=True, blank=True,
                verbose_name=_("count in use"))
    maximum_call = models.IntegerField(verbose_name=_('max concurrent calls'),
                   null=True, blank=True)
    #gatewaygroup = models.ManyToManyField(GatewayGroup)

    class Meta:
        db_table = u'dialer_gateway'
        verbose_name = _("dialer gateway")
        verbose_name_plural = _("dialer gateways")

    def set_name(self, name):
        self.name = name

    def __unicode__(self):
            return u"%s" % self.name

    #def prepare_phonenumber(self):
    #    return True


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
