from datetime import date, timedelta
from celery.task import Task, PeriodicTask
from celery.task.http import HttpDispatchTask
from dialer_campaign.models import *
from dialer_cdr.models import *
from celery.decorators import task
from common_functions import isint
from django.db import IntegrityError
from time import sleep
import telefonyhelper

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
    """
    res = HttpDispatchTask.delay(
          url="http://127.0.0.1:8000/api/dialer_cdr/testcall/",
          method="POST", x=10, y=10)
    #Todo this will be replaced by the Plivo RestAPIs
    result = res.get()

    """
    result= telefonyhelper.call_plivo()
    print result
    logger.info(result['RequestUUID'])
    
    obj_callrequest.request_uuid = result['RequestUUID']
    obj_callrequest.save()

    #lock to limit running process, do so per campaign
    #http://ask.github.com/celery/cookbook/tasks.html

    return True
