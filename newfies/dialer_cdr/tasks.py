from datetime import date, timedelta
from celery.task import Task, PeriodicTask
from celery.task.http import HttpDispatchTask, HttpDispatch
from dialer_campaign.models import *
from dialer_cdr.models import *
from celery.decorators import task
from common_functions import isint
from django.db import IntegrityError
from time import sleep
import telefonyhelper
from uuid import uuid1


class callrequest_pending(PeriodicTask):
    """A periodic task that check for pending calls

    **Usage**:

        callrequest_pending.delay()
    """
    # 1000000 ms = 1 sec
    run_every = timedelta(microseconds=5000000)
    
    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.debug("Determine if new pending calls")

        list_callrequest = Callrequest.objects.get_pending_callrequest()[:20]
        if not list_callrequest:
            logger.info("No Pending Calls")
        
        for callrequest in list_callrequest:
            logger.info("\n\n\n\n=> CallRequest (id:%s, phone_number:%s)" %
                        (callrequest.id, callrequest.phone_number))
            
            #TODO : update the callrequest to PROCESS 
            #callrequest.status = 7 # Update to Process
            #callrequest.save()
            init_callrequest.delay(callrequest.id, callrequest.campaign)

@task()
def init_callrequest(callrequest_id, campaign_id):
    """This tasks will outbound the call

    **Attributes**:

        * ``callrequest_id`` -
    """
    logger = init_callrequest.get_logger()
    logger.info('>> Dialout init_callrequest')
    obj_callrequest = Callrequest.objects.get(id=callrequest_id)
    logger.info("callrequest status = %s" % str(obj_callrequest.status))
    
    try:
        obj_campaign = Campaign.objects.get(id=campaign_id)
    except:
        logger.error('Can\'t find this campaign')

    """
    #Check if the contact is authorized
    if not obj_campaign.is_authorized_contact(obj_campaignsubscriber.contact):
        logger.error("Contact not authorized")
        obj_campaignsubscriber.status = 7 # Update to Not Authorized
        obj_campaignsubscriber.save()
        return True
    """
    
    #Construct the dialing out path

    #Send Call to API
    #http://ask.github.com/celery/userguide/remote-tasks.html

    #Todo this will be replaced by the Plivo RestAPIs
    """
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
    #Plivo
    """
    result= telefonyhelper.call_plivo()
    """
    res = dummy_testcall.delay(callerid='901901901', phone_number='1000', gateway='user/')
    result = res.get()

    logger.info('Received RequestUUID :> ' + str(result['RequestUUID']))

        
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
    """
    This is used for test purpose to simulate the behavior of Plivo

    **Attributes**:

        * ``callerid`` - CallerID
        * ``phone_number`` - Phone Number to call
        * ``gateway`` - Gateway to use for the call

    **Return**:

        * ``RequestUUID`` - A unique identifier for API request."""

    logger = dummy_testcall.get_logger()
    logger.info("Executing task id %r, args: %r kwargs: %r" % (
        dummy_testcall.request.id, dummy_testcall.request.args, dummy_testcall.request.kwargs))
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
    """This task trigger a call to local answer
    This is used for test purpose to simulate the behavior of Plivo

    **Attributes**:

        * ``RequestUUID`` - A unique identifier for API request."""
    logger = dummy_test_answerurl.get_logger()
    logger.info("Executing task id %r, args: %r kwargs: %r" % (
        dummy_test_answerurl.request.id, dummy_test_answerurl.request.args, dummy_test_answerurl.request.kwargs))
    logger.info("Waiting 1 seconds...")
    sleep(1)

    #find Callrequest
    try:
        obj_callrequest = Callrequest.objects.get(request_uuid=request_uuid)
    except :
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
                            sessiontime=0,
                            disposition=1)
    new_voipcall.save()

    #lock to limit running process, do so per campaign
    #http://ask.github.com/celery/cookbook/tasks.html

    return True


@task(default_retry_delay=2)  # retry in 2 seconds.
def dummy_test_hangupurl(request_uuid):
    """This task trigger a call to local answer
    This is used for test purpose to simulate the behavior of Plivo

    **Attributes**:

        * ``RequestUUID`` - A unique identifier for API request."""
    logger = dummy_test_hangupurl.get_logger()
    logger.info("Executing task id %r, args: %r kwargs: %r" % (
        dummy_test_hangupurl.request.id, dummy_test_hangupurl.request.args, dummy_test_hangupurl.request.kwargs))
    logger.info("Waiting 10 seconds...")
    sleep(10)

    #find VoIPCall
    try:
        obj_voipcall = VoIPCall.objects.get(request_uuid=request_uuid)
    except :
        sleep(1)
        obj_voipcall = VoIPCall.objects.get(request_uuid=request_uuid)

    #Update VoIPCall
    obj_voipcall.status = 1 # ANSWER
    obj_voipcall.sessiontime = 55
    obj_voipcall.save()

    obj_callrequest = Callrequest.objects.get(request_uuid=request_uuid)
    obj_callrequest.hangup_cause = 'NORMAL_CLEARING'
    obj_callrequest.save()
    
    return True