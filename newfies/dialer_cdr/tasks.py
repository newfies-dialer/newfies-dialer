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
from dialer_campaign.models import Campaign, Subscriber
from dialer_campaign.constants import SUBSCRIBER_STATUS, AMD_BEHAVIOR
from dialer_cdr.models import Callrequest, VoIPCall
from dialer_cdr.constants import CALLREQUEST_STATUS, CALLREQUEST_TYPE, \
    VOIPCALL_AMD_STATUS
from dialer_cdr.function_def import get_prefix_obj
from dialer_gateway.utils import phonenumber_change_prefix
from dialer_campaign.function_def import user_dialer_setting
from datetime import datetime, timedelta
from common.only_one_task import only_one
from uuid import uuid1


logger = get_task_logger(__name__)

LOCK_EXPIRE = 60 * 10 * 1  # Lock expires in 10 minutes


def check_retrycall_completion(obj_subscriber, callrequest):
    """
    We will check if the callrequest need to be restarted
    in order to achieve completion
    """

    #Check if subscriber is not completed and check if
    #subscriber.completion_count_attempt < campaign.completion_maxretry
    if (obj_subscriber.status == SUBSCRIBER_STATUS.COMPLETED
       or obj_subscriber.completion_count_attempt >= callrequest.campaign.completion_maxretry
       or not callrequest.campaign.completion_maxretry
       or callrequest.campaign.completion_maxretry == 0):
        logger.info("Subscriber completed or limit reached!")
    else:
        #Let's Init a new callrequest

        #Increment subscriber.completion_count_attempt
        if obj_subscriber.completion_count_attempt:
            obj_subscriber.completion_count_attempt = obj_subscriber.completion_count_attempt + 1
        else:
            obj_subscriber.completion_count_attempt = 1
        obj_subscriber.save()

        #init_callrequest -> delay at completion_intervalretry
        new_callrequest = Callrequest(
            request_uuid=uuid1(),
            parent_callrequest_id=callrequest.id,
            call_type=1,
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
        logger.info("Init Completion Retry CallRequest in  %d seconds" % second_towait)
        init_callrequest.apply_async(
            args=[new_callrequest.id, callrequest.campaign.id],
            countdown=second_towait)


def create_voipcall_esl(obj_callrequest, request_uuid, leg='a', hangup_cause='',
                        hangup_cause_q850='', callerid='',
                        phonenumber='', starting_date='',
                        call_uuid='', duration=0, billsec=0, amd_status='person'):
    """
    Common function to create CDR / VoIP Call

    **Attributes**:

        * data : list with call details data
        * obj_callrequest:  refer to the CallRequest object
        * request_uuid : cdr uuid

    """
    if leg == 'a':
        #A-Leg
        leg_type = 1
        used_gateway = obj_callrequest.aleg_gateway
    else:
        #B-Leg
        leg_type = 2
        if obj_callrequest.content_object.__class__.__name__ == 'VoiceApp':
            used_gateway = obj_callrequest.content_object.gateway
        else:
            #Survey
            used_gateway = obj_callrequest.aleg_gateway
    if amd_status == 'machine':
        amd_status_id = VOIPCALL_AMD_STATUS.MACHINE
    else:
        amd_status_id = VOIPCALL_AMD_STATUS.PERSON

    logger.info('Create CDR - request_uuid=%s;leg=%d;hangup_cause=%s;billsec=%s;amd_status=%s' %
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

    prefix_obj = get_prefix_obj(phonenumber)

    new_voipcall = VoIPCall(
        user=obj_callrequest.user,
        request_uuid=request_uuid,
        leg_type=leg_type,
        used_gateway=used_gateway,
        callrequest=obj_callrequest,
        callid=call_uuid,
        callerid=callerid,
        phone_number=phonenumber,
        dialcode=prefix_obj,
        starting_date=starting_date,
        duration=duration,
        billsec=billsec,
        disposition=disposition,
        hangup_cause=hangup_cause,
        hangup_cause_q850=hangup_cause_q850,
        amd_status=amd_status_id)
    #Save CDR
    new_voipcall.save()


def check_callevent():
    """
    Check callevent
    """
    cursor = connection.cursor()

    sql_statement = "SELECT id, event_name, body, job_uuid, call_uuid, used_gateway_id, "\
        "callrequest_id, callerid, phonenumber, duration, billsec, hangup_cause, "\
        "hangup_cause_q850, starting_date, status, created_date, amd_status FROM call_event WHERE status=1 LIMIT 1000 OFFSET 0"

    cursor.execute(sql_statement)
    row = cursor.fetchall()

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
        try:
            if callrequest_id == 0:
                callrequest = Callrequest.objects.get(request_uuid=opt_request_uuid.strip(' \t\n\r'))
            else:
                callrequest = Callrequest.objects.get(id=callrequest_id)
        except:
            logger.error("Cannot find Callrequest job_uuid : %s" % job_uuid)
            continue

        logger.info("Find Callrequest id : %d" % callrequest.id)

        try:
            obj_subscriber = Subscriber.objects.get(id=callrequest.subscriber.id)
            if opt_hangup_cause == 'NORMAL_CLEARING':
                if obj_subscriber.status != SUBSCRIBER_STATUS.COMPLETED:
                    obj_subscriber.status = SUBSCRIBER_STATUS.SENT
            else:
                obj_subscriber.status = SUBSCRIBER_STATUS.FAIL
            obj_subscriber.save()
        except:
            logger.debug('Error cannot find the Subscriber!')
            return False

        #Update Callrequest Status
        if opt_hangup_cause == 'NORMAL_CLEARING':
            callrequest.status = CALLREQUEST_STATUS.SUCCESS
        else:
            callrequest.status = CALLREQUEST_STATUS.FAILURE
        callrequest.hangup_cause = opt_hangup_cause
        callrequest.save()

        if call_uuid == '':
            call_uuid = job_uuid
        if callerid == '':
            callerid = callrequest.callerid
        if phonenumber == '':
            phonenumber = callrequest.phone_number

        create_voipcall_esl(obj_callrequest=callrequest,
            request_uuid=opt_request_uuid,
            leg='a',
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
        if (opt_hangup_cause != 'NORMAL_CLEARING'
           and callrequest.call_type == CALLREQUEST_TYPE.ALLOW_RETRY) or \
           (amd_status == 'machine' and callrequest.campaign.voicemail
           and callrequest.campaign.amd_behavior == AMD_BEHAVIOR.HUMAN_ONLY):
            #Update to Retry Done
            callrequest.call_type = CALLREQUEST_TYPE.RETRY_DONE
            callrequest.save()

            dialer_set = user_dialer_setting(callrequest.user)
            #check if we are allowed to retry on failure
            if ((obj_subscriber.count_attempt - 1) >= callrequest.campaign.maxretry
               or (obj_subscriber.count_attempt - 1) >= dialer_set.maxretry
               or not callrequest.campaign.maxretry):
                logger.error("Not allowed retry - Maxretry (%d)" %
                             callrequest.campaign.maxretry)
                #Check here if we should try for completion
                check_retrycall_completion(obj_subscriber, callrequest)
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
                    content_object=callrequest.content_object,
                    subscriber=callrequest.subscriber
                )
                new_callrequest.save()
                #NOTE : implement a PID algorithm
                second_towait = callrequest.campaign.intervalretry
                logger.info("Init Retry CallRequest in  %d seconds" % second_towait)
                init_callrequest.apply_async(
                    args=[new_callrequest.id, callrequest.campaign.id],
                    countdown=second_towait)
        else:
            #The Call is Answered
            logger.info("Check for completion call")

            #Check if we should relaunch a new call to achieve completion
            check_retrycall_completion(obj_subscriber, callrequest)

    logger.debug('End Loop : check_callevent')


class task_pending_callevent(PeriodicTask):
    """A periodic task that checks the call events

    **Usage**:

        check_callevent.delay()
    """
    run_every = timedelta(seconds=10)
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
        init_callrequest.delay(callrequest.id, callrequest.campaign.id)
"""


@task()
def init_callrequest(callrequest_id, campaign_id):
    """This task outbounds the call

    **Attributes**:

        * ``callrequest_id`` - Callrequest ID
    """
    #Update callrequest to Process
    obj_callrequest = Callrequest.objects.get(id=callrequest_id)
    obj_callrequest.status = CALLREQUEST_STATUS.PROCESS
    obj_callrequest.save()
    logger.info("TASK :: init_callrequest - status = %s" %
        str(obj_callrequest.status))
    try:
        obj_campaign = Campaign.objects.get(id=campaign_id)
    except:
        logger.error("Can't find the campaign : %s" % campaign_id)
        return False

    if obj_callrequest.aleg_gateway:
        id_aleg_gateway = obj_callrequest.aleg_gateway.id
        dialout_phone_number = phonenumber_change_prefix(
            obj_callrequest.phone_number,
            id_aleg_gateway)
    else:
        dialout_phone_number = obj_callrequest.phone_number
    logger.info("dialout_phone_number : %s" % dialout_phone_number)

    if settings.DIALERDEBUG:
        dialout_phone_number = settings.DIALERDEBUG_PHONENUMBER

    #Retrieve the Gateway for the A-Leg
    gateways = obj_callrequest.aleg_gateway.gateways
    gateway_id = obj_callrequest.aleg_gateway.id
    gateway_codecs = obj_callrequest.aleg_gateway.gateway_codecs
    gateway_timeouts = obj_callrequest.aleg_gateway.gateway_timeouts
    gateway_retries = obj_callrequest.aleg_gateway.gateway_retries
    originate_dial_string = obj_callrequest.aleg_gateway.originate_dial_string
    callmaxduration = obj_campaign.callmaxduration

    #Sanitize gateways
    gateways = gateways.strip()
    if gateways[-1] != '/':
        gateways = gateways + '/'

    if obj_campaign.content_type.app_label == 'survey':
        #Use Survey Statemachine
        answer_url = settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL
    else:
        answer_url = settings.PLIVO_DEFAULT_ANSWER_URL

    originate_dial_string = obj_callrequest.aleg_gateway.originate_dial_string
    if (obj_callrequest.user.userprofile.accountcode and
       obj_callrequest.user.userprofile.accountcode > 0):
        originate_dial_string = originate_dial_string + \
            ',accountcode=' + str(obj_callrequest.user.userprofile.accountcode)

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
    if settings.NEWFIES_DIALER_ENGINE.lower() == 'dummy':
        #Use Dummy TestCall
        # res = dummy_testcall.delay(callerid=obj_callrequest.callerid,
        #     phone_number=dialout_phone_number,
        #     gateway=gateways)
        # result = res.get()
        result = ''
        logger.info(result)
        logger.error('Received RequestUUID :> ' + str(result['RequestUUID']))

    elif settings.NEWFIES_DIALER_ENGINE.lower() == 'plivo':
        try:
            #Request Call via Plivo
            from telefonyhelper import call_plivo
            result = call_plivo(
                callerid=obj_callrequest.callerid,
                callername=obj_callrequest.campaign.caller_name,
                phone_number=dialout_phone_number,
                Gateways=gateways,
                GatewayCodecs=gateway_codecs,
                GatewayTimeouts=gateway_timeouts,
                GatewayRetries=gateway_retries,
                ExtraDialString=originate_dial_string,
                AnswerUrl=answer_url,
                HangupUrl=settings.PLIVO_DEFAULT_HANGUP_URL,
                TimeLimit=str(callmaxduration))
        except:
            logger.error('error : call_plivo')
            obj_callrequest.status = 2  # Update to Failure
            obj_callrequest.save()
            if obj_callrequest.subscriber and obj_callrequest.subscriber.id:
                obj_subscriber = Subscriber.objects\
                    .get(id=obj_callrequest.subscriber.id)
                obj_subscriber.status = SUBSCRIBER_STATUS.FAIL
                obj_subscriber.save()
            return False
        logger.info(result)
        request_uuid = str(result['RequestUUID'])
        logger.info('Received RequestUUID :> ' + request_uuid)

    elif settings.NEWFIES_DIALER_ENGINE.lower() == 'esl':
        try:
            args_list = []
            send_digits = False
            time_limit = obj_callrequest.campaign.callmaxduration

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
            args_list.append("campaign_id=%d,subscriber_id=%d,used_gateway_id=%s,callrequest_id=%s" %
                (obj_callrequest.campaign_id, obj_callrequest.subscriber_id, gateway_id, obj_callrequest.id))

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
            obj_callrequest.status = 2  # Update to Failure
            obj_callrequest.save()
            if obj_callrequest.subscriber and obj_callrequest.subscriber.id:
                obj_subscriber = Subscriber.objects\
                    .get(id=obj_callrequest.subscriber.id)
                obj_subscriber.status = SUBSCRIBER_STATUS.FAIL
                obj_subscriber.save()
            return False
        logger.info('Received RequestUUID :> ' + request_uuid)
    else:
        logger.error('No other method supported!')
        return False

    #Update Subscriber
    if obj_callrequest.subscriber and obj_callrequest.subscriber.id:
        obj_subscriber = Subscriber.objects.get(id=obj_callrequest.subscriber.id)
        if not obj_subscriber.count_attempt:
            obj_subscriber.count_attempt = 1
        else:
            obj_subscriber.count_attempt = obj_subscriber.count_attempt + 1
        obj_subscriber.last_attempt = datetime.now()
        obj_subscriber.save()

    #Update CallRequest Object
    obj_callrequest.request_uuid = request_uuid
    obj_callrequest.save()

    #lock to limit running process, do so per campaign
    #http://ask.github.com/celery/cookbook/tasks.html

    return True
