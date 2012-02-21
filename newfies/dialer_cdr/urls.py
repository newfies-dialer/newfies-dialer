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

from django.conf.urls.defaults import *
from django.conf import settings
from dialer_cdr.views import *


urlpatterns = patterns('',
    # VoIP Call Report urls
    (r'^voipcall_report/$', 'dialer_cdr.views.voipcall_report'),
    (r'^voipcall_report_grid/$', 'dialer_cdr.views.voipcall_report_grid'),
    (r'^export_voipcall_report/$', 'dialer_cdr.views.export_voipcall_report'),
)
