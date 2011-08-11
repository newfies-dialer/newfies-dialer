from celery.task import Task, PeriodicTask
from dialer_campaign.models import Campaign
from dialer_campaign.function_def import user_dialer_setting
from dialer_cdr.models import Callrequest, VoIPCall
from celery.decorators import task
from datetime import datetime, timedelta
from time import sleep
from uuid import uuid1
from django.conf import settings
from dialer_gateway.utils import phonenumber_change_prefix


class callrequest_pending(PeriodicTask):
    """A periodic task that checks for pending calls

    **Usage**:

        callrequest_pending.delay()
    """
    # 1000000 ms = 1 sec
    run_every = timedelta(microseconds=10000000)

    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info("TASK :: callrequest_pending")

        list_callrequest = Callrequest.objects.get_pending_callrequest()[:20]
        if not list_callrequest:
            logger.debug("No Pending Calls")

        for callrequest in list_callrequest:
            logger.error("=> CallRequest (id:%s, phone_number:%s)" %
                        (callrequest.id, callrequest.phone_number))

            callrequest.status = 7 # Update to Process
            callrequest.save()
            init_callrequest.delay(callrequest.id, callrequest.campaign.id)


@task()
def init_callrequest(callrequest_id, campaign_id):
    """This task outbounds the call

    **Attributes**:

        * ``callrequest_id`` - Callrequest ID
    """
    logger = init_callrequest.get_logger()
    obj_callrequest = Callrequest.objects.get(id=callrequest_id)
    logger.info("TASK :: init_callrequest - status = %s" %
                                        str(obj_callrequest.status))

    try:
        obj_campaign = Campaign.objects.get(id=campaign_id)
    except:
        logger.error("Can't find the campaign : %s" % campaign_id)
        return False
    
    phone_number = obj_callrequest.phone_number
    if obj_callrequest.aleg_gateway:
        id_aleg_gateway = obj_callrequest.aleg_gateway.id
        dialout_phone_number = phonenumber_change_prefix(phone_number,
                                         id_aleg_gateway)
    else:
        dialout_phone_number = phone_number
    logger.info("dialout_phone_number : %s" % dialout_phone_number)

    #Construct the dialing out path
    """
    **Gateway Attributes**:

        * ``name`` - Gateway name.
        * ``description`` - Description about Gateway.
        * ``addprefix`` - Add prefix.
        * ``removeprefix`` - Remove prefix.
        * ``gateways`` - "user/,user", # Gateway string to try dialing \
        separated by comma. First in list will be tried first
        * ``gateway_codecs`` - "'PCMA,PCMU','PCMA,PCMU'", \
        # Codec string as needed by FS for each gateway separated by comma
        * ``gateway_timeouts`` - "10,10", # Seconds to timeout in string for\
        each gateway separated by comma
        * ``gateway_retries`` - "2,1", # Retry String for Gateways separated\
        by a comma, on how many times each gateway should be retried
        * ``originate_dial_string`` - originate_dial_string
        * ``secondused`` -
        * ``failover`` -
        * ``addparameter`` -
        * ``count_call`` -
        * ``count_in_use`` -
        * ``maximum_call`` -
        * ``status`` - Gateway status
    """

    #Retrieve the Gateway for the A-Leg
    gateways = obj_callrequest.aleg_gateway.gateways
    gateway_codecs = obj_callrequest.aleg_gateway.gateway_codecs
    gateway_timeouts = obj_callrequest.aleg_gateway.gateway_timeouts
    gateway_retries = obj_callrequest.aleg_gateway.gateway_retries
    originate_dial_string = obj_callrequest.aleg_gateway.originate_dial_string
    callmaxduration = obj_campaign.callmaxduration

    originate_dial_string = obj_callrequest.aleg_gateway.originate_dial_string

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
                                   phone_number=obj_callrequest.phone_number,
                                   gateway=gateways)
        result = res.get()
        logger.info(result)
        logger.error('Received RequestUUID :> ' + str(result['RequestUUID']))

    elif settings.NEWFIES_DIALER_ENGINE.lower() == 'plivo':
        #Request Call via Plivo
        from telefonyhelper import call_plivo
        try:
            result= call_plivo(callerid=obj_callrequest.callerid,
                        phone_number=obj_callrequest.phone_number,
                        Gateways=gateways,
                        GatewayCodecs=gateway_codecs,
                        GatewayTimeouts=gateway_timeouts,
                        GatewayRetries=gateway_retries,
                        ExtraDialString=originate_dial_string,
                        AnswerUrl=settings.PLIVO_DEFAULT_ANSWER_URL,
                        #AnswerUrl='http://localhost/~areski/django/MyProjects/plivohelper-php/examples/test.php?answer=1',
                        HangupUrl=settings.PLIVO_DEFAULT_HANGUP_URL,
                        TimeLimit=str(callmaxduration))
        except:
            logger.error('error : call_plivo')
            obj_callrequest.status = 2 # Update to Failure
            obj_callrequest.save()
            return False
        logger.info(result)
        logger.error('Received RequestUUID :> ' + str(result['RequestUUID']))

    else:
        logger.error('No other method supported, use one of these options :'\
                     'dummy ; plivo')
        return False

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
    logger = dummy_testcall.get_logger()
    logger.info("TASK :: dummy_testcall")
    logger = dummy_testcall.get_logger()
    logger.debug("Executing task id %r, args: %r kwargs: %r" % \
                (dummy_testcall.request.id,
                 dummy_testcall.request.args,
                 dummy_testcall.request.kwargs))
    logger.info("Waiting 1 seconds...")
    sleep(1)

    request_uuid = uuid1()

    #Trigger AnswerURL
    dummy_test_answerurl.delay(request_uuid)
    #Trigger HangupURL
    dummy_test_hangupurl.delay(request_uuid)

    return {'RequestUUID' : request_uuid}


