#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.conf.urls import patterns

urlpatterns = patterns('dialer_cdr.views',
                       # VoIP Call Report urls
                       (r'^voipcall_report/$', 'voipcall_report'),
                       (r'^export_voipcall_report/$', 'export_voipcall_report'),
                       )
