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
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from common.language_field import LanguageField
from django_countries.fields import CountryField
from dialer_gateway.models import Gateway
from dialer_settings.models import DialerSetting
import uuid
import hmac
import hashlib


def generate_key():
    # Get a random UUID.
    new_uuid = uuid.uuid4()
    # Hmac that beast.
    return hmac.new(str(new_uuid), digestmod=hashlib.sha1).hexdigest()


class Profile_abstract(models.Model):
    """This defines the Survey template

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
    """
    user = models.OneToOneField(User)
    address = models.CharField(blank=True, null=True,
                               max_length=200, verbose_name=_('address'))
    city = models.CharField(max_length=120, blank=True, null=True,
                            verbose_name=_('city'))
    state = models.CharField(max_length=120, blank=True, null=True,
                             verbose_name=_('state'))
    country = CountryField(blank=True, null=True, verbose_name=_('country'))
    zip_code = models.CharField(max_length=120, blank=True, null=True,
                                verbose_name=_('zip code'))
    phone_no = models.CharField(max_length=90, blank=True, null=True,
                                verbose_name=_('phone number'))
    fax = models.CharField(max_length=90, blank=True, null=True,
                           verbose_name=_('fax Number'))
    company_name = models.CharField(max_length=90, blank=True, null=True,
                                    verbose_name=_('company name'))
    company_website = models.URLField(max_length=90, blank=True, null=True,
                                      verbose_name=_('company website'))
    language = LanguageField(blank=True, null=True, verbose_name=_('language'))
    note = models.CharField(max_length=250, blank=True, null=True,
                            verbose_name=_('note'))
    accountcode = models.PositiveIntegerField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(Profile_abstract):
    """This defines extra features for the user

    **Relationships**:

        * ``userprofile_gateway`` - ManyToMany
        * ``dialersetting`` - Foreign key relationship to the DialerSetting \
        model.

    **Name of DB table**: user_profile
    """
    userprofile_gateway = models.ManyToManyField(Gateway, verbose_name=_('gateway'))
    dialersetting = models.ForeignKey(DialerSetting, verbose_name=_('dialer settings'),
        null=True, blank=True)
    #Used for tastypie
    #key = models.CharField(max_length=256, blank=True, default='')

    class Meta:
        permissions = (
            ("view_api_explorer", _('can see API-Explorer')),
        )
        db_table = 'user_profile'
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    def __unicode__(self):
        return u"%s" % str(self.user)

    # def save(self, *args, **kwargs):
    #     if not self.key:
    #         self.key = generate_key()

    #     return super(UserProfile, self).save(*args, **kwargs)


class Manager(User):
    """
    Manager are user that have access to the Customer/Manager interface.
    They don't have access to the admin.
    Manager, create surveys, phonebooks, they also create and run campaign.
    They are the actually user of the system.
    They also can create Agents which will receive the calls.
    """

    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('manager')
        verbose_name_plural = _('managers')

    def save(self, **kwargs):
        if not self.pk:
            self.is_staff = 0
            self.is_superuser = 0
        super(Manager, self).save(**kwargs)


class Staff(User):
    """Admin - Super User
    Staff are user that have access to the admin interface with restriction.
    They can apply few changes on the admin UI based on their permission.
    It's important to configure well their permission.
    A staff members can for instance access to overall reporting, or review
    call queues status.
    """

    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('admin')
        verbose_name_plural = _('admins')

    def save(self, **kwargs):
        if not self.pk:
            self.is_staff = 1
            self.is_superuser = 1
        super(Staff, self).save(**kwargs)
