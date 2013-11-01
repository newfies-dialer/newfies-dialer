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

from celery.task import PeriodicTask
from celery.decorators import task
from celery.utils.log import get_task_logger
from common.only_one_task import only_one
from appointment.models.alarms import Alarm
#from appointment.models.rules import Rule
from appointment.models.events import Event
from appointment.constants import EVENT_STATUS, ALARM_STATUS

# from celery.task.http import HttpDispatchTask
# from common_functions import isint
from datetime import datetime, timedelta
#import time


LOCK_EXPIRE = 60 * 10 * 1  # Lock expires in 10 minutes

logger = get_task_logger(__name__)


class event_dispatcher(PeriodicTask):
    """A periodic task that checks the events that occur and
    for each event it will do the following ::

        - check if needed to recreate a new event if a Rule is set for the event

        - check if there is an alarm for this event and then perform the alarm

    **Usage**:

        event_dispatcher.delay()
    """
    run_every = timedelta(seconds=60)

    @only_one(ikey="event_dispatcher", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.info("TASK :: event_dispatcher")

        #TODO:
        # 1) Will list all the event where event.start > NOW() and status = EVENT_STATUS.PENDING
        event_list = Event.objects.filter(start=datetime.now(), status=EVENT_STATUS.PENDING)
        for obj_event in event_list:

            try:
                # if event is attached with alarm then perform alarm
                alarm_id = Alarm.objects.get(event=obj_event).id
                alarm_dispatcher.delay(obj_event, alarm_id)
            except:
                pass

            # 2) Then will check if need to create a sub event, see if there is a FK.rule
            #    if so, base on the rule we will create a new event in the future (if the current event
            #    have one or several alarms, the alarms should be copied also)
            #if obj_event.rule:
            #    Event.objects.create()

            # 3) Mark the event as COMPLETED
            #obj_event.status = EVENT_STATUS.COMPLETED
            obj_event.save()


class alarm_dispatcher(PeriodicTask):
    """A periodic task that checks the alarms that occur and
    for each alarm it will do the following ::

        - check if the alarm should be run now

        - check if needed to perform some action based on the alarm type

    **Usage**:

        alarm_dispatcher.delay()
    """
    run_every = timedelta(seconds=60)

    @only_one(ikey="alarm_dispatcher", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.info("TASK :: alarm_dispatcher")

        #TODO: find the alarms where date_start_notice > NOW() and ALARM_STATUS.PENDING
        alarm_list = Alarm.objects.filter(date_start_notice=datetime.now(),
                                          status=ALARM_STATUS.PENDING)
        print alarm_list

        # For each alarms that need to be proceed get the event related and the id
        obj_event = None
        alarm_id = None

        perform_alarm.delay(obj_event, alarm_id)


@task()
def perform_alarm(obj_event, alarm_id):
    """
    Task to perform the alarm
    """
    logger.info("TASK :: perform_alarm")

    # TODO: this should not be done now, for the moment only print the alarm content