@task(default_retry_delay=2)  # retry in 2 seconds.
def dummy_test_answerurl(request_uuid):
    """This task triggers a call to local answer
    This is used for test purposes to simulate the behavior of Plivo

    **Attributes**:

        * ``RequestUUID`` - A unique identifier for API request."""
    logger = dummy_test_answerurl.get_logger()
    logger.info("TASK :: dummy_testcall")
    logger = dummy_test_answerurl.get_logger()
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
    obj_callrequest.status = 4 # SUCCESS
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
    """This task triggers a call to local answer
    This is used for test purposes to simulate the behavior of Plivo

    **Attributes**:

        * ``RequestUUID`` - A unique identifier for API request."""
    logger = dummy_test_hangupurl.get_logger()
    logger.info("TASK :: dummy_test_hangupurl")
    logger = dummy_test_hangupurl.get_logger()
    logger.debug("Executing task id %r, args: %r kwargs: %r" % \
                (dummy_test_hangupurl.request.id,
                 dummy_test_hangupurl.request.args,
                 dummy_test_hangupurl.request.kwargs))
    logger.info("Waiting 10 seconds...")
    sleep(10)

    #find VoIPCall
    try:
        obj_voipcall = VoIPCall.objects.get(request_uuid=request_uuid)
    except :
        sleep(1)
        obj_voipcall = VoIPCall.objects.get(request_uuid=request_uuid)

    #Update VoIPCall
    obj_voipcall.status = 'ANSWER' # 1
    obj_voipcall.duration = 55
    obj_voipcall.billsec = 55
    obj_voipcall.save()

    obj_callrequest = Callrequest.objects.get(request_uuid=request_uuid)
    obj_callrequest.hangup_cause = 'NORMAL_CLEARING'
    obj_callrequest.save()
    
    return True


"""
# TODO : Review logic
    try:
        dialer_set = user_dialer_setting(obj_campaign.user)
        if dialer_set:
            if obj_callrequest.num_attempt >= dialer_set.maxretry:
                logger.error("Not allowed retry")
                return False
    except:
        logger.error("Can't find dialer setting for user of the campaign : %s" % campaign_id)
        return False
    # TODO : num_attempt should incremented by 1
    # count of retries
    obj_callrequest.num_attempt += 1
"""