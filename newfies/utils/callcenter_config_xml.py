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
from user_profile.models import Manager
from agent.models import AgentProfile
from agent.constants import AGENT_STATUS, AGENT_TYPE
from callcenter.models import Queue, Tier
from callcenter.constants import STRATEGY
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET


def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def create_callcenter_config_xml(manager_id):
    """Create Callcenter XML config file"""
    top = Element('configuration', {"name": "callcenter.conf", "description": "CallCenter",})

    #settings = SubElement(top, 'settings')
    #comment = Comment('<param name="odbc-dsn" value="dsn:user:pass"/>\
    #    <param name="dbname" value="/dev/shm/callcenter.db"/>')
    #settings.append(comment)

    # Write queue
    queues = SubElement(top, 'queues')

    queue_field_list = ['tier_rule_wait_multiply_level', 'discard_abandoned_after',
                        'tier_rules_apply', 'abandoned_resume_allowed',
                        'time_base_score', 'max_wait_time_with_no_agent_time_reached',
                        'tier_rule_no_agent_no_wait', 'max_wait_time',
                        'tier_rule_wait_second', 'max_wait_time_with_no_agent',
                        'moh_sound', 'record_template', 'strategy']

    queue_list = Queue.objects.filter(manager_id=manager_id)

    for queue_obj in queue_list:
        obj_dict = queue_obj.__dict__

        # change queue name
        queue = SubElement(queues, 'queue', {"name": str(queue_obj.name)})

        for key, value in obj_dict.iteritems():
            if key in queue_field_list and value is not None:
                if key == 'strategy':
                    value = dict(STRATEGY)[value]
                    param = SubElement(queue, 'param', {"name": str(key), "value": str(value)})
                else:
                    param = SubElement(queue, 'param', {"name": str(key), "value": str(value)})

    # Write agent
    agents = SubElement(top, 'agents')

    agent_list = AgentProfile.objects.filter(manager_id=manager_id)
    agent_field_list = ['name', 'type', 'call_timeout', 'contact', 'status',
                        'max_no_answer', 'wrap_up_time', 'reject_delay_time',
                        'busy_delay_time', 'no_answer_delay_time']
    for agent_obj in agent_list:
        agent_dict = agent_obj.__dict__
        xml_agent_data = {}
        for key, value in agent_dict.iteritems():
            if key in agent_field_list and value is not None:
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
    tier_list = Tier.objects.filter(manager_id=manager_id)
    tier_field_list = ['agent_id', 'queue_id', 'level', 'position']

    for tier_obj in tier_list:
        agent_username = tier_obj.agent
        tier_dict = tier_obj.__dict__
        xml_tier_data = {}
        for key, value in tier_dict.iteritems():
            if key in tier_field_list:
                if key == 'queue_id':
                    xml_tier_data['queue'] = str(value)
                elif key == 'agent_id':
                    xml_tier_data['agent'] = str(agent_username)
                else:
                    xml_tier_data[str(key)] = str(value)

        # write tier detail
        tier = SubElement(tiers, 'tier', xml_tier_data)

    #print prettify(top)
    callcenter_file = open('/tmp/callcenter.conf.xml', 'w')
    callcenter_file.write(prettify(top))
    callcenter_file.close()

