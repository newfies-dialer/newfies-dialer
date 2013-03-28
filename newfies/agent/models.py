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
from user_profile.models import Manager, Profile_abstract


class AgentProfile(Profile_abstract):
    """This defines extra features for the user

    **Attributes**:

        * ``is_agent`` - Designates whether the user is an agent

    **Relationships**:

        * ``manager`` - Foreign key relationship to the manager model.

    **Name of DB table**: agent_profile
    """
    is_agent = models.BooleanField(default=True,
        verbose_name=_('Designates whether the user is an agent.'))
    manager = models.ForeignKey(Manager, verbose_name=_("manager"), blank=True, null=True,
        help_text=_("select manager"), related_name="manager")

    class Meta:
        permissions = (
            ("view_agent_dashboard", _('can see Agent dashboard')),
        )
        db_table = 'agent_profile'
        verbose_name = _("agent profile")
        verbose_name_plural = _("agent profiles")

    def __unicode__(self):
        return u"%s" % str(self.user)


class Agent(User):
    """Agent

    Agents are user that have access to the Agent interface.
    They don't have access to the admin/manager.
    """
    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('agent')
        verbose_name_plural = _('agents')

    def save(self, **kwargs):
        if not self.pk:
            self.is_staff = 0
            self.is_superuser = 0
        super(Agent, self).save(**kwargs)

    def is_agent(self):
        try:
            AgentProfile.objects.get(user=self)
            return True
        except:
            return False
    User.add_to_class('is_agent', is_agent)

    def manager_name(self):
        """This will show manager name for each agent"""
        try:
            name = AgentProfile.objects.get(user_id=self.id).manager
        except:
            name = ''

        return name
    manager_name.allow_tags = True
    manager_name.short_description = _('manager')

