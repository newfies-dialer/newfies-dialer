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

from django.utils.translation import ugettext_lazy as _
from common.utils import Choice


class CALLREQUEST_STATUS(Choice):
    """
    Store the Call Request Status
    """
    PENDING = 1, _("pending").capitalize()
    FAILURE = 2, _("failure").capitalize()
    RETRY = 3, _("retry").capitalize()
    SUCCESS = 4, _("success").capitalize()
    ABORT = 5, _("abort").capitalize()
    PAUSE = 6, _("pause").capitalize()
    CALLING = 7, _("calling").capitalize()


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
    FAILED = 'FAILED', _('FAILED')  # Added to catch all


class CDR_REPORT_COLUMN_NAME(Choice):
    """
    Column Name for the CDR Report
    """
    date = _('start date')
    call_id = _('call ID')
    leg = _('leg')
    caller_id = _('caller ID')
    phone_no = _('phone no')
    gateway = _('gateway')
    duration = _('duration')
    bill_sec = _('bill sec')
    disposition = _('disposition')
    amd_status = _('amd status')


class VOIPCALL_AMD_STATUS(Choice):
    """
    Store the AMD Status
    """
    PERSON = 1, _("person").capitalize()
    MACHINE = 2, _("machine").capitalize()
    UNSURE = 3, _("unsure").capitalize()
