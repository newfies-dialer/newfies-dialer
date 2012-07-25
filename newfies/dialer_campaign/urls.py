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
from django.conf.urls.defaults import patterns


urlpatterns = patterns('dialer_campaign.views',

    # Phonebook urls
    (r'^phonebook/$', 'phonebook_list'),
    (r'^phonebook_grid/$', 'phonebook_grid'),
    (r'^phonebook/add/$', 'phonebook_add'),
    (r'^phonebook/contact_count/$', 'get_contact_count'),
    (r'^phonebook/del/(.+)/$', 'phonebook_del'),
    (r'^phonebook/(.+)/$', 'phonebook_change'),

    # Contacts urls
    (r'^contact/$', 'contact_list'),
    (r'^contact_grid/$', 'contact_grid'),
    (r'^contact/add/$', 'contact_add'),
    (r'^contact/import/$', 'contact_import'),
    (r'^contact/del/(.+)/$', 'contact_del'),
    (r'^contact/(.+)/$', 'contact_change'),

    # Campaign urls
    (r'^campaign/$', 'campaign_list'),
    (r'^campaign_grid/$', 'campaign_grid'),
    (r'^campaign/add/$', 'campaign_add'),
    (r'^campaign/del/(.+)/$', 'campaign_del'),
    # Campaign Actions (start|stop|pause|abort) for customer UI
    (r'^campaign/update_campaign_status_cust/(\d*)/(\d*)/$',
                    'update_campaign_status_cust'),
    (r'^campaign/(.+)/$', 'campaign_change'),

    # Campaign Actions (start|stop|pause|abort) for Admin UI
    (r'^update_campaign_status_admin/(\d*)/(\d*)/$',
                    'update_campaign_status_admin'),
    # Send notification to admin regarding dialer setting
    (r'^notify/admin/$', 'notify_admin'),
)
