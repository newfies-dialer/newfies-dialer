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
from django_countries import CountryField
from common.intermediate_model_base_class import Model
from dialer_contact.constants import CONTACT_STATUS
import jsonfield


class Phonebook(Model):
    """This defines the Phonebook

    **Attributes**:

        * ``name`` - phonebook name.
        * ``description`` - description about the phonebook.

    **Relationships**:

        * ``user`` - Foreign key relationship to the User model.\
        Each phonebook is assigned to a User

    **Name of DB table**: dialer_phonebook
    """
    name = models.CharField(max_length=90, verbose_name=_('Name'))
    description = models.TextField(null=True, blank=True,
                                   help_text=_("Phonebook Notes"))
    user = models.ForeignKey('auth.User', related_name='Phonebook owner')
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('Date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_phonebook", _('Can see Phonebook')),
        )
        db_table = u'dialer_phonebook'
        verbose_name = _("Phonebook")
        verbose_name_plural = _("Phonebooks")

    def __unicode__(self):
            return u"%s" % self.name

    def phonebook_contacts(self):
        """This will return a count of the contacts in the phonebook"""
        return Contact.objects.filter(phonebook=self.id).count()
    phonebook_contacts.allow_tags = True
    phonebook_contacts.short_description = _('Contacts')


class Contact(Model):
    """This defines the Contact

    **Attributes**:

        * ``contact`` - Contact no
        * ``last_name`` - Contact's last name
        * ``first_name`` - Contact's first name
        * ``email`` - Contact's e-mail address
        * ``city`` - city name
        * ``description`` - description about a Contact
        * ``status`` - contact status
        * ``additional_vars`` - Additional variables

    **Relationships**:

        * ``phonebook`` - Foreign key relationship to the Phonebook model.\
        Each contact mapped with a phonebook
        * ``country`` - Foreign key relationship to the Country model.\
        Each contact mapped with a country

    **Name of DB table**: dialer_contact
    """
    phonebook = models.ForeignKey(Phonebook, verbose_name=_('Phonebook'),
                                  help_text=_("Select Phonebook"))
    contact = models.CharField(max_length=90, verbose_name=_('Contact Number'))
    status = models.IntegerField(choices=list(CONTACT_STATUS), default='1',
                                 verbose_name=_("Status"), blank=True, null=True)
    last_name = models.CharField(max_length=120, blank=True, null=True,
                                 verbose_name=_('Last Name'))
    first_name = models.CharField(max_length=120, blank=True, null=True,
                                  verbose_name=_('First Name'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('Email'))
    country = CountryField(blank=True, null=True, verbose_name=_('Country'))
    city = models.CharField(max_length=120, blank=True, null=True,
                            verbose_name=_('City'))
    additional_vars = jsonfield.JSONField(null=True, blank=True,
                                          verbose_name=_('Additional parameters (JSON)'),
                                          help_text=_("Enter the list of parameters in Json format, ie. {\"age\": \"32\"}"))
    description = models.TextField(null=True, blank=True,
                                   verbose_name=_("Notes"))
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('Date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_contact", _('Can see Contact')),
        )
        db_table = u'dialer_contact'
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

    def __unicode__(self):
        return u"%s (%s)" % (self.contact, self.last_name)

    def contact_name(self):
        """Return Contact Name"""
        return u"%s %s" % (self.first_name, self.last_name)
    contact_name.allow_tags = True
    contact_name.short_description = _('Name')
