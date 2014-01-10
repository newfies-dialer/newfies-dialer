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


urlpatterns = patterns('dnc.views',
    # DNC urls
    (r'^module/dnc_list/$', 'dnc_list'),
    (r'^module/dnc_list/add/$', 'dnc_add'),
    (r'^module/dnc_list/contact_count/$', 'get_dnc_contact_count'),
    (r'^module/dnc_list/del/(.+)/$', 'dnc_del'),
    (r'^module/dnc_list/(.+)/$', 'dnc_change'),

    # DNC Contacts urls
    (r'^module/dnc_contact/$', 'dnc_contact_list'),
    (r'^module/dnc_contact/add/$', 'dnc_contact_add'),
    (r'^module/dnc_contact_import/$', 'dnc_contact_import'),
    (r'^module/dnc_contact/export/$', 'dnc_contact_export'),
    (r'^module/dnc_contact/export_view/$', 'dnc_contact_export_view'),
    (r'^module/dnc_contact/del/(.+)/$', 'dnc_contact_del'),
    (r'^module/dnc_contact/(.+)/$', 'dnc_contact_change'),
)
