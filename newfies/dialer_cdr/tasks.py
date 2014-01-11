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

from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.conf import settings
from celery.utils.log import get_task_logger
from celery.decorators import task
from celery.task import PeriodicTask

from dialer_campaign.constants import SUBSCRIBER_STATUS, AMD_BEHAVIOR
from dialer_cdr.models import Callrequest
from dialer_cdr.constants import CALLREQUEST_STATUS, CALLREQUEST_TYPE
from dialer_cdr.utils import voipcall_save  # BufferVoIPCall

from appointment.models.users import CalendarUserProfile
from appointment.models.alarms import AlarmRequest
from appointment.constants import ALARMREQUEST_STATUS, ALARM_STATUS
from sms.models import Message
from sms.tasks import SendMessage
#from dialer_cdr.function_def import get_prefix_obj
from dialer_gateway.utils import prepare_phonenumber
from datetime import datetime, timedelta
from django.utils.timezone import utc
from common.only_one_task import only_one
from common_functions import debug_query
from uuid import uuid1
from time import sleep
try:
    import ESL as ESL
except ImportError:
    ESL = None


logger = get_task_logger(__name__)

LOCK_EXPIRE = 60 * 10 * 1  # Lock expires in 10 minutes


def dial_out(dial_command):
    if not ESL:
        logger.debug('ESL not installed')
        return 'load esl error'

    reload(ESL)
    c = ESL.ESLconnection(settings.ESL_HOSTNAME, settings.ESL_PORT, settings.ESL_SECRET)
    c.connected()
    ev = c.api("bgapi", str(dial_command))
    c.disconnect()
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
    return request_uuid


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
        #Increment subscriber.completion_count_attempt
        if callrequest.subscriber.completion_count_attempt:
            callrequest.subscriber.completion_count_attempt = callrequest.subscriber.completion_count_attempt + 1
        else:
            callrequest.subscriber.completion_count_attempt = 1
        callrequest.subscriber.save()

        #TODO: Add method in models.Callrequest to create copy
        # Init new callrequest -> delay at completion_intervalretry
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
            caller_name=callrequest.caller_name,
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


@task(ignore_result=True)
def update_callrequest(callrequest, opt_hangup_cause):
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


