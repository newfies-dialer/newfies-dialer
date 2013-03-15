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


urlpatterns = patterns('dnc.views',
    # DNC urls
    (r'^dnc/$', 'dnc_list'),
    (r'^dnc/add/$', 'dnc_add'),
    #(r'^dnc/contact_count/$', 'get_dnc_contact_count'),
    #(r'^dnc/del/(.+)/$', 'dnc_del'),
    #(r'^dnc/(.+)/$', 'dnc_change'),

    # Contacts urls
    #(r'^dnc_contact/$', 'dnc_contact_list'),
    #(r'^contact/add/$', 'dnc_contact_add'),
    #(r'^dnc_contact/import/$', 'dnc_contact_import'),
    #(r'^dnc_contact/del/(.+)/$', 'dnc_contact_del'),
    #(r'^dnc_contact/(.+)/$', 'dnc_contact_change'),
)
