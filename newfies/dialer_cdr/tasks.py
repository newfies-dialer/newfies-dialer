#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from celery.utils.log import get_task_logger
from django.db import connection
from celery.decorators import task
from celery.task import PeriodicTask
from django.conf import settings
from dialer_campaign.constants import SUBSCRIBER_STATUS, AMD_BEHAVIOR
from dialer_cdr.models import Callrequest, VoIPCall
from dialer_cdr.constants import CALLREQUEST_STATUS, CALLREQUEST_TYPE, \
    VOIPCALL_AMD_STATUS, LEG_TYPE
#from dialer_cdr.function_def import get_prefix_obj
from dialer_gateway.utils import prepare_phonenumber
from datetime import datetime, timedelta
from common.only_one_task import only_one
from uuid import uuid1
from common_functions import debug_query


logger = get_task_logger(__name__)

LOCK_EXPIRE = 60 * 10 * 1  # Lock expires in 10 minutes


def check_retrycall_completion(callrequest):
    """
    We will check if the callrequest need to be restarted
    in order to achieve completion
    """

    #Check if subscriber is not completed and check if
    #subscriber.completion_count_attempt < campaign.completion_maxretry
    if (callrequest.subscriber.status == SUBSCRIBER_STATUS.COMPLETED
       or callrequest.subscriber.completion_count_attempt >= callrequest.campaign.completion_maxretry
       or not callrequest.campaign.completion_maxretry
       or callrequest.campaign.completion_maxretry == 0):
        logger.debug("Subscriber completed or limit reached!")
    else:
        #Let's Init a new callrequest

        #Increment subscriber.completion_count_attempt
        if callrequest.subscriber.completion_count_attempt:
            callrequest.subscriber.completion_count_attempt = callrequest.subscriber.completion_count_attempt + 1
        else:
            callrequest.subscriber.completion_count_attempt = 1
        callrequest.subscriber.save()

        #init_callrequest -> delay at completion_intervalretry
        new_callrequest = Callrequest(
            request_uuid=uuid1(),
            parent_callrequest_id=callrequest.id,
            call_type=CALLREQUEST_TYPE.ALLOW_RETRY,
            num_attempt=callrequest.num_attempt + 1,
            user=callrequest.user,
            campaign_id=callrequest.campaign_id,
            aleg_gateway_id=callrequest.aleg_gateway_id,
            content_type=callrequest.content_type,
            object_id=callrequest.object_id,
            phone_number=callrequest.phone_number,
            timelimit=callrequest.timelimit,
            callerid=callrequest.callerid,
            timeout=callrequest.timeout,
            content_object=callrequest.content_object,
            subscriber=callrequest.subscriber
        )
        new_callrequest.save()
        #NOTE : implement a PID algorithm
        second_towait = callrequest.campaign.completion_intervalretry
        logger.debug("Init Completion Retry CallRequest in  %d seconds" % second_towait)
        init_callrequest.apply_async(
            args=[new_callrequest.id, callrequest.campaign.id, callrequest.campaign.callmaxduration],
            countdown=second_towait)


class BufferVoIPCall:

    list_voipcall = []

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


