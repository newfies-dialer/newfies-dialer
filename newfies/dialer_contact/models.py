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
from django_countries.fields import CountryField
from common.intermediate_model_base_class import Model
from dialer_contact.constants import CONTACT_STATUS
import jsonfield
import re


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
    name = models.CharField(max_length=90, verbose_name=_('name'))
    description = models.TextField(null=True, blank=True,
                                   help_text=_("phonebook notes"))
    user = models.ForeignKey('auth.User', related_name='Phonebook owner')
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_phonebook", _('can see phonebook')),
        )
        db_table = u'dialer_phonebook'
        verbose_name = _("phonebook")
        verbose_name_plural = _("phonebooks")

    def __unicode__(self):
            return u"%s" % self.name

    def phonebook_contacts(self):
        """This will return a count of the contacts in the phonebook"""
        return Contact.objects.filter(phonebook=self.id).count()
    phonebook_contacts.allow_tags = True
    phonebook_contacts.short_description = _('contacts')


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
    phonebook = models.ForeignKey(Phonebook, verbose_name=_('phonebook'))
    contact = models.CharField(max_length=90, verbose_name=_('contact number'))
    status = models.IntegerField(choices=list(CONTACT_STATUS),
                                 default=CONTACT_STATUS.ACTIVE,
                                 verbose_name=_("status"), blank=True, null=True)
    last_name = models.CharField(max_length=120, blank=True, null=True,
                                 verbose_name=_('last name'))
    first_name = models.CharField(max_length=120, blank=True, null=True,
                                  verbose_name=_('first name'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('email'))
    address = models.CharField(max_length=250, null=True, blank=True,
                               verbose_name=_("address"))
    city = models.CharField(max_length=120, blank=True, null=True,
                            verbose_name=_('city'))
    state = models.CharField(max_length=120, blank=True, null=True,
                             verbose_name=_('state'))
    country = CountryField(blank=True, null=True, verbose_name=_('country'))
    unit_number = models.CharField(max_length=50, blank=True, null=True,
                                   verbose_name=_("unit number"))
    additional_vars = jsonfield.JSONField(null=True, blank=True,
                                          verbose_name=_('additional parameters (JSON)'),
                                          help_text=_("enter the list of parameters in JSON format, e.g. {\"age\": \"32\"}"))
    description = models.TextField(null=True, blank=True,
                                   verbose_name=_("notes"))
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_contact", _('can see contact')),
        )
        db_table = u'dialer_contact'
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")

    def __unicode__(self):
        return u"%s (%s)" % (self.contact, self.last_name)

    def contact_name(self):
        """Return Contact Name"""
        return u"%s %s" % (self.first_name, self.last_name)

    def replace_tag(self, text):
        """
        Replace tag by contact values.
        This function will replace all the following tags:

            {last_name}
            {first_name}
            {email}
            {country}
            {city}
            {phone_number}

        as well as, get additional_vars, and replace json tags
        """
        text = str(text).lower()
        taglist = {
            'last_name': self.last_name,
            'first_name': self.first_name,
            'email': self.email,
            'country': self.country,
            'city': self.city,
            'phone_number': self.contact,
        }
        if self.additional_vars:
            for index in self.additional_vars:
                taglist[index] = self.additional_vars[index]

        for ind in taglist:
            text = text.replace('{' + ind + '}', str(taglist[ind]))

        # replace the tags not found
        text = re.sub('{(\w+)}', '', text)
        return text

    contact_name.allow_tags = True
    contact_name.short_description = _('name')
