#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.conf.urls import patterns, url

urlpatterns = patterns('sms_module.views',

    # SMS Campaign urls
    url(r'^sms_dashboard/$', 'sms_dashboard'),
    url(r'^sms_campaign/$', 'sms_campaign_list'),
    url(r'^sms_campaign/add/$', 'sms_campaign_add'),
    url(r'^sms_campaign/del/(.+)/$', 'sms_campaign_del'),

    # SMS Campaign Actions (start|stop|pause|abort) for customer UI
    url(r'^sms_campaign/update_sms_campaign_status_cust/(\d*)/(\d*)/$',
                    'update_sms_campaign_status_cust'),
    url(r'^sms_campaign/(.+)/$', 'sms_campaign_change'),

    # SMS Campaign Actions (start|stop|pause|abort) for Admin UI
    url(r'^update_sms_campaign_status_admin/(\d*)/(\d*)/$',
                    'update_sms_campaign_status_admin'),

    # SMS Report urls
    (r'^sms_report/$', 'sms_report'),
    (r'^export_sms_report/$', 'export_sms_report'),
)
