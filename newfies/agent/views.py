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
from django.contrib.auth.decorators import login_required,\
    permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from common.common_functions import current_view


@permission_required('agent.view_agent_dashboard', login_url='/')
@login_required
def agent_dashboard(request):
    """

    **Attributes**:

        * ``template`` - frontend/agent/dashboard.html
    """
    template = 'frontend/agent/dashboard.html'

    data = {
        'module': current_view(request),
    }

    return render_to_response(template, data,
        context_instance=RequestContext(request))

