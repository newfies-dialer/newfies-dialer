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
from agent.models import Agent, AgentProfile


def manager_list():
    """Return all managers of the system"""
    manager_list = []
    list = Manager.objects.values_list('id', 'username')\
        .filter(is_staff=True, is_superuser=False, is_active=True).order_by('id')
    for l in list:
        manager_list.append((l[0], l[1]))
    return manager_list


def agent_list(managert_id=None):
    """Return all agents of the system"""
    agent_list = []
    agent_id_list = AgentProfile.objects.values_list('user_id', flat=True)

    if managert_id is not None:
        agent_id_list = agent_id_list.filter(manager_id=int(managert_id))

    list = Agent.objects.values_list('id', 'username')\
        .filter(id__in=agent_id_list).order_by('id')

    for l in list:
        agent_list.append((l[0], l[1]))
    return agent_list
