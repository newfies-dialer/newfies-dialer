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


urlpatterns = patterns('callcenter.views',
    (r'^module/queue/$', 'queue_list'),
    (r'^module/queue/add/$', 'queue_add'),
    (r'^module/queue/del/(.+)/$', 'queue_del'),
    (r'^module/queue/(.+)/$', 'queue_change'),
    (r'^module/tier/$', 'tier_list'),
    (r'^module/tier/add/$', 'tier_add'),
    (r'^module/tier/del/(.+)/$', 'tier_del'),
    (r'^module/tier/(.+)/$', 'tier_change'),
)
