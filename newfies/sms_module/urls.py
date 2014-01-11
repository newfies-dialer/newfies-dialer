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

from django.conf.urls import patterns

urlpatterns = patterns('sms_module.views',

    # SMS Campaign urls
    (r'^sms_dashboard/$', 'sms_dashboard'),
    (r'^sms_campaign/$', 'sms_campaign_list'),
    (r'^sms_campaign/add/$', 'sms_campaign_add'),
    (r'^sms_campaign/del/(.+)/$', 'sms_campaign_del'),
    (r'^sms_campaign/duplicate/(.+)/$', 'sms_campaign_duplicate'),
    (r'^sms_campaign/text_message/(.+)/$', 'sms_campaign_text_message'),

    # SMS Campaign Actions (start|stop|pause|abort) for customer UI
    (r'^sms_campaign/update_sms_campaign_status_cust/(\d*)/(\d*)/$',
        'update_sms_campaign_status_cust'),
    (r'^sms_campaign/(.+)/$', 'sms_campaign_change'),

    # SMS Campaign Actions (start|stop|pause|abort) for Admin UI
    (r'^update_sms_campaign_status_admin/(\d*)/(\d*)/$',
        'update_sms_campaign_status_admin'),

    # SMS Report urls
    (r'^sms_report/$', 'sms_report'),
    (r'^export_sms_report/$', 'export_sms_report'),
)
