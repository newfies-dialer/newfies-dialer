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
from django.conf.urls import patterns

urlpatterns = patterns('agent.views',
    (r'^agent_login_form/$', 'agent_login_form'),
    (r'^agent_login/$', 'agent_login'),
    (r'^agent_logout/$', 'agent_logout'),
    (r'^agent_dashboard/$', 'agent_dashboard'),
    (r'^agent_detail/$', 'agent_detail'),
    (r'^agent_detail_change/$', 'agent_detail_change'),
    (r'^module/agent/$', 'agent_list'),
    (r'^module/agent/add/$', 'agent_add'),
    (r'^module/agent/del/(.+)/$', 'agent_del'),
    (r'^module/agent/password/(.+)/$', 'agent_change_password'),
    (r'^module/agent/(.+)/$', 'agent_change'),
)
