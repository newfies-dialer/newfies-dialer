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

from django.conf import settings
from celery.task import PeriodicTask
from celery.decorators import task
from celery.utils.log import get_task_logger
from dialer_campaign.models import Campaign
from dialer_campaign.function_def import user_dialer_setting
from dialer_cdr.models import Callrequest
from dialer_cdr.tasks import init_callrequest
from dialer_contact.tasks import collect_subscriber
from common.only_one_task import only_one
from datetime import datetime, timedelta
from math import ceil
#from celery.task.http import HttpDispatchTask
#from common_functions import isint


if settings.DIALERDEBUG:
    Timelaps = 5
else:
    Timelaps = 60

LOCK_EXPIRE = 60 * 10 * 1  # Lock expires in 10 minutes

logger = get_task_logger(__name__)


class campaign_spool_contact(PeriodicTask):
    """A periodic task that checks the campaign, add subscribers

    **Usage**:

        campaign_spool_contact.delay()
    """

    run_every = timedelta(seconds=15)
    #The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    #run_every = timedelta(seconds=60)

    def run(self, **kwargs):
        logger.info("TASK :: campaign_spool_contact")

        for campaign in Campaign.objects.get_running_campaign():
            logger.debug("=> Spool Contact : Campaign name %s (id:%s)" % \
                (campaign.name, str(campaign.id)))

            #Start collecting the contacts for this campaign
            collect_subscriber.delay(campaign.id)


#TODO: Put a priority on this task
@task()
def check_campaign_pendingcall(campaign_id):
    """This will execute the outbound calls in the campaign

    **Attributes**:

        * ``campaign_id`` - Campaign ID
    """
    logger.info("TASK :: check_campaign_pendingcall = %s" % str(campaign_id))

    try:
        obj_campaign = Campaign.objects.get(id=campaign_id)
    except:
        logger.error('Can\'t find this campaign')
        return False

    #TODO: Control the Speed
    #if there is many task pending we should slow down
    frequency = obj_campaign.frequency  # default 10 calls per minutes

    dialer_set = user_dialer_setting(obj_campaign.user)

    # default call_type
    call_type = 1
    # Check campaign's maxretry
    if obj_campaign.maxretry == 0:
        call_type = 2

    # Check user's dialer setting maxretry
    if dialer_set:
        if dialer_set.maxretry == 0:
            call_type = 2

        # check frequency to control the Speed
        #if dialer_set.frequency:
        #    frequency = 20

    #Speed
    #check if the other tasks send for this campaign finished to be ran

    #Get the subscriber of this campaign
    # get_pending_subscriber get Max 1000 records
    list_subscriber = obj_campaign.get_pending_subscriber_update(
                            frequency,
                            6  # Update to In Process
                            )
    if list_subscriber:
        logger.debug("Number of subscriber found : %d" % len(list_subscriber))

    try:
        no_subscriber = list_subscriber.count()
    except AttributeError:
        no_subscriber = 0

    if no_subscriber == 0:
        logger.info("No Subscriber to proceed on this campaign")
        return False

    if no_subscriber < 10:
        #if not many subscriber, don't wait too long n create a faster dialing feeling
        time_to_wait = 6.0
    else:
        #Set time to wait for balanced dispatching of calls
        time_to_wait = 60.0 / no_subscriber

    count = 0
    for elem_camp_subscriber in list_subscriber:
        """Loop on Subscriber and start the initcall task"""
        count = count + 1
        logger.info("Add CallRequest for Subscriber (%s) & wait (%s) " %
                        (str(elem_camp_subscriber.id), str(time_to_wait)))

        #Check if the contact is authorized
        if not obj_campaign.is_authorized_contact(
                        elem_camp_subscriber.contact.contact):
            logger.error("Error : Contact not authorized")
            elem_camp_subscriber.status = 7  # Update to Not Authorized
            elem_camp_subscriber.save()
            return True

        #Create a Callrequest Instance to track the call task
        new_callrequest = Callrequest(status=1,  # PENDING
                            call_type=call_type,
                            call_time=datetime.now(),
                            timeout=obj_campaign.calltimeout,
                            callerid=obj_campaign.callerid,
                            phone_number=elem_camp_subscriber.contact.contact,
                            campaign=obj_campaign,
                            aleg_gateway=obj_campaign.aleg_gateway,
                            content_type=obj_campaign.content_type,
                            object_id=obj_campaign.object_id,
                            user=obj_campaign.user,
                            extra_data=obj_campaign.extra_data,
                            timelimit=obj_campaign.callmaxduration,
                            subscriber=elem_camp_subscriber)
        new_callrequest.save()

        #Todo Check if it's a good practice / implement a PID algorithm
        second_towait = ceil(count * time_to_wait)
        logger.info("Init CallRequest in  %d seconds" % second_towait)
        init_callrequest.apply_async(
                    args=[new_callrequest.id, obj_campaign.id],
                    countdown=second_towait)
        #Shell_plus
        # from dialer_cdr.tasks import init_callrequest
        # from datetime import datetime
        # new_callrequest_id = 112
        # obj_campaign_id = 3
        # countdown = 1
        # init_callrequest.apply_async(args=[new_callrequest_id, obj_campaign_id], countdown=1)

    return True


class campaign_running(PeriodicTask):
    """A periodic task that checks the campaign, create and tasks the calls

    **Usage**:

        campaign_running.delay()
    """
    run_every = timedelta(seconds=Timelaps)
    #NOTE : until we implement a PID Controller :
    #http://en.wikipedia.org/wiki/PID_controller

    #The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    #run_every = timedelta(seconds=60)

    @only_one(key="campaign_running", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.debug("TASK :: campaign_running")

        for campaign in Campaign.objects.get_running_campaign():
            logger.debug("=> Campaign name %s (id:%s)" % (campaign.name,
                                                         campaign.id))

            check_campaign_pendingcall.delay(campaign.id)

        return True


class campaign_expire_check(PeriodicTask):
    """A periodic task that checks the campaign expiration

    **Usage**:

        campaign_expire_check.delay()
    """
    run_every = timedelta(seconds=300)
    #The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    #run_every = timedelta(seconds=60)

    @only_one(key="campaign_expire_check", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.info("TASK :: campaign_expire_check")
        from dialer_campaign.views import common_campaign_status
        for campaign in Campaign.objects.get_expired_campaign():
            logger.debug("=> Campaign name %s (id:%s)" % (campaign.name,
                                                         campaign.id))
            common_campaign_status(campaign.id, 4)

        return True
