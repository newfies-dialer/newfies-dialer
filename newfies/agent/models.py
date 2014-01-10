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
#from agent.compat import User
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _
from user_profile.models import Manager, Profile_abstract
from .constants import AGENT_STATUS, AGENT_TYPE
from rest_framework.authtoken.models import Token


#Profile_abstract is OneToOneField(User) with additionals fields as city, states...
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

    type = models.IntegerField(choices=list(AGENT_TYPE),
                               default=AGENT_TYPE.CALLBACK,
                               verbose_name=_("type"), blank=True, null=True)
    call_timeout = models.IntegerField(default='45', blank=True, null=True,
                                       verbose_name=_('timeout on call'),
                                       help_text=_("connection timeout in seconds"))
    contact = models.CharField(max_length=90, blank=True, null=True,
                               verbose_name=_('contact'))
    status = models.IntegerField(choices=list(AGENT_STATUS),
                                 default=AGENT_STATUS.LOGGED_OUT,
                                 verbose_name=_("status"), blank=True, null=True)
    no_answer_delay_time = models.IntegerField(blank=True, null=True,
                                        verbose_name=_('no answer delay time'))
    max_no_answer = models.IntegerField(blank=True, null=True,
                                        verbose_name=_('max. no of answer'))
    wrap_up_time = models.IntegerField(blank=True, null=True,
                                       verbose_name=_('wrap up time'))
    reject_delay_time = models.IntegerField(blank=True, null=True,
                                        verbose_name=_('reject delay time'))
    busy_delay_time = models.IntegerField(blank=True, null=True,
                                          verbose_name=_('busy delay time'))
    #key = models.CharField(max_length=256, blank=True, default='')

    class Meta:
        permissions = (
            ("view_agent_dashboard", _('can see Agent dashboard')),
            ("view_agent", _('can see Agent list')),
        )
        db_table = 'agent_profile'
        verbose_name = _("agent profile")
        verbose_name_plural = _("agent profiles")

    def __unicode__(self):
        return u"%s" % str(self.user)


class Agent(User):
    """Agent Model

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


def common_signal(manager_id):
    """common_signal for agentprofile model for post_save & post_delete"""
    # from utils.callcenter_config_xml import create_callcenter_config_xml
    # create_callcenter_config_xml(manager_id)
    pass


def post_save_agentprofile(sender, **kwargs):
    """A ``post_delete`` signal is sent by the AgentProfile model instance whenever
    it is going to save.
    """
    if kwargs['created']:
        Token.objects.create(user=kwargs['instance'].user)

    common_signal(kwargs['instance'].manager_id)


def post_delete_agentprofile(sender, **kwargs):
    """A ``post_delete`` signal is sent by the AgentProfile model instance whenever
    it is going to delete.
    """
    common_signal(kwargs['instance'].manager_id)

post_save.connect(post_save_agentprofile, sender=AgentProfile)
post_delete.connect(post_delete_agentprofile, sender=AgentProfile)

# Create an easy way to use the user profile
# using user.profile will get or create a user profile
# object
Agent.profile = property(lambda u: AgentProfile.objects.get_or_create(user=u)[0])
Agent.api_key = property(lambda u: Token.objects.get_or_create(user=u)[0].key)


#from django.dispatch import receiver


#@receiver(post_save, sender=User)
#def create_auth_token(sender, instance=None, created=False, **kwargs):
#    if created:
#        Token.objects.create(user=instance)
