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

from django.contrib.auth.models import User
from notification import models as notification


def common_send_notification(request, status, recipient=None):
    """User Notification (e.g. start | stop | pause | abort |
    contact/campaign limit) needs to be saved.
    It is a common function for the admin and customer UI's

    **Attributes**:

        * ``pk`` - primary key of the campaign record
        * ``status`` - get label for notifications

    **Logic Description**:

        * This function is used by ``update_campaign_status_admin()`` &
          ``update_campaign_status_cust()``

    """
    if not recipient:
        recipient = request.user
        sender = User.objects.get(is_superuser=1, username=recipient)
    else:
        if request.user.is_anonymous():
            sender = User.objects.get(is_superuser=1, username=recipient)
        else:
            sender = request.user

    if notification:
        note_label = notification.NoticeType.objects.get(default=status)
        notification.send(
            [recipient], note_label.label, {"from_user": request.user}, sender=sender)
    return True
