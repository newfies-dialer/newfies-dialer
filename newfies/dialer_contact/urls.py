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


urlpatterns = patterns('dialer_contact.views',
    # Phonebook urls
    (r'^phonebook/$', 'phonebook_list'),
    (r'^phonebook/add/$', 'phonebook_add'),
    (r'^phonebook/contact_count/$', 'get_contact_count'),
    (r'^phonebook/del/(.+)/$', 'phonebook_del'),
    (r'^phonebook/(.+)/$', 'phonebook_change'),

    # Contacts urls
    (r'^contact/$', 'contact_list'),
    (r'^contact/add/$', 'contact_add'),
    (r'^contact_import/$', 'contact_import'),
    (r'^contact/del/(.+)/$', 'contact_del'),
    (r'^contact/(.+)/$', 'contact_change'),
)
