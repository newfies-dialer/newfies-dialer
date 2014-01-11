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
from django.conf.urls import patterns, url
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from agent.api_views import (AgentProfileViewSet,
    AgentPasswordViewSet, obtain_auth_token_login, AgentSubscriberViewSet,
    AgentQueueStatusViewSet)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'agents-profile', AgentProfileViewSet)
router.register(r'agents-password', AgentPasswordViewSet, 'agents_password')
router.register(r'agent-subscriber', AgentSubscriberViewSet, 'agent_subscriber')

# # The API URLs are now determined automatically by the router.
# # Additionally, we include the login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^agent-rest-api/', include(router.urls)),
    # Login and logout views for the browsable API
    url(r'^agent-rest-api/api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),

    url(r'^agent-rest-api/agent-queue-status/(?P<agent_id>[0-9]+)/$', AgentQueueStatusViewSet.as_view(), name="agent_queue_status"),
)

# curl -i -X POST http://127.0.0.1:8000/api/api-token-auth/ -d "username=testagent&password=testagent"
urlpatterns += patterns('',
    #url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token')
    #Rewrite obtain_auth_token_login to enable session login
    url(r'^agent-rest-api/api-token-auth/', obtain_auth_token_login)
)
