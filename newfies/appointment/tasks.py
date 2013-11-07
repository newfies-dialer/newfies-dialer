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

from django.core.exceptions import ObjectDoesNotExist
from celery.task import PeriodicTask
from celery.decorators import task
from celery.utils.log import get_task_logger
from common.only_one_task import only_one
from appointment.models.alarms import Alarm
#from appointment.models.rules import Rule
from appointment.models.events import Event
from appointment.constants import EVENT_STATUS, ALARM_STATUS, ALARM_METHOD

# from celery.task.http import HttpDispatchTask
# from common_functions import isint
from datetime import datetime, timedelta
#import time


LOCK_EXPIRE = 60 * 10 * 1  # Lock expires in 10 minutes

logger = get_task_logger(__name__)


class event_dispatcher(PeriodicTask):
    """A periodic task that checks for scheduled Event and perform number of
    tasks for the Event and create the occurence of the next future Event.

    For each Event found, this PeriodicTask will ::

        - check the Rule assigned to the Event and create a new occurence of
          this event based on the Rule. The new occurence is an other Event object.

        - check if an alarm exists and execute the alarm

    **Usage**:

        event_dispatcher.delay()
    """
    run_every = timedelta(seconds=60)

    @only_one(ikey="event_dispatcher", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.info("TASK :: event_dispatcher")

        # 1) Will list all the events where event.start > NOW() and status = EVENT_STATUS.PENDING
        event_list = Event.objects.filter(start=datetime.now(), status=EVENT_STATUS.PENDING)
        for obj_event in event_list:
            try:
                # if event is attached with alarm then perform alarm
                alarm_id = Alarm.objects.get(event=obj_event).id
                perform_alarm.delay(obj_event, alarm_id)
            except ObjectDoesNotExist:
                pass

            #TODO:
            # 2) Then will check if need to create a sub event, see if there is a FK.rule
            #    if so, base on the rule we will create a new event in the future (if the current event
            #    have one or several alarms, the alarms should be copied also)

            if obj_event.rule:
                if obj_event.rule.frequency == "YEARLY":
                    pass
                elif obj_event.rule.frequency == "MONTHLY":
                    pass
                elif obj_event.rule.frequency == "WEEKLY":
                    pass
                elif obj_event.rule.frequency == "DAILY":
                    pass
                elif obj_event.rule.frequency == "HOURLY":
                    pass
                elif obj_event.rule.frequency == "MINUTELY":
                    pass
                elif obj_event.rule.frequency == "SECONDLY":
                    pass

                #Event.objects.create()

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

        alarm_list = Alarm.objects.filter(date_start_notice=datetime.now(),
                                          status=ALARM_STATUS.PENDING)
        for obj_alarm in alarm_list:
            if obj_alarm.event:
                # For each alarms that need to be proceed get the event related and the id
                perform_alarm.delay(obj_alarm.event, obj_alarm.id)

            #if obj_alarm.method == ALARM_METHOD.CALL:
            #    # perform CALL
            #elif obj_alarm.method == ALARM_METHOD.SMS:
            #    # perform SMS
            #elif obj_alarm.method == ALARM_METHOD.EMAIL:
            #    # perform EMAIL


@task()
def perform_alarm(obj_event, alarm_id):
    """
    Task to perform the alarm
    """
    logger.info("TASK :: perform_alarm")

    # TODO: this should not be done now, for the moment only print the alarm content
