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

from django.core.exceptions import ObjectDoesNotExist
from celery.task import PeriodicTask
from celery.task import Task
from celery.utils.log import get_task_logger
from dialer_campaign.models import Campaign
from dialer_campaign.constants import SUBSCRIBER_STATUS,\
    CAMPAIGN_STATUS
from dialer_cdr.constants import CALLREQUEST_STATUS, CALLREQUEST_TYPE
from dialer_cdr.models import Callrequest
from dialer_cdr.tasks import init_callrequest
from dialer_contact.tasks import collect_subscriber
from dnc.models import DNCContact
from common.only_one_task import only_one
from datetime import datetime, timedelta
from django.utils.timezone import utc
from math import floor
from common_functions import debug_query
# from celery.task.http import HttpDispatchTask
# from common_functions import isint

LOCK_EXPIRE = 60 * 10 * 1  # Lock expires in 10 minutes
DIV_MIN = 10  # This will divide the minutes by that value and allow to not wait too long for the calls

logger = get_task_logger(__name__)


# OPTIMIZATION - FINE
class campaign_spool_contact(PeriodicTask):
    """A periodic task that checks the the running campaign
    for each running campaign it will check if it's necessary to import
    the contact from the phonebook to the subscriber list

    **Usage**:

        campaign_spool_contact.delay()
    """
    # The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    run_every = timedelta(seconds=60)

    def run(self, **kwargs):
        logger.info("TASK :: campaign_spool_contact")

        for campaign in Campaign.objects.get_running_campaign():
            logger.debug("=> Spool Contact : Campaign name %s (id:%s)" %
                        (campaign.name, str(campaign.id)))
            # Start collecting the contacts for this campaign
            collect_subscriber.delay(campaign.id)


