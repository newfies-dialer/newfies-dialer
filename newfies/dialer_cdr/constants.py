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

from django.utils.translation import gettext as _
from common.utils import Choice


class CALLREQUEST_STATUS(Choice):
    """
    Store the Call Request Status
    """
    PENDING = 1, _("Pending")
    FAILURE = 2, _("Failure")
    RETRY = 3, _("Retry")
    SUCCESS = 4, _("Success")
    ABORT = 5, _("Abort")
    PAUSE = 6, _("Pause")
    PROCESS = 7, _("Processing")
    IN_PROGRESS = 8, _("In Progress")


class CALLREQUEST_TYPE(Choice):
    """
    Store the Call Request Type
    """
    ALLOW_RETRY = 1, _('ALLOW RETRY')
    CANNOT_RETRY = 2, _('CANNOT RETRY')
    RETRY_DONE = 3, _('RETRY DONE')


class LEG_TYPE(Choice):
    """
    Store the Leg Type
    """
    A_LEG = 1, _('A-Leg')
    B_LEG = 2, _('B-Leg')


class VOIPCALL_DISPOSITION(Choice):
    """
    Store the Call Disposition
    """
    ANSWER = 'ANSWER', u'ANSWER'
    BUSY = 'BUSY', u'BUSY'
    NOANSWER = 'NOANSWER', u'NOANSWER'
    CANCEL = 'CANCEL', u'CANCEL'
    CONGESTION = 'CONGESTION', u'CONGESTION'
    CHANUNAVAIL = 'CHANUNAVAIL', u'CHANUNAVAIL'
    DONTCALL = 'DONTCALL', u'DONTCALL'
    TORTURE = 'TORTURE', u'TORTURE'
    INVALIDARGS = 'INVALIDARGS', u'INVALIDARGS'
    NOROUTE = 'NOROUTE', u'NOROUTE'
    FORBIDDEN = 'FORBIDDEN', u'FORBIDDEN'
