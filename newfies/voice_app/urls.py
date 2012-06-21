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
from django.conf import settings
from voice_app.views import voiceapp_list, voiceapp_grid, \
                            voiceapp_add, voiceapp_del, \
                            voiceapp_change


urlpatterns = patterns('voice_app.views',
(r'^voiceapp/$', 'voiceapp_list'),
(r'^voiceapp_grid/$', 'voiceapp_grid'),
(r'^voiceapp/add/$', 'voiceapp_add'),
(r'^voiceapp/del/(.+)/$', 'voiceapp_del'),
(r'^voiceapp/(.+)/$', 'voiceapp_change'),
)