# OPTIMIZATION - FINE
class pending_call_processing(Task):
    @only_one(ikey="check_pendingcall", timeout=LOCK_EXPIRE)
    def run(self, campaign_id):
        """
        This task retrieves the next outbound call to be made for a given campaign,
        and will create a new callrequest and schedule a task to process those calls

        **Attributes**:

            * ``campaign_id`` - Campaign ID
        """
        logger = self.get_logger()
        logger.info("TASK :: pending_call_processing = %d" % campaign_id)

        debug_query(0)

        try:
            obj_campaign = Campaign.objects.select_related('user__userprofile__dialersetting', 'aleg_gateway', 'content_type').get(id=campaign_id)
        except:
            logger.error("Can't find this campaign")
            return False

        # TODO : Control the Speed
        # if there is many task pending we should slow down
        frequency = obj_campaign.frequency  # default 10 calls per minutes

        debug_query(1)

        #TODO: move this logic of setting call_type after post_save of CallRequest
        # Default call_type
        call_type = CALLREQUEST_TYPE.ALLOW_RETRY
        # Check campaign's maxretry
        if obj_campaign.maxretry == 0:
            call_type = CALLREQUEST_TYPE.CANNOT_RETRY

        # Check user's dialer setting maxretry
        try:
            obj_campaign.user.userprofile.dialersetting
            if obj_campaign.user.userprofile.dialersetting.maxretry == 0:
                call_type = CALLREQUEST_TYPE.CANNOT_RETRY
        except ObjectDoesNotExist:
            logger.error("Can't find user's dialersetting")
            return False

        debug_query(2)

        # Speed
        # Check if the other tasks send for this campaign finished to be ran

        # Get the subscriber of this campaign
        # get_pending_subscriber get Max 1000 records
        if frequency >= 10:
            callfrequency = int(frequency / DIV_MIN) + 1  # 1000 per minutes 101
            #callfrequency = int(frequency) + 1  # 1000 per minutes 101
        else:
            callfrequency = frequency
        (list_subscriber, no_subscriber) = obj_campaign.get_pending_subscriber_update(callfrequency, SUBSCRIBER_STATUS.IN_PROCESS)
        logger.info("##subscriber=%d campaign_id=%d callfrequency=%d frequency=%d" % (no_subscriber, campaign_id, callfrequency, frequency))
        debug_query(3)

        if no_subscriber == 0:
            return False

        # Set time to wait for balanced dispatching of calls
        #time_to_wait = int(60 / DIV_MIN) / no_subscriber
        time_to_wait = 6.0 / no_subscriber
        count = 0

        for elem_camp_subscriber in list_subscriber:
            # Loop on Subscriber and start the initcall's task
            count = count + 1
            second_towait = floor(count * time_to_wait)
            ms_addtowait = (count * time_to_wait) - second_towait
            logger.info("Init CallRequest in %d seconds (cmpg:%d,subscriber:%d)" % (second_towait, campaign_id, elem_camp_subscriber.id))

            phone_number = elem_camp_subscriber.duplicate_contact
            debug_query(4)

            #Verify that the contact is authorized
            if not obj_campaign.is_authorized_contact(obj_campaign.user.userprofile.dialersetting, phone_number):
                logger.error("Error : Contact not authorized")
                elem_camp_subscriber.status = SUBSCRIBER_STATUS.NOT_AUTHORIZED
                elem_camp_subscriber.save()
                return True
            #Verify that the contact is not in the DNC list
            if obj_campaign.dnc:
                res_dnc = DNCContact.objects.filter(dnc_id=obj_campaign.dnc_id, phone_number=phone_number)
                if res_dnc:
                    logger.error("Contact (%s) in DNC list" % phone_number)
                    elem_camp_subscriber.status = SUBSCRIBER_STATUS.NOT_AUTHORIZED
                    elem_camp_subscriber.save()
                    return True
                else:
                    logger.debug("Contact (%s) not in DNC list" % phone_number)

            debug_query(5)

            #TODO: idea to speed up, create bluck of 10(Y) and then send a list of callrequest_id to init_callrequest

            # Create Callrequest
            new_callrequest = Callrequest(
                status=CALLREQUEST_STATUS.PENDING,
                call_type=call_type,
                call_time=datetime.utcnow().replace(tzinfo=utc),
                timeout=obj_campaign.calltimeout,
                callerid=obj_campaign.callerid,
                caller_name=obj_campaign.caller_name,
                phone_number=phone_number,
                campaign=obj_campaign,
                aleg_gateway=obj_campaign.aleg_gateway,
                content_type=obj_campaign.content_type,
                object_id=obj_campaign.object_id,
                user=obj_campaign.user,
                extra_data=obj_campaign.extra_data,
                timelimit=obj_campaign.callmaxduration,
                subscriber=elem_camp_subscriber)
            new_callrequest.save()

            debug_query(6)

            init_callrequest.apply_async(
                args=[new_callrequest.id, obj_campaign.id, obj_campaign.callmaxduration, ms_addtowait],
                countdown=second_towait)
            # Shell_plus
            # from dialer_cdr.tasks import init_callrequest
            # from datetime import datetime
            # new_callrequest_id = 112
            # obj_campaign_id = 3
            # countdown = 1
            # init_callrequest.apply_async(args=[new_callrequest_id, obj_campaign_id], countdown=1)

        debug_query(7)
        return True


# OPTIMIZATION - FINE
class campaign_running(PeriodicTask):
    """A periodic task that checks the campaign, create and spool the calls

    **Usage**:

        campaign_running.delay()
    """
    run_every = timedelta(seconds=int(60 / DIV_MIN))
    # NOTE : until we implement a PID Controller :
    # http://en.wikipedia.org/wiki/PID_controller

    # The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    # run_every = timedelta(seconds=60)

    def run(self, **kwargs):
        logger.debug("TASK :: campaign_running")

        for campaign in Campaign.objects.get_running_campaign():
            logger.info("=> Campaign name %s (id:%s)" %
                        (campaign.name, campaign.id))
            keytask = 'check_campaign_pendingcall-%d' % (campaign.id)
            pending_call_processing().delay(campaign.id, keytask=keytask)
        return True


# OPTIMIZATION - FINE
class campaign_expire_check(PeriodicTask):
    """A periodic task that checks the campaign expiration

    **Usage**:

        campaign_expire_check.delay()
    """
    run_every = timedelta(seconds=300)

    @only_one(ikey="campaign_expire_check", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.info("TASK :: campaign_expire_check")
        campaign_id_list = []
        for obj_campaign in Campaign.objects.get_expired_campaign():
            logger.debug("=> Campaign name %s (id:%s)" %
                        (obj_campaign.name, obj_campaign.id))
            campaign_id_list.append(obj_campaign.id)

        #Update in bulk
        Campaign.objects.filter(id__in=campaign_id_list).update(status=CAMPAIGN_STATUS.END)
        return True
