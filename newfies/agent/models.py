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
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from common.language_field import LanguageField
from django_countries import CountryField
from user_profile.models import Manager

from dialer_gateway.models import Gateway
from dialer_settings.models import DialerSetting

"""
class Agent(User):
    This defines extra features for the agent profile

    **Attributes**:

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

    **Name of DB table**: agent

    is_agent = models.BooleanField(default=True,
        verbose_name=_('Designates whether the user is an agent.'))

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
    manager = models.ForeignKey(Manager, verbose_name=_("manager"), blank=True, null=True,
        help_text=_("select manager"))

    class Meta:
        permissions = (
            ("view_queue", _('can see Queue')),
        )
        proxy = False
        app_label = 'auth'
        verbose_name = _('agent')
        verbose_name_plural = _('agents')
        permissions = (
            ("agent", _('can see Agent interface')),
        )
"""


class AgentProfile(models.Model):
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
    is_agent = models.BooleanField(default=True,
        verbose_name=_('Designates whether the user is an agent.'))
    manager = models.ForeignKey(Manager, verbose_name=_("manager"), blank=True, null=True,
        help_text=_("select manager"), related_name="manager")

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
        permissions = (
            ("view_api_explorer", _('can see API-Explorer')),
        )
        db_table = 'agent_profile'
        verbose_name = _("agent profile")
        verbose_name_plural = _("agent profiles")

    def __unicode__(self):
        return u"%s" % str(self.user)


class Agent(User):
    """Agent"""

    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('agent')
        verbose_name_plural = _('agents')

        permissions = (
            ("aegnt", _('can see agent interface')),
        )

    def save(self, **kwargs):
        if not self.pk:
            self.is_staff = 0
            self.is_superuser = 0
        super(Agent, self).save(**kwargs)


class ManagerProfile(models.Model):
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
    userprofile_gateway = models.ManyToManyField(Gateway, verbose_name=_('gateway'), null=True, blank=True)
    dialersetting = models.ForeignKey(DialerSetting,
                      verbose_name=_('dialer settings'), null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'manager_profile'
        verbose_name = _("manager profile")
        verbose_name_plural = _("manager profiles")

    def __unicode__(self):
        return u"%s" % str(self.user)
