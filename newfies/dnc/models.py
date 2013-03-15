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


class DNC(models.Model):
    """This defines the Do Not Call List

    **Attributes**:

        * ``name`` - List name.

    **Relationships**:

        * ``user`` - Foreign key relationship to the User model.

    """
    name = models.CharField(max_length=50, blank=False,
                            null=True, verbose_name=_("name"),
                            help_text=_("DNC name"))
    user = models.ForeignKey('auth.User', related_name='DNC owner')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.name)

    class Meta:
        verbose_name = _("DNC list")
        verbose_name_plural = _("DNC lists")


class DNCContact(models.Model):
    """This defines the Do Not Call Contact for each DNC List

    **Attributes**:

        * ``phone_number`` - Phone number
        * ``dnc`` - DNC List

    **Relationships**:

        * ``user`` - Foreign key relationship to the User model.
        * ``used_gateway`` - Foreign key relationship to the Gateway model.
        * ``callrequest`` - Foreign key relationship to the Callrequest model.

    **Name of DB table**: dialer_cdr
    """
    dnc = models.ForeignKey(DNC, null=True, blank=True,
                    verbose_name=_("DNC List"))
    phone_number = models.CharField(max_length=120, db_index=True, null=True, blank=True,
        verbose_name=_("phone number"))

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True,)

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.phone_number)

    class Meta:
        verbose_name = _("DNC contact")
        verbose_name_plural = _("DNC contacts")
