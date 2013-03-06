#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.db import models
from django.utils.translation import ugettext_lazy as _


class DialerSetting(models.Model):
    """This defines the settings to apply to a user

    **Attributes**:

        * ``name`` - Settings name.
        * ``max_frequency`` - Max frequency, speed of the campaign.\
        This is the number of calls per minute.
        * ``callmaxduration`` - Max retries allowed
        * ``maxretry`` - Max retries allowed per user
        * ``max_calltimeout`` - Maximum number of seconds to timeout on calls
        * ``max_number_campaign`` - Max Number of campaigns
        * ``max_number_subscriber_campaign`` - Max Number of subscriber
        * ``blacklist`` - Used to blacklist phone numbers to be called
        * ``whitelist`` - Used to whitelist phone numbers to be called

    **Name of DB table**: dialer_setting
    """
    name = models.CharField(max_length=50, blank=False,
                            null=True, verbose_name=_("name"),
                            help_text=_("settings name"))
    #Campaign Settings
    max_frequency = models.IntegerField(default='100', blank=True,
                                        null=True, verbose_name=_("max frequency"),
                                        help_text=_("maximum calls per minute"))
    callmaxduration = models.IntegerField(default='1800', blank=True,
                                          null=True, verbose_name=_('max Call Duration'),
                                          help_text=_("maximum call duration in seconds (1800 = 30 Minutes)"))

    maxretry = models.IntegerField(default='3', blank=True, null=True,
                                   verbose_name=_('max retries'),
                                   help_text=_("maximum retries per user."))
    max_calltimeout = models.IntegerField(default='45', blank=True, null=True,
                                          verbose_name=_('timeout on call'),
                                          help_text=_("maximum call timeout in seconds"))

    max_number_campaign = models.IntegerField(default=10,
                                              help_text=_("maximum number of campaigns"))
    max_number_subscriber_campaign = models.IntegerField(default=10000,
                help_text=_("maximum subscribers per campaign"))

    blacklist = models.TextField(blank=True, null=True, default='', verbose_name=_("blacklist"),
        help_text=_("use regular expressions to blacklist phone numbers. For example, '^[2-4][1]+' will prevent all phone numbers starting with 2,3 or 4 and followed by 1 being called."))

    whitelist = models.TextField(blank=True, null=True, default='', verbose_name=_("whitelist"),
        help_text=_("use regular expressions to whitelist phone numbers"))

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.name)

    class Meta:
        verbose_name = _("dialer setting")
        verbose_name_plural = _("dialer settings")
        db_table = "dialer_setting"
