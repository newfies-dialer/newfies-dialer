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


urlpatterns = patterns('common_notification.views',
    # User notification for Customer UI
    (r'^user_notification/del/(.+)/$', 'notification_del_read'),
    (r'^user_notification/', 'user_notification'),

    # Notification Status (seen/unseen) for customer UI
    (r'^update_notification/(\d*)/$', 'update_notification'),
)
