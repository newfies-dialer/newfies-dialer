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
from django.db.models.signals import post_save
from common.intermediate_model_base_class import Model
from user_profile.models import Manager
from agent.models import AgentProfile
from agent.constants import AGENT_STATUS, AGENT_TYPE
from callcenter.constants import STRATEGY


class Queue(Model):
    """This defines the callcenter queue

    **XML output**:
        <param name="strategy" value="agent-with-least-talk-time"/>
        <param name="moh-sound" value="$${hold_music}"/>
        <param name="record-template" value="$${base_dir}/recordings/sales/${strftime(%Y-%m-%d-%H-%M-%S)}.${destination_number}.${caller_id_number}.${uuid}.wav"/>
        <param name="time-base-score" value="queue"/>
        <param name="tier-rules-apply" value="false"/>
        <param name="tier-rule-wait-second" value="300"/>
        <param name="tier-rule-wait-multiply-level" value="true"/>
        <param name="tier-rule-no-agent-no-wait" value="false"/>
        <param name="discard-abandoned-after" value="14400"/>
        <param name="abandoned-resume-allowed" value="True"/>
        <param name="max-wait-time" value="0"/>
        <param name="max-wait-time-with-no-agent" value="120"/>
        <param name="max-wait-time-with-no-agent-time-reached" value="5"/>

    **Attributes**:

        * ``strategy`` - Queue strategy
        * ```` -


    **Relationships**:

        * ``manager`` - Foreign key relationship to the manager model.

    **Name of DB table**: queue
    """
    manager = models.ForeignKey(Manager, verbose_name=_("manager"), blank=True, null=True,
                                help_text=_("select manager"), related_name="queue manager")
    strategy = models.IntegerField(choices=list(STRATEGY),
                                  default=STRATEGY.agent_with_least_talk_time,
                                  verbose_name=_("status"), blank=True, null=True)
    moh_sound = models.CharField(verbose_name=_("moh-sound"),
                                max_length=250, null=True, blank=True)
    record_template = models.CharField(verbose_name=_("record-template"),
                                max_length=250, null=True, blank=True)
    time_base_score = models.CharField(verbose_name=_("time-base-score"),
                                max_length=50, null=True, blank=True, default='queue')
    tier_rules_apply = models.BooleanField(default=False, verbose_name=_("tier-rules-apply"))
    tier_rule_wait_second = models.IntegerField(verbose_name=_("tier-rule-wait-second"),
                                max_length=250, null=True, blank=True, default=300)
    tier_rule_wait_multiply_level = models.BooleanField(default=True,
                                            verbose_name=_("tier-rule-wait-multiply-level"))
    tier_rule_no_agent_no_wait = models.BooleanField(default=False,
                                                     verbose_name=_("tier-rule-no-agent-no-wait"))
    discard_abandoned_after = models.IntegerField(verbose_name=_("discard-abandoned-after"),
                                                  max_length=250, null=True, blank=True,
                                                  default=14400)
    abandoned_resume_allowed = models.BooleanField(default=True,
                                                   verbose_name=_("abandoned-resume-allowed"))
    max_wait_time = models.IntegerField(verbose_name=_("max-wait-time"),
                                        max_length=250, null=True, blank=True,
                                        default=0)
    max_wait_time_with_no_agent = models.IntegerField(verbose_name=_("max-wait-time-with-no-agent"),
                                                      max_length=250, null=True, blank=True,
                                                      default=120)
    max_wait_time_with_no_agent_time_reached = models.IntegerField(verbose_name=_("max-wait-time-with-no-agent-time-reached"),
                                                                   max_length=250, null=True, blank=True,
                                                                   default=5)

    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_queue_list", _('can see Queue list')),
        )
        db_table = u'callcenter_queue'
        verbose_name = _("queue")
        verbose_name_plural = _("queues")

    def __unicode__(self):
        NAME = dict(STRATEGY)
        return u"%s [%s]" % (self.id, NAME[self.strategy])


