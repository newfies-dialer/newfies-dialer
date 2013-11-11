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
from appointment.models.users import CalendarUserProfile
from appointment.constants import EVENT_STATUS, ALARM_STATUS, ALARM_METHOD

from mod_mailer.models import MailSpooler  #, MailTemplate
from mod_mailer.constants import MAILSPOOLER_TYPE

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

    For each Event found, the PeriodicTask event_dispatcher will ::

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

        # List all the events where event.start > NOW() - 12 hours and status = EVENT_STATUS.PENDING
        start = datetime.now() - timedelta(hours=12)
        event_list = Event.objects.filter(start__gte=start, status=EVENT_STATUS.PENDING)
        for obj_event in event_list:
            try:
                # Get and perform alarm
                obj_alarm = Alarm.objects.get(event=obj_event)
                perform_alarm.delay(obj_event, obj_alarm)
            except ObjectDoesNotExist:
                pass

            # Check if need to create a sub event in the future
            next_occurrence = obj_event.get_next_occurrence()
            print "next_occurrence"
            print next_occurrence

            if next_occurrence:
                # The result of get_next_occurrences help to create the next event
                new_event = obj_event.copy_event(next_occurrence)

                # Copy the alarm link to the event
                alarm_list = Alarm.objects.filter(event=obj_event)
                for obj_alarm in alarm_list:
                    obj_alarm.copy_alarm(new_event)

            # Mark the event as COMPLETED
            obj_event.status = EVENT_STATUS.COMPLETED
            obj_event.save()


class alarm_dispatcher(PeriodicTask):
    """A periodic task that checks for scheduled Alarm and trigger the Alarm according
    to the alarm type, such as phone Call, SMS or Email.

    For each Alarm found, the PeriodicTask alarm_dispatcher will ::

        - found when the next alarm should be performed. We should notice that alarm
          trigger date/time is not related to the event date, an alarm can happen
          hours/days before an event occurs

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
        # Browse all the Alarms found
        for obj_alarm in alarm_list:
            # Check if there is an existing Event
            if obj_alarm.event:
                # TODO fix second_towait => second_towait = Alarm.date_start_notice - now()
                # if second_towait negative then set to 0 to be run directly
                second_towait = (obj_alarm.daysdate_start_notice - datetime.now()).seconds
                if second_towait < 0:
                    second_towait = 0

                if second_towait == 0:
                    perform_alarm.delay(obj_alarm.event, obj_alarm)
                else:
                    perform_alarm.apply_async(
                        args=[obj_alarm.event, obj_alarm], countdown=second_towait)
            else:
                logger.error("not event link to alarm: %d" % obj_alarm.id)
                #TODO: Mark Alarm as completed / error


@task()
def perform_alarm(obj_event, obj_alarm):
    """
    Task to perform the alarm
    """
    logger.info("TASK :: perform_alarm")

    #if obj_alarm.method == ALARM_METHOD.CALL:
    #    # perform CALL
    #    pass
    #elif obj_alarm.method == ALARM_METHOD.SMS:
    #    # perform SMS
    if obj_alarm.method == ALARM_METHOD.EMAIL:
        # perform EMAIL
        if obj_alarm.alarm_email and obj_alarm.mail_template:
            # create MailSpooler object

            MailSpooler.objects.create(
                mailtemplate=obj_alarm.mail_template,
                contact_email=obj_alarm.alarm_email
            )
