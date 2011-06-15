from datetime import date, timedelta
from celery.task import Task, PeriodicTask
from celery.task.http import HttpDispatchTask
from dialer_campaign.models import *
from dialer_cdr.models import *
from celery.decorators import task
from common_functions import isint
from django.db import IntegrityError
from time import sleep


class callrequest_pending(PeriodicTask):
    """A periodic task that check for pending calls

    **Usage**:

        callrequest_pending.delay()
    """
    run_every = timedelta(microseconds=1000)

    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info("Determine if new pending calls")

        for callrequest in Callrequest.objects.get_pending_callrequest():
            logger.info("=> CallRequest (id:%s)" % (callrequest.id))
            
            #TODO : update the callrequest to PROCESS 

            #init_callrequest.delay(callrequest.id)

        logger.info("Finish Spawn the campaign")
        

@task()
def init_callrequest(callrequest_id):
    """This tasks will outbound the call

    **Attributes**:

        * ``callrequest_id`` -
    """
    logger = init_callrequest.get_logger()
    logger.info('Dialout init_callrequest')
    obj_callrequest = Callrequest.objects.get(id=callrequest_id)
    logger.info("callrequest status = %s" % str(obj_callrequest.status))

    if obj_callrequest.status == 1:
        #Here we continue
        obj_callrequest.status = 7 # Update to Process
        obj_callrequest.save()
    else:
        logger.error("Only Pending status are processed ")
        return True

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
    res = HttpDispatchTask.delay(
          url="http://127.0.0.1:8000/api/dialer_cdr/testcall/",
          method="POST", x=10, y=10)
    #Todo this will be replaced by the Plivo RestAPIs
    result = res.get()

    obj_callrequest.request_uuid = result['RequestUUID']
    obj_callrequest.save()

    #lock to limit running process, do so per campaign
    #http://ask.github.com/celery/cookbook/tasks.html

    return True