class Tier(Model):
    """This defines the callcenter tier

    **XML output**:
        <!-- If no level or position is provided, they will default to 1.  You should do this to keep db value on restart. -->
        <!-- agent 1000 will be in both the sales and support queues -->
        <tier agent="1000@default" queue="sales@default" level="1" position="1"/>
        <tier agent="1000@default" queue="support@default" level="1" position="1"/>
        <!-- agent 1001 will only be in the support queue -->
        <tier agent="1001@default" queue="support@default" level="1" position="1"/>

    **Attributes**:

        * ``request_uuid`` - Unique id
        * ```` -


    **Relationships**:

        * ``manager`` - Foreign key relationship to the manager model.

    **Name of DB table**: queue
    """
    manager = models.ForeignKey(Manager,
                                verbose_name=_("manager"), blank=True, null=True,
                                help_text=_("select manager"), related_name="tier manager")
    agent = models.ForeignKey(AgentProfile,
                              verbose_name=_("agent"), blank=True, null=True,
                              help_text=_("select agent"), related_name="agent")
    queue = models.ForeignKey(Queue,
                              verbose_name=_("queue"), blank=True, null=True,
                              help_text=_("select queue"), related_name="queue")
    level = models.IntegerField(verbose_name=_("level"), default=1)
    position = models.IntegerField(verbose_name=_("position"), default=1)

    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_tier_list", _('can see Tier list')),
        )
        db_table = u'callcenter_tier'
        verbose_name = _("tier")
        verbose_name_plural = _("tiers")

    def __unicode__(self):
            return u"%s" % (self.id)


def post_save_update_xml(sender, **kwargs):
    """A ``post_save`` signal is sent by the Contact model instance whenever
    it is going to save.

    **Logic Description**:

        *
    """
    if not kwargs['created']:
        obj = kwargs['instance']
        from xml.etree.ElementTree import Element, SubElement, Comment, tostring

        top = Element('configuration', {"name": "callcenter.conf", "description": "CallCenter",})

        #settings = SubElement(top, 'settings')
        #comment = Comment('<param name="odbc-dsn" value="dsn:user:pass"/>\
        #    <param name="dbname" value="/dev/shm/callcenter.db"/>')
        #settings.append(comment)

        # Write queue
        queues = SubElement(top, 'queues')

        queue_field_list = ['tier_rule_wait_multiply_level', 'discard_abandoned_after',
        'tier_rules_apply', 'abandoned_resume_allowed', 'time_base_score',
        'max_wait_time_with_no_agent_time_reached', 'tier_rule_no_agent_no_wait',
        'max_wait_time', 'tier_rule_wait_second', 'max_wait_time_with_no_agent',
        'moh_sound', 'record_template', 'strategy']

        queue_list = Queue.objects.filter(manager=obj.manager)

        for queue_obj in queue_list:
            obj_dict = queue_obj.__dict__

            # change queue name
            queue = SubElement(queues, 'queue', {"name": str(queue_obj.id)})

            for key, value in obj_dict.iteritems():
                if key in queue_field_list:
                    if key == 'strategy':
                        value = dict(STRATEGY)[value]
                        param = SubElement(queue, 'param', {"name": str(key), "value": str(value)})
                    else:
                        param = SubElement(queue, 'param', {"name": str(key), "value": str(value)})

        # Write agent
        agents = SubElement(top, 'agents')

        agent_list = AgentProfile.objects.filter(manager=obj.manager)
        agent_field_list = ['name', 'type', 'call_timeout', 'contact', 'status',
                            'max_no_answer', 'wrap_up_time', 'reject_delay_time',
                            'busy_delay_time', 'no_answer_delay_time']
        for agent_obj in agent_list:
            agent_dict = agent_obj.__dict__
            xml_agent_data = {}
            for key, value in agent_dict.iteritems():
                if key in agent_field_list:
                    if key == 'type':
                        value = dict(AGENT_TYPE)[value]
                        xml_agent_data[str(key)] = str(value)

                    elif key == 'status':
                        value = dict(AGENT_STATUS)[value]
                        xml_agent_data[str(key)] = str(value)
                    else:
                        key = key.replace('_', '-')
                        xml_agent_data[str(key)] = str(value)

            # write agent detail
            agent = SubElement(agents, 'agent', xml_agent_data)

        # Write tier
        tiers = SubElement(top, 'tiers')
        tier_list = Tier.objects.filter(manager=obj.manager)
        tier_field_list = ['agent_id', 'queue_id', 'level', 'position']

        for tier_obj in tier_list:
            tier_dict = tier_obj.__dict__
            xml_tier_data = {}
            for key, value in tier_dict.iteritems():
                if key in tier_field_list:
                    if key == 'queue_id':
                        xml_tier_data['queue'] = str(value)
                    elif key == 'agent_id':
                        xml_tier_data['agent'] = str(value)
                    else:
                        xml_tier_data[str(key)] = str(value)

            # write tier detail
            tier = SubElement(tiers, 'tier', xml_tier_data)

        #print tostring(top)
        import xml.etree.ElementTree as ET
        tree = ET.ElementTree(top)
        tree.write("/tmp/callcenter.conf.xml")


post_save.connect(post_save_update_xml, sender=Tier)