@task(ignore_result=True)
def process_callevent(record):
    """
    Process the callevent, this tasks will:
        - Retrieve the callrequest using either callrequest_id or request_uuid
        - create the voipcall, and save different data
    """
    #TODO: add method in utils parse_callevent
    app_type = 'campaign'
    event_name = record[1]
    body = record[2]
    job_uuid = record[3]
    call_uuid = record[4]
    #used_gateway_id = record[5]
    callrequest_id = record[6]
    alarm_request_id = record[7]
    callerid = record[8]
    phonenumber = record[9]
    duration = record[10]
    billsec = record[11]
    hangup_cause = record[12]
    hangup_cause_q850 = record[13]
    starting_date = record[14]
    amd_status = record[17]
    leg = record[18]

    if event_name == 'BACKGROUND_JOB':
        #hangup cause come from body
        hangup_cause = body[5:]

    if hangup_cause == '':
        hangup_cause = body[5:]

    request_uuid = job_uuid
    opt_hangup_cause = hangup_cause
    debug_query(22)

    try:
        if callrequest_id == 0:
            callrequest = Callrequest.objects \
                .select_related('aleg_gateway', 'subscriber', 'campaign') \
                .get(request_uuid=request_uuid.strip(' \t\n\r'))
        else:
            #mainly coming here
            callrequest = Callrequest.objects \
                .select_related('aleg_gateway', 'subscriber', 'campaign') \
                .get(id=callrequest_id)
    except:
        logger.error("Cannot find Callrequest job_uuid : %s" % job_uuid)
        return True

    logger.error(callrequest)
    if callrequest.alarm_request_id:
        app_type = 'alarm'
        alarm_req = AlarmRequest.objects.get(pk=callrequest.alarm_request_id)
        #Overwrite alarm_request_id as this is equal to 0 when call fails
        alarm_request_id = callrequest.alarm_request_id

    logger.debug("Find Callrequest id : %d" % callrequest.id)
    debug_query(23)

    if leg == 'aleg' and app_type == 'campaign':
        #Update callrequest
        #update_callrequest.delay(callrequest, opt_hangup_cause)
        #Disabled above tasks to reduce amount of tasks

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
        # ...

        callrequest.save()
        callrequest.subscriber.save()
        debug_query(24)
    elif leg == 'aleg' and app_type == 'alarm':
        if opt_hangup_cause == 'NORMAL_CLEARING':
            callrequest.status = CALLREQUEST_STATUS.SUCCESS
            alarm_req.status = ALARMREQUEST_STATUS.SUCCESS
            alarm_req.duration = duration
            alarm_req.alarm.status = ALARM_STATUS.SUCCESS
        else:
            callrequest.status = CALLREQUEST_STATUS.FAILURE
            alarm_req.status = ALARMREQUEST_STATUS.FAILURE
            alarm_req.alarm.status = ALARM_STATUS.FAILURE
        callrequest.hangup_cause = opt_hangup_cause

        callrequest.save()
        alarm_req.save()
        alarm_req.alarm.save()
        debug_query(24)

    if call_uuid == '':
        call_uuid = job_uuid
    if callerid == '':
        callerid = callrequest.callerid
    if phonenumber == '':
        phonenumber = callrequest.phone_number
    #Create those in Bulk - add in a buffer until reach certain number
    # buff_voipcall.save(
    #     obj_callrequest=callrequest,
    #     request_uuid=request_uuid,
    #     leg=leg,
    #     hangup_cause=opt_hangup_cause,
    #     hangup_cause_q850=hangup_cause_q850,
    #     callerid=callerid,
    #     phonenumber=phonenumber,
    #     starting_date=starting_date,
    #     call_uuid=call_uuid,
    #     duration=duration,
    #     billsec=billsec,
    #     amd_status=amd_status)

    # debug_query(25)

    voipcall_save(
        callrequest=callrequest,
        request_uuid=request_uuid,
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

    #If the call failed we will check if we want to make a retry call
    #Add condition to retry when it s machine and we want to reach a human
    if (app_type == 'campaign' and opt_hangup_cause != 'NORMAL_CLEARING' and callrequest.call_type == CALLREQUEST_TYPE.ALLOW_RETRY) or \
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

    elif app_type == 'campaign':
        #The Call is Answered and it's a campaign call
        logger.debug("Check for completion call")

        #Check if we should relaunch a new call to achieve completion
        check_retrycall_completion(callrequest)

    elif opt_hangup_cause != 'NORMAL_CLEARING' and app_type == 'alarm':
        #
        check_retry_alarm(alarm_request_id)


# OPTIMIZATION - TO REVIEW
def callevent_processing():
    """
    Retrieve callevents and process them

    call_event table is created by listener.lua

    CREATE TABLE if not exists call_event (
        id serial NOT NULL PRIMARY KEY,
        event_name varchar(200) NOT NULL,
        body varchar(200) NOT NULL,
        job_uuid varchar(200),
        call_uuid varchar(200) NOT NULL,
        used_gateway_id integer,
        callrequest_id integer,
        alarm_request_id integer,
        callerid varchar(200),
        phonenumber varchar(200),
        duration integer DEFAULT 0,
        billsec integer DEFAULT 0,
        hangup_cause varchar(40),
        hangup_cause_q850 varchar(10),
        amd_status varchar(40),
        starting_date timestamp with time zone,
        status smallint,
        leg smallint,
        created_date timestamp with time zone NOT NULL
        );
    CREATE INDEX call_event_idx_status ON call_event (status);
    --CREATE INDEX call_event_idx_date ON call_event (created_date);
    --CREATE INDEX call_event_idx_uuid ON call_event (call_uuid);
    """
    debug_query(20)

    cursor = connection.cursor()
    #TODO (Areski)
    #Replace this for ORM with select_for_update or transaction

    sql_statement = "SELECT id, event_name, body, job_uuid, call_uuid, used_gateway_id, " \
        "callrequest_id, alarm_request_id, callerid, phonenumber, duration, billsec, hangup_cause, " \
        "hangup_cause_q850, starting_date, status, created_date, amd_status, leg " \
        "FROM call_event WHERE status=1 LIMIT 1000 OFFSET 0"

    cursor.execute(sql_statement)
    row = cursor.fetchall()

    debug_query(21)
    # buff_voipcall = BufferVoIPCall()

    for record in row:
        call_event_id = record[0]
        event_name = record[1]
        #Update Call Event
        sql_statement = "UPDATE call_event SET status=2 WHERE id=%d" % call_event_id
        cursor.execute(sql_statement)

        logger.info("Processing Event : %s" % event_name)
        process_callevent.delay(record)

    debug_query(30)
    # buff_voipcall.commit()
    # debug_query(31)
    logger.debug('End Loop : callevent_processing')


class task_pending_callevent(PeriodicTask):
    """
    A periodic task that checks the call events

    **Usage**:

        callevent_processing.delay()
    """
    #The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    run_every = timedelta(seconds=15)

    #run_every = timedelta(seconds=15)

    #TODO: problem of the lock if it's a cloud, it won't be shared
    @only_one(ikey="task_pending_callevent", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.debug("ASK :: task_pending_callevent")
        callevent_processing()

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


@task(ignore_result=True)
def init_callrequest(callrequest_id, campaign_id, callmaxduration, ms_addtowait=0, alarm_request_id=None):
    """
    This task read the callrequest, update it as 'In Process'
    then proceed on the call outbound, using the different call engine supported

    **Attributes**:

        * ``callrequest_id`` - Callrequest ID
        * ``campaign_id`` - Campaign ID
        * ``callmaxduration`` - Max duration
        * ``ms_addtowait`` - Milliseconds to wait before outbounding the call

    """
    outbound_failure = False
    subscriber_id = None
    contact_id = None
    debug_query(8)

    if ms_addtowait > 0:
        sleep(ms_addtowait)

    #Survey Call or Alarm Call
    if campaign_id:
        #TODO: use only https://docs.djangoproject.com/en/dev/ref/models/querysets/#django.db.models.query.QuerySet.only
        obj_callrequest = Callrequest.objects.select_related('aleg_gateway', 'user__userprofile', 'subscriber', 'campaign').get(id=callrequest_id)
        subscriber_id = obj_callrequest.subscriber_id
        contact_id = obj_callrequest.subscriber.contact_id
    elif alarm_request_id:
        obj_callrequest = Callrequest.objects.select_related('aleg_gateway', 'user__userprofile').get(id=callrequest_id)
        alarm_request_id = obj_callrequest.alarm_request_id
    else:
        logger.info("TASK :: init_callrequest, wrong campaign_id & alarm_request_id")
        return False

    debug_query(9)
    logger.info("TASK :: init_callrequest - status:%s;cmpg:%s;alarm:%s" % (obj_callrequest.status, campaign_id, alarm_request_id))

    # TODO: move method prepare_phonenumber into the model gateway
    #obj_callrequest.aleg_gatewayprepare_phonenumber()
    dialout_phone_number = prepare_phonenumber(
        obj_callrequest.phone_number,
        obj_callrequest.aleg_gateway.addprefix,
        obj_callrequest.aleg_gateway.removeprefix,
        obj_callrequest.aleg_gateway.status)
    if not dialout_phone_number:
        logger.info("Error with dialout_phone_number - phone_number:%s" % (obj_callrequest.phone_number))
        return False
    else:
        logger.debug("dialout_phone_number : %s" % dialout_phone_number)

    debug_query(10)

    if settings.DIALERDEBUG:
        dialout_phone_number = settings.DIALERDEBUG_PHONENUMBER

    #Retrieve the Gateway for the A-Leg
    gateways = obj_callrequest.aleg_gateway.gateways
    gateway_id = obj_callrequest.aleg_gateway.id
    #gateway_codecs / gateway_retries
    gateway_timeouts = obj_callrequest.aleg_gateway.gateway_timeouts
    if not gateway_timeouts:
        gateway_timeouts = '60'
    originate_dial_string = obj_callrequest.aleg_gateway.originate_dial_string

    debug_query(11)

    #Sanitize gateways
    gateways = gateways.strip()
    if gateways[-1] != '/':
        gateways = gateways + '/'

    originate_dial_string = obj_callrequest.aleg_gateway.originate_dial_string
    if obj_callrequest.user.userprofile and obj_callrequest.user.userprofile.accountcode:
        originate_dial_string = originate_dial_string + ',accountcode=' + str(obj_callrequest.user.userprofile.accountcode)

    debug_query(12)

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
            args_list.append("origination_caller_id_name='%s'" % obj_callrequest.caller_name)

            #Add App Vars
            args_list.append("campaign_id=%s,subscriber_id=%s,alarm_request_id=%s,used_gateway_id=%s,callrequest_id=%s,contact_id=%s" %
                (campaign_id, subscriber_id, alarm_request_id, gateway_id, obj_callrequest.id, contact_id))
            args_list.append(originate_dial_string)

            #Call Vars
            callvars = "bridge_early_media=true,originate_timeout=%s,newfiesdialer=true,leg_type=1" % (gateway_timeouts, )
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
                args_list.append("execute_on_media_%d='sched_hangup +%d ORIGINATOR_CANCEL'" % (exec_on_media, hangup_on_ring))
                exec_on_media += 1

            #TODO: look and test http://wiki.freeswitch.org/wiki/Misc._Dialplan_Tools_queue_dtmf
            # Send digits
            if send_digits:
                if send_preanswer:
                    args_list.append("execute_on_media_%d='send_dtmf %s'"
                        % (exec_on_media, send_digits))
                    exec_on_media += 1
                else:
                    args_list.append("execute_on_answer='send_dtmf %s'" % send_digits)

            # Set time_limit
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
            if settings.DIALERDEBUG:
                dial_command = "originate {%s}user/areski '%s'" % (args_str, settings.ESL_SCRIPT)
            else:
                dial_command = "originate {%s}%s%s '%s'" % (args_str, gateways, dialout_phone_number, settings.ESL_SCRIPT)

            # originate {bridge_early_media=true,hangup_after_bridge=true,originate_timeout=10}user/areski &playback(/tmp/myfile.wav)
            # dial = "originate {bridge_early_media=true,hangup_after_bridge=true,originate_timeout=,newfiesdialer=true,used_gateway_id=1,callrequest_id=38,leg_type=1,origination_caller_id_number=234234234,origination_caller_id_name=234234,effective_caller_id_number=234234234,effective_caller_id_name=234234,}user//1000 '&lua(/usr/share/newfies-lua/newfies.lua)'"
            logger.warn('dial_command : %s' % dial_command)

            request_uuid = dial_out(dial_command)

            debug_query(14)

            if request_uuid and len(request_uuid) > 0 and request_uuid[:5] == 'error':
                outbound_failure = True
            debug_query(13)
        except:
            raise
            logger.error('error : ESL')
            outbound_failure = True
        logger.debug('Received RequestUUID :> %s' % request_uuid)
    else:
        logger.error('No other method supported!')
        obj_callrequest.status = CALLREQUEST_STATUS.FAILURE
        obj_callrequest.save()
        #ADD if alarm_request_id update AlarmRequest
        return False

    #Survey Call or Alarm Call
    if campaign_id:
        #Update Subscriber
        if not obj_callrequest.subscriber.count_attempt:
            obj_callrequest.subscriber.count_attempt = 1
        else:
            obj_callrequest.subscriber.count_attempt = obj_callrequest.subscriber.count_attempt + 1
        obj_callrequest.subscriber.last_attempt = datetime.utcnow().replace(tzinfo=utc)
        #check if the outbound call failed then update Subscriber
        if outbound_failure:
            obj_callrequest.subscriber.status = SUBSCRIBER_STATUS.FAIL
        obj_callrequest.subscriber.save()
    elif alarm_request_id:
        if outbound_failure:
            check_retry_alarm(alarm_request_id)

    #Update CallRequest Object
    obj_callrequest.request_uuid = request_uuid
    #check if the outbound call failed
    if outbound_failure:
        obj_callrequest.status = CALLREQUEST_STATUS.FAILURE
    else:
        obj_callrequest.status = CALLREQUEST_STATUS.CALLING
    obj_callrequest.save()

    debug_query(14)

    return True


def check_retry_alarm(alarm_request_id):
    obj_alarmreq = AlarmRequest.objects.get(id=alarm_request_id)
    if obj_alarmreq.alarm.maxretry >= obj_alarmreq.alarm.num_attempt:
        obj_alarmreq.update_status(ALARMREQUEST_STATUS.RETRY)
        obj_alarmreq.alarm.retry_alarm()
    else:
        obj_alarmreq.update_status(ALARMREQUEST_STATUS.FAILURE)
        #Check phonenumber_sms_failure
        if obj_alarmreq.alarm.phonenumber_sms_failure:

            # TODO: Use template SMS key (failure_reach) with this text as default
            failure_sms = "we haven't been able to reach '" \
                + str(obj_alarmreq.alarm.alarm_phonenumber) \
                + "' after trying " + str(obj_alarmreq.alarm.num_attempt) \
                + " times"

            sms_obj = Message.objects.create(
                content=failure_sms,
                recipient_number=obj_alarmreq.alarm.phonenumber_sms_failure,
                sender=obj_alarmreq.alarm.survey.user,
                content_type=ContentType.objects.get(model='alarmrequest'),
                object_id=obj_alarmreq.id,
            )
            try:
                calendar_user = obj_alarmreq.alarm.event.calendar.user
                calendar_setting = CalendarUserProfile.objects.get(user=calendar_user).calendar_setting
                SendMessage.delay(sms_obj.id, calendar_setting.sms_gateway_id)
            except:
                SendMessage.delay(sms_obj.id)

            print "Sent SMS Failure alarm : %s" % str(obj_alarmreq.alarm.alarm_phonenumber)
