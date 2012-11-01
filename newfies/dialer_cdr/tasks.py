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

from celery.utils.log import get_task_logger
from celery.decorators import task, periodic_task
from django.conf import settings
from django.core.cache import cache
from dialer_campaign.models import Campaign, Subscriber
from dialer_campaign.constants import SUBSCRIBER_STATUS
from dialer_cdr.models import Callrequest, VoIPCall
from dialer_cdr.constants import CALLREQUEST_STATUS
from dialer_gateway.utils import phonenumber_change_prefix
from datetime import datetime, timedelta
from time import sleep
from uuid import uuid1


logger = get_task_logger(__name__)


LOCK_EXPIRE = 60 * 1  # Lock expires in 1 minute


def single_instance_task(timeout):
    def task_exc(func):
        def wrapper(*args, **kwargs):
            lock_id = "celery-single-instance-" + func.__name__
            print lock_id
            acquire_lock = lambda: cache.add(lock_id, "true", timeout)
            release_lock = lambda: cache.delete(lock_id)
            if acquire_lock():
                try:
                    func(*args, **kwargs)
                finally:
                    release_lock()
        return wrapper
    return task_exc

"""
@periodic_task(run_every=timedelta(seconds=1))
@single_instance_task(LOCK_EXPIRE)
def callrequest_pending(*args, **kwargs):
    #A periodic task that checks for pending calls
    #**Usage**:
    #    callrequest_pending.delay()
    #
    logger.info("TASK :: callrequest_pending")

    #TODO: Django 1.4 select_for_update
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
    if obj_callrequest.user.userprofile.accountcode and \
        obj_callrequest.user.userprofile.accountcode > 0:
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
        res = dummy_testcall.delay(callerid=obj_callrequest.callerid,
                                    phone_number=dialout_phone_number,
                                    gateway=gateways)
        result = res.get()
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
        logger.error('Received RequestUUID :> ' + str(result['RequestUUID']))

    else:
        logger.error('No other method supported, use one of these options :'\
                     'dummy ; plivo')
        return False

    #Update Subscriber
    if obj_callrequest.subscriber \
        and obj_callrequest.subscriber.id:
        obj_subscriber = Subscriber.objects.get(
                    id=obj_callrequest.subscriber.id)
        if obj_subscriber.count_attempt == None \
            or not obj_subscriber.count_attempt >= 0:
            obj_subscriber.count_attempt = 1
        else:
            obj_subscriber.count_attempt = obj_subscriber.count_attempt + 1
        obj_subscriber.last_attempt = datetime.now()
        obj_subscriber.save()

    #Update CallRequest Object
    obj_callrequest.request_uuid = result['RequestUUID']
    obj_callrequest.save()

    #lock to limit running process, do so per campaign
    #http://ask.github.com/celery/cookbook/tasks.html

    return True


"""
The following tasks have been created for testing purpose.
Tasks :
    - dummy_testcall
    - dummy_test_answerurl
    - dummy_test_hangupurl
"""


@task()
def dummy_testcall(callerid, phone_number, gateway):
    """This is used for test purposes to simulate the behavior of Plivo

    **Attributes**:

        * ``callerid`` - CallerID
        * ``phone_number`` - Phone Number to call
        * ``gateway`` - Gateway to use for the call

    **Return**:

        * ``RequestUUID`` - A unique identifier for API request."""
    logger.info("TASK :: dummy_testcall")
    logger.debug("Executing task id %r, args: %r kwargs: %r" % \
                (dummy_testcall.request.id,
                 dummy_testcall.request.args,
                 dummy_testcall.request.kwargs))
    sleep(1)
    logger.info("Waiting 1 seconds...")

    request_uuid = uuid1()

    #Trigger AnswerURL
    dummy_test_answerurl.delay(request_uuid)
    #Trigger HangupURL
    dummy_test_hangupurl.delay(request_uuid)

    return {'RequestUUID': request_uuid}


@task(default_retry_delay=2)  # retry in 2 seconds.
def dummy_test_answerurl(request_uuid):
    """This task triggers a call to local answer
    This is used for test purposes to simulate the behavior of Plivo

    **Attributes**:

        * ``RequestUUID`` - A unique identifier for API request."""
    logger.info("TASK :: dummy_testcall")
    logger.debug("Executing task id %r, args: %r kwargs: %r" % \
                (dummy_test_answerurl.request.id,
                 dummy_test_answerurl.request.args,
                 dummy_test_answerurl.request.kwargs))

    logger.info("Waiting 1 seconds...")
    sleep(1)
    #find Callrequest
    try:
        obj_callrequest = Callrequest.objects.get(request_uuid=request_uuid)
    except:
        sleep(1)
        obj_callrequest = Callrequest.objects.get(request_uuid=request_uuid)

    #Update CallRequest
    obj_callrequest.status = 4  # SUCCESS
    obj_callrequest.save()
    #Create CDR
    new_voipcall = VoIPCall(user=obj_callrequest.user,
                            request_uuid=obj_callrequest.request_uuid,
                            callrequest=obj_callrequest,
                            callid='',
                            callerid=obj_callrequest.callerid,
                            phone_number=obj_callrequest.phone_number,
                            duration=0,
                            billsec=0,
                            disposition=1)
    new_voipcall.save()
    #lock to limit running process, do so per campaign
    #http://ask.github.com/celery/cookbook/tasks.html

    return True


@task(default_retry_delay=2)  # retry in 2 seconds.
def dummy_test_hangupurl(request_uuid):
    """
    This task triggers a call to local answer
    This is used for test purposes to simulate the behavior of Plivo

    **Attributes**:

        * ``RequestUUID`` - A unique identifier for API request.

    """
    logger.info("TASK :: dummy_test_hangupurl")
    logger.debug("Executing task id %r, args: %r kwargs: %r" % \
                (dummy_test_hangupurl.request.id,
                 dummy_test_hangupurl.request.args,
                 dummy_test_hangupurl.request.kwargs))
    logger.info("Waiting 10 seconds...")
    sleep(10)

    #find VoIPCall
    try:
        obj_voipcall = VoIPCall.objects.get(request_uuid=request_uuid)
    except:
        sleep(1)
        obj_voipcall = VoIPCall.objects.get(request_uuid=request_uuid)

    #Update VoIPCall
    obj_voipcall.status = 'ANSWER'
    obj_voipcall.duration = 55
    obj_voipcall.billsec = 55
    obj_voipcall.save()

    obj_callrequest = Callrequest.objects.get(request_uuid=request_uuid)
    obj_callrequest.hangup_cause = 'NORMAL_CLEARING'
    obj_callrequest.save()

    return True
