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
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext as _
#from agent.function_def import agent_list
#from agent.models import AgentProfile


class AgentFilter(SimpleListFilter):
    title = _('agent')
    parameter_name = 'agent'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return []  # agent_list()

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() is not None:
            #agent_id_list = AgentProfile.objects.values_list('user_id', flat=True).all()
            return queryset  # .filter(agent_id__in=agent_id_list)
        else:
            return queryset
