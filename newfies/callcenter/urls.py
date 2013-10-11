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
from django.conf.urls import patterns


urlpatterns = patterns('callcenter.views',

    (r'^queue/$', 'queue_list'),
    (r'^queue/add/$', 'queue_add'),
    (r'^queue/del/(.+)/$', 'queue_del'),
    (r'^queue/(.+)/$', 'queue_change'),

    (r'^tier/$', 'tier_list'),
    (r'^tier/add/$', 'tier_add'),
    (r'^tier/del/(.+)/$', 'tier_del'),
    (r'^tier/(.+)/$', 'tier_change'),
)