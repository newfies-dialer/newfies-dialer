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

from django.utils.translation import ugettext_lazy as _
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
    ANSWER = 'ANSWER', _('ANSWER')
    BUSY = 'BUSY', _('BUSY')
    NOANSWER = 'NOANSWER', _('NOANSWER')
    CANCEL = 'CANCEL', _('CANCEL')
    CONGESTION = 'CONGESTION', _('CONGESTION')
    CHANUNAVAIL = 'CHANUNAVAIL', _('CHANUNAVAIL')
    DONTCALL = 'DONTCALL', _('DONTCALL')
    TORTURE = 'TORTURE', _('TORTURE')
    INVALIDARGS = 'INVALIDARGS', _('INVALIDARGS')
    NOROUTE = 'NOROUTE', _('NOROUTE')
    FORBIDDEN = 'FORBIDDEN', _('FORBIDDEN')


class CDR_REPORT_COLUMN_NAME(Choice):
    """
    Column Name for the CDR Report
    """
    date = _('Start date')
    call_id = _('Call ID')
    leg = _('Leg')
    caller_id = _('Caller ID')
    phone_no = _('Phone No')
    gateway = _('Gateway')
    duration = _('Duration')
    bill_sec = _('Bill Sec')
    disposition = _('Disposition')


class VOIPCALL_AMD_STATUS(Choice):
    """
    Store the AMD Status
    """
    PERSON = 1, _("Person")
    MACHINE = 2, _("Machine")
    UNSURE = 3, _("Unsure")
