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

from dialer_cdr.models import VoIPCall
from dialer_cdr.constants import VOIPCALL_AMD_STATUS, LEG_TYPE
from celery.utils.log import get_task_logger
#from dialer_cdr.function_def import get_prefix_obj

logger = get_task_logger(__name__)


class BufferVoIPCall:
    """
    BufferVoIPCall stores VoIPCall (CDR) into a buffer and allow
    to save CDRs per bulk.
    - save : store the CDRs in memory
    - commit : trigger the bulk_create method to save the CDRs
    """

    def __init__(self):
        self.list_voipcall = []

    def save(self, obj_callrequest, request_uuid, leg='aleg', hangup_cause='',
             hangup_cause_q850='', callerid='',
             phonenumber='', starting_date='',
             call_uuid='', duration=0, billsec=0, amd_status='person'):
        """
        Save voip call into buffer
        """
        if leg == 'aleg':
            #A-Leg
            leg_type = LEG_TYPE.A_LEG
            used_gateway = obj_callrequest.aleg_gateway
        else:
            #B-Leg
            leg_type = LEG_TYPE.B_LEG
            used_gateway = obj_callrequest.aleg_gateway
            #This code is useful if we want to let the survey editor select the gateway
            # if obj_callrequest.content_object.__class__.__name__ == 'Survey':
            #     #Get the gateway from the App
            #     used_gateway = obj_callrequest.content_object.gateway
            # else:
            #     #Survey
            #     used_gateway = obj_callrequest.aleg_gateway
        if amd_status == 'machine':
            amd_status_id = VOIPCALL_AMD_STATUS.MACHINE
        else:
            amd_status_id = VOIPCALL_AMD_STATUS.PERSON

        logger.debug('Create CDR - request_uuid=%s;leg=%d;hangup_cause=%s;billsec=%s;amd_status=%s' %
            (request_uuid, leg_type, hangup_cause, str(billsec), amd_status))

        #Get the first word only
        hangup_cause = hangup_cause.split()[0]

        if hangup_cause == 'NORMAL_CLEARING' or hangup_cause == 'ALLOTTED_TIMEOUT':
            hangup_cause = 'ANSWER'

        if hangup_cause == 'ANSWER':
            disposition = 'ANSWER'
        elif hangup_cause == 'USER_BUSY':
            disposition = 'BUSY'
        elif hangup_cause == 'NO_ANSWER':
            disposition = 'NOANSWER'
        elif hangup_cause == 'ORIGINATOR_CANCEL':
            disposition = 'CANCEL'
        elif hangup_cause == 'NORMAL_CIRCUIT_CONGESTION':
            disposition = 'CONGESTION'
        else:
            disposition = 'FAILED'

        #Note: Removed for test performance
        #Note: Look at prefix PG module : https://github.com/dimitri/prefix
        #prefix_obj = get_prefix_obj(phonenumber)

        #Save this for bulk saving
        self.list_voipcall.append(
            VoIPCall(
                user_id=obj_callrequest.user_id,
                request_uuid=request_uuid,
                leg_type=leg_type,
                used_gateway=used_gateway,
                callrequest_id=obj_callrequest.id,
                callid=call_uuid,
                callerid=callerid,
                phone_number=phonenumber,
                #dialcode=prefix_obj,
                starting_date=starting_date,
                duration=duration,
                billsec=billsec,
                disposition=disposition,
                hangup_cause=hangup_cause,
                hangup_cause_q850=hangup_cause_q850,
                amd_status=amd_status_id)
        )

    def commit(self):
        """
        function to create CDR / VoIP Call
        """
        VoIPCall.objects.bulk_create(self.list_voipcall)


def voipcall_save(callrequest, request_uuid, leg='aleg', hangup_cause='',
                  hangup_cause_q850='', callerid='', phonenumber='', starting_date='',
                  call_uuid='', duration=0, billsec=0, amd_status='person'):
    """
    This task will save the voipcall(CDR) to the DB,
    it will also reformat the disposition
    """
    #TODO: following code is duplicated, see above

    used_gateway = callrequest.aleg_gateway
    #Set Leg Type
    if leg == 'aleg':
        leg_type = LEG_TYPE.A_LEG
    else:
        leg_type = LEG_TYPE.B_LEG
    #Set AMD status
    if amd_status == 'machine':
        amd_status_id = VOIPCALL_AMD_STATUS.MACHINE
    else:
        amd_status_id = VOIPCALL_AMD_STATUS.PERSON

    logger.debug('Create CDR - request_uuid=%s;leg=%d;hangup_cause=%s;billsec=%s;amd_status=%s' %
        (request_uuid, leg_type, hangup_cause, str(billsec), amd_status))

    #Get the first word only
    hangup_cause = hangup_cause.split()[0]

    if hangup_cause == 'NORMAL_CLEARING' or hangup_cause == 'ALLOTTED_TIMEOUT':
        disposition = 'ANSWER'
    elif hangup_cause == 'USER_BUSY':
        disposition = 'BUSY'
    elif hangup_cause == 'NO_ANSWER':
        disposition = 'NOANSWER'
    elif hangup_cause == 'ORIGINATOR_CANCEL':
        disposition = 'CANCEL'
    elif hangup_cause == 'NORMAL_CIRCUIT_CONGESTION':
        disposition = 'CONGESTION'
    else:
        disposition = 'FAILED'

    #Note: Removed for test performance
    #Note: Look at prefix PG module : https://github.com/dimitri/prefix
    #prefix_obj = get_prefix_obj(phonenumber)

    #Save the VoIPCall
    new_voipcall = VoIPCall(
        user_id=callrequest.user_id,
        request_uuid=request_uuid,
        leg_type=leg_type,
        used_gateway=used_gateway,
        callrequest_id=callrequest.id,
        callid=call_uuid,
        callerid=callerid,
        phone_number=phonenumber,
        #dialcode=prefix_obj,
        starting_date=starting_date,
        duration=duration,
        billsec=billsec,
        disposition=disposition,
        hangup_cause=hangup_cause,
        hangup_cause_q850=hangup_cause_q850,
        amd_status=amd_status_id)
    new_voipcall.save()
