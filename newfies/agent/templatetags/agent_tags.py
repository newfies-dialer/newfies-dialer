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

from django.template.defaultfilters import register
from agent.models import AgentProfile


@register.assignment_tag(name='agent_check')
def agent_check(user):
    try:
        AgentProfile.objects.get(user=user, is_agent=True)
        return True
    except:
        return False