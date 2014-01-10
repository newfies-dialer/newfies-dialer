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

urlpatterns = patterns('dialer_campaign.views',
    #  Campaign urls
    (r'^campaign/$', 'campaign_list'),
    (r'^campaign/add/$', 'campaign_add'),
    (r'^campaign/del/(.+)/$', 'campaign_del'),
    (r'^campaign_duplicate/(.+)/$', 'campaign_duplicate'),

    # Campaign Actions (start|stop|pause|abort)
    (r'^campaign/update_campaign_status_cust/(\d*)/(\d*)/$',
        'update_campaign_status_cust'),
    (r'^campaign/(.+)/$', 'campaign_change'),
    # Campaign Actions (start|stop|pause|abort) for Admin UI
    (r'^update_campaign_status_admin/(\d*)/(\d*)/$',
        'update_campaign_status_admin'),

    #  Subscriber urls
    (r'^subscribers/$', 'subscriber_list'),
    (r'^subscribers/export_subscriber/$', 'subscriber_export'),

    # Send notification to admin regarding dialer setting
    (r'^notify/admin/$', 'notify_admin'),
)
