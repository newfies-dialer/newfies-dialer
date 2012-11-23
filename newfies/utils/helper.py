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

from django.contrib.auth.decorators import login_required
from notification import models as notification


@login_required
def notice_count(request):
    """Get count of logged in user's notifications"""
    notice_count = notification.Notice.objects\
        .filter(recipient=request.user, unseen=1)\
        .count()
    return notice_count


def common_notification_status(request, id):
    """Notification Status (e.g. seen/unseen) need to be change.
    It is a common function for admin and customer UI

    **Attributes**:

        * ``pk`` - primary key of notice record

    **Logic Description**:

        * Selected Notification's status need to be changed.
          Changed status can be seen or unseen.
    """
    notice = notification.Notice.objects.get(pk=id)
    if notice.unseen == 1:
        notice.unseen = 0
    else:
        notice.unseen = 1
    notice.save()
    return True