# OPTIMIZATION - TO REVIEW
def check_callevent():
    """
    Check callevent

    call_event table is created by listener.lua

    CREATE TABLE if not exists call_event (
        id serial NOT NULL PRIMARY KEY,
        event_name varchar(200) NOT NULL,
        body varchar(200) NOT NULL,
        job_uuid varchar(200),
        call_uuid varchar(200) NOT NULL,
        used_gateway_id integer,
        callrequest_id integer,
        callerid varchar(200),
        phonenumber varchar(200),
        duration integer DEFAULT 0,
        billsec integer DEFAULT 0,
        hangup_cause varchar(40),
        hangup_cause_q850 varchar(10),
        amd_status varchar(40),
        starting_date timestamp with time zone,
        status integer,
        created_date timestamp with time zone NOT NULL
        );
    CREATE INDEX call_event_idx_uuid ON call_event (call_uuid);
    CREATE INDEX call_event_idx_status ON call_event (status);
    CREATE INDEX call_event_idx_date ON call_event (created_date);

    """
    debug_query(20)

    cursor = connection.cursor()

    sql_statement = "SELECT id, event_name, body, job_uuid, call_uuid, used_gateway_id, "\
        "callrequest_id, callerid, phonenumber, duration, billsec, hangup_cause, "\
        "hangup_cause_q850, starting_date, status, created_date, amd_status, leg FROM call_event WHERE status=1 LIMIT 2000 OFFSET 0"

    cursor.execute(sql_statement)
    row = cursor.fetchall()

    debug_query(21)
    buff_voipcall = BufferVoIPCall()

    for record in row:
        call_event_id = record[0]
        event_name = record[1]
        body = record[2]
        job_uuid = record[3]
        call_uuid = record[4]
        #used_gateway_id = record[5]
        callrequest_id = record[6]
        callerid = record[7]
        phonenumber = record[8]
        duration = record[9]
        billsec = record[10]
        hangup_cause = record[11]
        hangup_cause_q850 = record[12]
        starting_date = record[13]
        amd_status = record[16]
        leg = record[17]

        #Update Call Event
        sql_statement = "UPDATE call_event SET status=2 WHERE id=%d" % call_event_id
        cursor.execute(sql_statement)
        logger.info("Processing Event : %s" % event_name)

        if event_name == 'BACKGROUND_JOB':
            #hangup cause come from body
            hangup_cause = body[5:]

        # if event_name == 'CHANNEL_HANGUP_COMPLETE':
        #     #hangup cause come from body
        #     print(event_name)

        if hangup_cause == '':
            hangup_cause = body[5:]

        opt_request_uuid = job_uuid
        opt_hangup_cause = hangup_cause

        debug_query(22)

        try:
            if callrequest_id == 0:
                callrequest = Callrequest.objects\
                    .select_related('aleg_gateway', 'subscriber', 'campaign')\
                    .get(request_uuid=opt_request_uuid.strip(' \t\n\r'))
            else:
                #mainly coming here
                callrequest = Callrequest.objects\
                    .select_related('aleg_gateway', 'subscriber', 'campaign')\
                    .get(id=callrequest_id)
        except:
            logger.error("Cannot find Callrequest job_uuid : %s" % job_uuid)
            continue

        logger.debug("Find Callrequest id : %d" % callrequest.id)
        debug_query(23)

        if leg == 'aleg':
            #Only the aleg will update the subscriber status / Bleg is only recorded
            #Update Callrequest Status
            if opt_hangup_cause == 'NORMAL_CLEARING':
                callrequest.status = CALLREQUEST_STATUS.SUCCESS
                if callrequest.subscriber.status != SUBSCRIBER_STATUS.COMPLETED:
                    callrequest.subscriber.status = SUBSCRIBER_STATUS.SENT
            else:
                callrequest.status = CALLREQUEST_STATUS.FAILURE
                callrequest.subscriber.status = SUBSCRIBER_STATUS.FAIL
            callrequest.hangup_cause = opt_hangup_cause

            callrequest.save()
            callrequest.subscriber.save()

        debug_query(24)

        if call_uuid == '':
            call_uuid = job_uuid
        if callerid == '':
            callerid = callrequest.callerid
        if phonenumber == '':
            phonenumber = callrequest.phone_number

        #TODO: Create those in Bulk - add in a buffer until reach certain number
        buff_voipcall.save(
            obj_callrequest=callrequest,
            request_uuid=opt_request_uuid,
            leg=leg,
            hangup_cause=opt_hangup_cause,
            hangup_cause_q850=hangup_cause_q850,
            callerid=callerid,
            phonenumber=phonenumber,
            starting_date=starting_date,
            call_uuid=call_uuid,
            duration=duration,
            billsec=billsec,
            amd_status=amd_status)

        debug_query(25)

        #If the call failed we will check if we want to make a retry call
        #Add condition to retry when it s machine and we want to reach a human
        if (opt_hangup_cause != 'NORMAL_CLEARING' and callrequest.call_type == CALLREQUEST_TYPE.ALLOW_RETRY) or \
           (amd_status == 'machine' and callrequest.campaign.voicemail
           and callrequest.campaign.amd_behavior == AMD_BEHAVIOR.HUMAN_ONLY):
            #Update to Retry Done
            callrequest.call_type = CALLREQUEST_TYPE.RETRY_DONE
            callrequest.save()

            debug_query(26)

            #check if we are allowed to retry on failure
            if ((callrequest.subscriber.count_attempt - 1) >= callrequest.campaign.maxretry
               or not callrequest.campaign.maxretry):
                logger.error("Not allowed retry - Maxretry (%d)" %
                             callrequest.campaign.maxretry)
                #Check here if we should try for completion
                check_retrycall_completion(callrequest)
                debug_query(28)
            else:
                #Allowed Retry
                logger.error("Allowed Retry - Maxretry (%d)" % callrequest.campaign.maxretry)

                # Create new callrequest, Assign parent_callrequest,
                # Change callrequest_type & num_attempt
                new_callrequest = Callrequest(
                    request_uuid=uuid1(),
                    parent_callrequest_id=callrequest.id,
                    call_type=CALLREQUEST_TYPE.ALLOW_RETRY,
                    num_attempt=callrequest.num_attempt + 1,
                    user=callrequest.user,
                    campaign_id=callrequest.campaign_id,
                    aleg_gateway_id=callrequest.aleg_gateway_id,
                    content_type=callrequest.content_type,
                    object_id=callrequest.object_id,
                    phone_number=callrequest.phone_number,
                    timelimit=callrequest.timelimit,
                    callerid=callrequest.callerid,
                    timeout=callrequest.timeout,
                    subscriber_id=callrequest.subscriber_id
                )
                new_callrequest.save()
                #NOTE : implement a PID algorithm
                second_towait = callrequest.campaign.intervalretry
                debug_query(29)

                logger.debug("Init Retry CallRequest in  %d seconds" % second_towait)
                init_callrequest.apply_async(
                    args=[new_callrequest.id, callrequest.campaign.id, callrequest.campaign.callmaxduration],
                    countdown=second_towait)
        else:
            #The Call is Answered
            logger.debug("Check for completion call")

            #Check if we should relaunch a new call to achieve completion
            check_retrycall_completion(callrequest)

    debug_query(30)

    buff_voipcall.commit()
    debug_query(31)

    logger.debug('End Loop : check_callevent')


