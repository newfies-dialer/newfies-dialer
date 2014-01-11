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


class DNC(models.Model):
    """This defines the Do Not Call List

    **Attributes**:

        * ``name`` - List name.

    **Relationships**:

        * ``user`` - Foreign key relationship to the User model.

    **Name of DB table**: dnc_list
    """
    name = models.CharField(max_length=50, blank=False,
                            null=True, verbose_name=_("name"),
                            help_text=_("Enter a DNC list name"))
    description = models.TextField(null=True, blank=True,
                                   help_text=_("DNC notes"))
    user = models.ForeignKey('auth.User', related_name='DNC owner')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.name)

    class Meta:
        permissions = (
            ("view_dnc", _('can see Do Not Call list')),
        )
        db_table = "dnc_list"
        verbose_name = _("Do Not Call list")
        verbose_name_plural = _("Do Not Call lists")

    def dnc_contacts_count(self):
        """This will return a count of the contacts in the dnc"""
        return DNCContact.objects.filter(dnc=self.id).count()
    dnc_contacts_count.allow_tags = True
    dnc_contacts_count.short_description = _('DNC contacts')


class DNCContact(models.Model):
    """This defines the Do Not Call Contact for each DNC List

    **Attributes**:

        * ``phone_number`` - Phone number
        * ``dnc`` - DNC List

    **Relationships**:

        * ``dnc`` - Foreign key relationship to the DNC model.

    **Name of DB table**: dnc_contact
    """
    dnc = models.ForeignKey(DNC, verbose_name=_("Do Not Call List"))
    phone_number = models.CharField(max_length=120, db_index=True,
                                    verbose_name=_("phone number"))

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True,)

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.phone_number)

    class Meta:
        permissions = (
            ("view_dnc_contact", _('can see Do Not Call contact')),
        )
        db_table = "dnc_contact"
        verbose_name = _("Do Not Call contact")
        verbose_name_plural = _("Do Not Call contacts")
