from celery.task import Task, PeriodicTask
from dialer_campaign.models import Campaign, CampaignSubscriber
from dialer_cdr.models import Callrequest, VoIPCall
from celery.decorators import task
from django.db import IntegrityError
from datetime import datetime, timedelta
from time import sleep
#from celery.task.http import HttpDispatchTask
#from common_functions import isint


@task(default_retry_delay=30 * 60)  # retry in 30 minutes.
def add(x, y):
    """This task adds 2 numbers.
    For instance (1, 2) will return '3'

    **Attributes**:

        * ``x`` -
        * ``y`` -"""

    print("Executing task id %r, args: %r kwargs: %r" % (
        add.request.id, add.request.args, add.request.kwargs))
    try:
        return x + y
    except Exception, exc:
        self.retry(exc=exc, countdown=60)  # override the default and
                                           # retry in 1 minute




@task()
def initiate_call_subscriber(subscriber_id, campaign_id):
    """This task will outbound the call to the subscriber

    **Attributes**:

        * ``subscriber_id`` - Campaign Subscriber`s ID
        * ``callrequest_id`` - Callrequest ID
    """
    logger = initiate_call_subscriber.get_logger()
    obj_subscriber = CampaignSubscriber.objects.get(id=subscriber_id)
    logger.info("\nTASK :: initiate_call_subscriber - status = %s" %
                str(obj_subscriber.status))

    try:
        obj_camp_subs = CampaignSubscriber.objects\
                                 .get(id=subscriber_id)
    except:
        logger.error('Can\'t find this CampaignSubscriber')

    try:
        obj_campaign = Campaign.objects.get(id=campaign_id)
    except:
        logger.error('Can\'t find this Campaign')

    if obj_subscriber.status != 1:
        logger.error("Only Pending status are processed ")
        return True

    #Check if the contact is authorized
    if not obj_campaign.is_authorized_contact(obj_camp_subs.contact.contact):
        logger.error("Contact not authorized")
        obj_camp_subs.status = 7 # Update to Not Authorized
        obj_camp_subs.save()
        return True

    #Create a Callrequest Instance to track the call task
    new_callrequest = Callrequest(status=1, #PENDING
                            call_time=datetime.now(),
                            timeout=obj_campaign.calltimeout,
                            callerid=obj_campaign.callerid,
                            phone_number=obj_camp_subs.contact.contact,
                            campaign=obj_campaign,
                            aleg_gateway=obj_campaign.aleg_gateway,
                            voipapp=obj_campaign.voipapp,
                            user=obj_campaign.user,
                            extra_data=obj_campaign.extra_data,
                            timelimit=obj_campaign.callmaxduration,
                            campaign_subscriber=obj_camp_subs)
    new_callrequest.save()

    #Update the campaign status
    obj_camp_subs.status = 6 # Update to In Process
    obj_camp_subs.callrequest = new_callrequest
    obj_camp_subs.save()
    
    return True


#TODO: Put a priority on this task
@task()
def check_campaign_pendingcall(campaign_id):
    """This will execute the outbound calls in the campaign

    **Attributes**:

        * ``campaign_id`` - Campaign ID
    """
    logger = check_campaign_pendingcall.get_logger()
    logger.info("TASK :: check_campaign_pendingcall = %s" % str(campaign_id))

    try:
        obj_campaign = Campaign.objects.get(id=campaign_id)
    except:
        logger.error('Can\'t find this campaign')

    #TODO: Control the Speed
    #if there is many task pending we should slow down
    frequency = obj_campaign.frequency # default 10 calls per minutes

    #Speed
    #check if the other tasks send for this campaign finished to be ran

    #Get the subscriber of this campaign
    # get_pending_subscriber get Max 1000 records
    list_subscriber = obj_campaign.get_pending_subscriber(frequency)
    #print (list_subscriber)

    try:
        no_subscriber = list_subscriber.count()
    except AttributeError:
        no_subscriber = 0

    if no_subscriber == 0:
        logger.debug("No Subscriber to proceed on this campaign")
        return False

    #find how to dispatch them in the current minutes
    time_to_wait = 60.0 / no_subscriber

    for elem_subscriber in list_subscriber:
        """Loop on Subscriber and start the initcall task"""
        initiate_call_subscriber.delay(elem_subscriber.id, campaign_id)
        sleep(time_to_wait)


class campaign_running(PeriodicTask):
    """A periodic task that checks the campaign, create and tasks the calls

    **Usage**:

        campaign_running.delay()
    """

    run_every = timedelta(seconds=15)
    #The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    #run_every = timedelta(seconds=60)

    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info( "TASK :: campaign_running")

        for campaign in Campaign.objects.get_running_campaign():
            logger.debug("=> Campaign name %s (id:%s)" % (campaign.name,
                                                         campaign.id))

            check_campaign_pendingcall.delay(campaign.id)

@task()
def collect_subscriber(campaign_id):
    """This task will collect all the subscribers

    **Attributes**:

        * ``campaign_id`` - Campaign ID
    """
    logger = collect_subscriber.get_logger()
    logger.debug("Collect subscribers for the campaign = %s" % str(campaign_id))

    #Retrieve the list of active contact
    obj_campaign = Campaign.objects.get(id=campaign_id)
    list_contact = obj_campaign.get_active_contact_no_subscriber()

    if not list_contact:
        logger.debug("No new contact or phonebook to import into \
            this campaign.")
        return True
    else:
        #Create CampaignSubscribers for each new active contact
        for elem_contact in list_contact:
            try:
                CampaignSubscriber.objects.create(
                                    contact=elem_contact,
                                    status=1, #START
                                    duplicate_contact=elem_contact.contact,
                                    campaign=obj_campaign)
            except IntegrityError, e:
                #We don't stop if it fails to add a subscriber to one campaign
                logger.error("IntegrityError to create CampaignSubscriber "\
                    "contact_id=%s - Error:%s" % (elem_contact.id, e))

    return True
