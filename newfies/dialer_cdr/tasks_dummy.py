from celery.utils.log import get_task_logger
from celery.decorators import task
from dialer_cdr.models import Callrequest, VoIPCall
from uuid import uuid1
from time import sleep


logger = get_task_logger(__name__)

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
    logger.debug("Executing task id %r, args: %r kwargs: %r" %
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
    logger.debug("Executing task id %r, args: %r kwargs: %r" %
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
    logger.debug("Executing task id %r, args: %r kwargs: %r" %
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
