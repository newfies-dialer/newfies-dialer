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
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from common.language_field import LanguageField
from django_countries import CountryField
from dialer_gateway.models import Gateway
from dialer_settings.models import DialerSetting


class UserProfile(models.Model):
    """This defines extra features for the user

    **Attributes**:

        * ``accountcode`` - Account name.
        * ``address`` -
        * ``city`` -
        * ``state`` -
        * ``address`` -
        * ``country`` -
        * ``zip_code`` -
        * ``phone_no`` -
        * ``fax`` -
        * ``company_name`` -
        * ``company_website`` -
        * ``language`` -
        * ``note`` -

    **Relationships**:

        * ``user`` - Foreign key relationship to the User model.
        * ``userprofile_gateway`` - ManyToMany
        * ``userprofile_voipservergroup`` - ManyToMany
        * ``dialersetting`` - Foreign key relationship to the DialerSetting \
        model.

    **Name of DB table**: user_profile
    """
    user = models.OneToOneField(User)
    address = models.CharField(blank=True, null=True,
                               max_length=200, verbose_name=_('Address'))
    city = models.CharField(max_length=120, blank=True, null=True,
                            verbose_name=_('City'))
    state = models.CharField(max_length=120, blank=True, null=True,
                             verbose_name=_('State'))
    country = CountryField(blank=True, null=True, verbose_name=_('Country'))
    zip_code = models.CharField(max_length=120, blank=True, null=True,
                                verbose_name=_('Zip code'))
    phone_no = models.CharField(max_length=90, blank=True, null=True,
                                verbose_name=_('Phone number'))
    fax = models.CharField(max_length=90, blank=True, null=True,
                           verbose_name=_('Fax Number'))
    company_name = models.CharField(max_length=90, blank=True, null=True,
                                    verbose_name=_('Company name'))
    company_website = models.URLField(verify_exists=False,
                                      max_length=90, blank=True, null=True,
                                      verbose_name=_('Company website'))
    language = LanguageField(blank=True, null=True, verbose_name=_('Language'))
    note = models.CharField(max_length=250, blank=True, null=True,
                            verbose_name=_('Note'))
    accountcode = models.PositiveIntegerField(null=True, blank=True)
    #voip_gateway = models.ForeignKey(Gateway, verbose_name='VoIP Gateway',
    #                            help_text=_("Select VoIP Gateway"))
    userprofile_gateway = models.ManyToManyField(Gateway,
                                            verbose_name=_('Gateway'))
    dialersetting = models.ForeignKey(DialerSetting,
                      verbose_name=_('Dialer settings'), null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_api_explorer", _('Can see API-Explorer')),
        )
        db_table = 'user_profile'
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profile")


class Customer(User):

    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')


class Staff(User):

    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('Admin')
        verbose_name_plural = _('Admins')

    def save(self, **kwargs):
        if not self.pk:
            self.is_staff = 1
            self.is_superuser = 1
        super(Staff, self).save(**kwargs)