class task_pending_callevent(PeriodicTask):
    """A periodic task that checks the call events

    **Usage**:

        check_callevent.delay()
    """
    run_every = timedelta(seconds=15)
    #The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    #run_every = timedelta(seconds=60)

    @only_one(ikey="task_pending_callevent", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.info("ASK :: task_pending_callevent")
        check_callevent()


"""
from celery.decorators import periodic_task
from datetime import timedelta

@periodic_task(run_every=timedelta(seconds=1))
@only_one(ikey="callrequest_pending", timeout=LOCK_EXPIRE)
def callrequest_pending(*args, **kwargs):
    #A periodic task that checks for pending calls
    #**Usage**:
    #    callrequest_pending.delay()
    #
    logger.info("TASK :: callrequest_pending")

    list_callrequest = Callrequest.objects\
                .get_pending_callrequest()[:settings.MAX_CALLS_PER_SECOND]
    logger.info("callrequest_pending - number_found=%d" % \
                len(list_callrequest))

    if not list_callrequest:
        logger.debug("No Pending Calls")

    for callrequest in list_callrequest:
        logger.info("=> CallRequest (id:%s, phone_number:%s)" %
                    (callrequest.id, callrequest.phone_number))

        callrequest.status = 7 # Update to Process
        callrequest.save()
        init_callrequest.delay(callrequest.id, callrequest.campaign.id, callrequest.campaign.callmaxduration)
"""


@task()
def init_callrequest(callrequest_id, campaign_id, callmaxduration):
    """
    This task read the callrequest, update it as 'In Process'
    then proceed on the call outbound, using the different call engine supported

    **Attributes**:

        * ``callrequest_id`` - Callrequest ID

    """
    debug_query(8)

    #Get CallRequest object
    # .only('id', 'callerid', 'phone_number', 'status',
    #     'request_uuid', 'campaign__id', 'subscriber__id',
    #     'aleg_gateway__id', 'aleg_gateway__addprefix', 'aleg_gateway__removeprefix', 'aleg_gateway__status',
    #     'aleg_gateway__gateways', 'aleg_gateway__gateway_timeouts', 'aleg_gateway__originate_dial_string',
    #     'user__userprofile__accountcode', 'campaign__caller_name',
    #     'subscriber__id', 'subscriber__contact__id', 'subscriber__count_attempt', 'subscriber__last_attempt')\
    obj_callrequest = Callrequest.objects.select_related('aleg_gateway', 'user__userprofile', 'subscriber', 'campaign').get(id=callrequest_id)

    debug_query(9)

    logger.info("TASK :: init_callrequest - status = %s" % str(obj_callrequest.status))

    debug_query(10)

    if obj_callrequest.aleg_gateway:
        dialout_phone_number = prepare_phonenumber(
            obj_callrequest.phone_number,
            obj_callrequest.aleg_gateway.addprefix,
            obj_callrequest.aleg_gateway.removeprefix,
            obj_callrequest.aleg_gateway.status)
    else:
        dialout_phone_number = obj_callrequest.phone_number
    logger.debug("dialout_phone_number : %s" % dialout_phone_number)

    debug_query(11)

    if settings.DIALERDEBUG:
        dialout_phone_number = settings.DIALERDEBUG_PHONENUMBER

    #Retrieve the Gateway for the A-Leg
    gateways = obj_callrequest.aleg_gateway.gateways
    gateway_id = obj_callrequest.aleg_gateway.id
    #gateway_codecs = obj_callrequest.aleg_gateway.gateway_codecs
    #gateway_retries = obj_callrequest.aleg_gateway.gateway_retries
    gateway_timeouts = obj_callrequest.aleg_gateway.gateway_timeouts
    originate_dial_string = obj_callrequest.aleg_gateway.originate_dial_string

    debug_query(12)

    #Sanitize gateways
    gateways = gateways.strip()
    if gateways[-1] != '/':
        gateways = gateways + '/'

    originate_dial_string = obj_callrequest.aleg_gateway.originate_dial_string
    if (obj_callrequest.user.userprofile.accountcode and
       obj_callrequest.user.userprofile.accountcode > 0):
        originate_dial_string = originate_dial_string + \
            ',accountcode=' + str(obj_callrequest.user.userprofile.accountcode)

    debug_query(13)

    outbound_failure = False

    #Send Call to API
    #http://ask.github.com/celery/userguide/remote-tasks.html

    """
    #this could be needed if we want to call a different API / Twilio
    import httplib, urllib
    params = urllib.urlencode({'From': '900900000', 'To': '1000',})
    headers = {"Content-type": "application/x-www-form-urlencoded",
           "Accept": "text/plain"}
    conn = httplib.HTTPConnection("127.0.0.1:8000")
    conn.request("POST", "/api/dialer_cdr/testcall/", params, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = response.read()
    conn.close()
    """

    if settings.NEWFIES_DIALER_ENGINE.lower() == 'esl':
        try:
            args_list = []
            send_digits = False
            time_limit = callmaxduration

            # To wait before sending DTMF to the extension, you can add leading 'w'
            # characters.
            # Each 'w' character waits 0.5 seconds instead of sending a digit.
            # Each 'W' character waits 1.0 seconds instead of sending a digit.
            # You can also add the tone duration in ms by appending @[duration] after string.
            # Eg. 1w2w3@1000
            check_senddigit = dialout_phone_number.partition('w')
            if check_senddigit[1] == 'w':
                send_digits = check_senddigit[1] + check_senddigit[2]
                dialout_phone_number = check_senddigit[0]

            args_list.append("origination_caller_id_number=%s" % obj_callrequest.callerid)
            if obj_callrequest.campaign.caller_name:
                args_list.append("origination_caller_id_name='%s'" % obj_callrequest.campaign.caller_name)

            #Add App Vars
            args_list.append("campaign_id=%d,subscriber_id=%d,used_gateway_id=%s,callrequest_id=%s,contact_id=%s" %
                (obj_callrequest.campaign_id, obj_callrequest.subscriber_id, gateway_id, obj_callrequest.id, obj_callrequest.subscriber.contact_id))

            args_list.append(originate_dial_string)

            #Call Vars
            callvars = "bridge_early_media=true,originate_timeout=%s,newfiesdialer=true,leg_type=1" % \
                (gateway_timeouts, )

            args_list.append(callvars)

            #Default Test
            hangup_on_ring = ''
            send_preanswer = False

            # set hangup_on_ring
            try:
                hangup_on_ring = int(hangup_on_ring)
            except ValueError:
                hangup_on_ring = -1
            exec_on_media = 1
            if hangup_on_ring >= 0:
                args_list.append("execute_on_media_%d='sched_hangup +%d ORIGINATOR_CANCEL'"
                    % (exec_on_media, hangup_on_ring))
                exec_on_media += 1

            # Send digits
            if send_digits:
                if send_preanswer:
                    args_list.append("execute_on_media_%d='send_dtmf %s'"
                        % (exec_on_media, send_digits))
                    exec_on_media += 1
                else:
                    args_list.append("execute_on_answer='send_dtmf %s'" % send_digits)

            # set time_limit
            try:
                time_limit = int(time_limit)
            except ValueError:
                time_limit = -1
            #TODO : Fix time_limit - maybe implement this into Lua
            # if time_limit > 0:
            #     # create sched_hangup_id
            #     sched_hangup_id = str(uuid1())
            #     # create a new request uuid
            #     request_uuid = str(uuid1())
            #     args_list.append("api_on_answer_1='sched_api +%d %s hupall ALLOTTED_TIMEOUT'"
            #         % (time_limit, sched_hangup_id))

            # build originate string
            args_str = ','.join(args_list)

            #DEBUG
            #settings.ESL_SCRIPT = '&playback(/usr/local/freeswitch/sounds/en/us/callie/voicemail/8000/vm-record_greeting.wav)'
            dial = "originate {%s}%s%s '%s'" % \
                (args_str, gateways, dialout_phone_number, settings.ESL_SCRIPT)
            # originate {bridge_early_media=true,hangup_after_bridge=true,originate_timeout=10}user/areski &playback(/tmp/myfile.wav)
            # dial = "originate {bridge_early_media=true,hangup_after_bridge=true,originate_timeout=,newfiesdialer=true,used_gateway_id=1,callrequest_id=38,leg_type=1,origination_caller_id_number=234234234,origination_caller_id_name=234234,effective_caller_id_number=234234234,effective_caller_id_name=234234,}user//1000 '&lua(/usr/share/newfies-lua/newfies.lua)'"
            print dial

            import ESL
            c = ESL.ESLconnection(settings.ESL_HOSTNAME, settings.ESL_PORT, settings.ESL_SECRET)
            c.connected()
            ev = c.api("bgapi", str(dial))
            c.disconnect()

            debug_query(14)

            if ev:
                result = ev.serialize()
                logger.debug(result)
                pos = result.find('Job-UUID:')
                if pos:
                    request_uuid = result[pos + 10:pos + 46]
                else:
                    request_uuid = 'error'
            else:
                request_uuid = 'error'

        except:
            raise
            logger.error('error : ESL')
            outbound_failure = True
            return False
        logger.info('Received RequestUUID :> ' + request_uuid)
    else:
        logger.error('No other method supported!')
        obj_callrequest.status = CALLREQUEST_STATUS.FAILURE
        obj_callrequest.save()
        return False

    #Update Subscriber
    if not obj_callrequest.subscriber.count_attempt:
        obj_callrequest.subscriber.count_attempt = 1
    else:
        obj_callrequest.subscriber.count_attempt = obj_callrequest.subscriber.count_attempt + 1
    obj_callrequest.subscriber.last_attempt = datetime.now()
    #check if the outbound call failed then update Subscriber
    if outbound_failure:
        obj_callrequest.subscriber.status = SUBSCRIBER_STATUS.FAIL
    obj_callrequest.subscriber.save()

    #Update CallRequest Object
    obj_callrequest.request_uuid = request_uuid
    #check if the outbound call failed
    if outbound_failure:
        obj_callrequest.status = CALLREQUEST_STATUS.FAILURE
    else:
        obj_callrequest.status = CALLREQUEST_STATUS.CALLING
    obj_callrequest.save()

    #lock to limit running process, do so per campaign
    #http://ask.github.com/celery/cookbook/tasks.html

    debug_query(15)

    return True
