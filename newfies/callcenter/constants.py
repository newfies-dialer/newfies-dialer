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

from django.utils.translation import ugettext_lazy as _
from common.utils import Choice


class STRATEGY(Choice):
    ring_all = 1, 'ring-all'
    longest_idle_agent = 2, 'longest-idle-agent'
    round_robin = 3, 'round-robin'
    top_down = 4, 'top-down'
    agent_with_least_talk_time = 5, 'agent-with-least-talk-time'
    agent_with_fewest_calls = 6, 'agent-with-fewest-calls'
    sequentially_by_agent_order = 7, 'sequentially-by-agent-order'
    random = 8, 'random'


class QUEUE_COLUMN_NAME(Choice):
    name = _('name')
    strategy = _('strategy')
    time_base_score = _('time base score')
    date = _('date')


class TIER_COLUMN_NAME(Choice):
    agent = _('agent')
    queue = _('queue')
    level = _('level')
    position = _('position')
    date = _('date')


class TIME_BASE_SCORE_TYPE(Choice):
    queue = 'queue'
    system = 'system'


class AGENT_CALLSTATE_TYPE(Choice):
    agent_offering = 'agent-offering'
    bridge_agent_start = 'bridge-agent-start'
