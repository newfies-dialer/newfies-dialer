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
from dateutil.relativedelta import relativedelta
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
                obj_alarm = Alarm.objects.get(event=obj_event)
                perform_alarm.delay(obj_event, obj_alarm)
            except ObjectDoesNotExist:
                pass

            #TODO:
            # 2) Then will check if need to create a sub event, see if there is a FK.rule
            #    if so, base on the rule we will create a new event in the future (if the current event
            #    have one or several alarms, the alarms should be copied also)

            if obj_event.rule:
                # we dont need this check here (frequency == "YEARLY"),
                # instead we will implement method on event get_next_occurrences
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

                #base on the result of get_next_occurrences we will know when to create the next event
                #Event.objects.create()

            # 3) Mark the event as COMPLETED
            #obj_event.status = EVENT_STATUS.COMPLETED
            obj_event.save()


class alarm_dispatcher(PeriodicTask):
    """A periodic task that checks for scheduled Alarm and perform number of
    tasks to trigger the Alarm.

    For each Alarm found, this PeriodicTask will ::

        - found when the next alarm should be triggered, note the alarm trigger is not
          related to the date of the event, as an Alarm can happen hours/days before an event

        - run the Alarm actions based on the method/settings of the Alarm

    **Usage**:

        alarm_dispatcher.delay()
    """
    run_every = timedelta(seconds=60)

    @only_one(ikey="alarm_dispatcher", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.info("TASK :: alarm_dispatcher")

        # Select Alarm where date_start_notice >= now() - 5 minutes and <= now() + 5 minutes
        start_time = datetime.now() + relativedelta(minutes=-5)
        end_time = datetime.now() + relativedelta(minutes=+5)
        alarm_list = Alarm.objects.filter(date_start_notice__range=(start_time, end_time),
                                          status=ALARM_STATUS.PENDING)
        for obj_alarm in alarm_list:
            if obj_alarm.event:
                # For each alarms that need to be proceed get the event related and the id

                # TODO fix second_towait => second_towait = Alarm.date_start_notice - now()
                # if second_towait negative then set to 0 to be run directly
                second_towait = (obj_alarm.daysdate_start_notice - datetime.now()).seconds
                if second_towait < 0:
                    second_towait = 0

                if second_towait == 0:
                    perform_alarm.delay(obj_alarm.event, obj_alarm)
                else:
                    second_towait = 10
                    perform_alarm.apply_async(
                        args=[obj_alarm.event, obj_alarm], countdown=second_towait)


@task()
def perform_alarm(obj_event, obj_alarm):
    """
    Task to perform the alarm
    """
    logger.info("TASK :: perform_alarm")

    #if obj_alarm.method == ALARM_METHOD.CALL:
    #    # perform CALL
    #elif obj_alarm.method == ALARM_METHOD.SMS:
    #    # perform SMS
    #elif obj_alarm.method == ALARM_METHOD.EMAIL:
    #    # perform EMAIL

    # TODO: We can start implementing the Email
