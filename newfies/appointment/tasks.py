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
from django.contrib.contenttypes.models import ContentType
from celery.task import PeriodicTask
from celery.decorators import task
from celery.utils.log import get_task_logger
from common.only_one_task import only_one
from appointment.models.alarms import Alarm, AlarmRequest
from appointment.models.events import Event
from appointment.models.users import CalendarUserProfile
from appointment.constants import EVENT_STATUS, ALARM_STATUS, \
    ALARM_METHOD, ALARMREQUEST_STATUS
from mod_mailer.models import MailSpooler
from dialer_cdr.models import Callrequest
from dialer_cdr.tasks import init_callrequest
from dialer_cdr.constants import CALLREQUEST_STATUS, CALLREQUEST_TYPE
from math import floor
from datetime import datetime, timedelta
from django.utils.timezone import utc
from dateutil.relativedelta import relativedelta


LOCK_EXPIRE = 60 * 10 * 1  # Lock expires in 10 minutes
FREQ_DISPATCHER = 6

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
        start_from = datetime.utcnow().replace(tzinfo=utc) - timedelta(hours=12)
        start_to = datetime.utcnow().replace(tzinfo=utc)
        event_list = Event.objects.filter(start__gte=start_from, start__lte=start_to, status=EVENT_STATUS.PENDING)
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
    run_every = timedelta(seconds=FREQ_DISPATCHER)

    @only_one(ikey="alarm_dispatcher", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.info("TASK :: alarm_dispatcher")

        # Select Alarm where date_start_notice >= now() - 60 minutes and <= now() + 5 minutes
        start_time = datetime.utcnow().replace(tzinfo=utc) + relativedelta(minutes=-60)
        end_time = datetime.utcnow().replace(tzinfo=utc) + relativedelta(minutes=+5)
        alarm_list = Alarm.objects.filter(date_start_notice__range=(start_time, end_time),
                                          status=ALARM_STATUS.PENDING).order_by('date_start_notice')
        # Browse all the Alarm found
        for obj_alarm in alarm_list:
            # Check if there is an existing Event
            if obj_alarm.event:
                obj_alarm.status = ALARM_STATUS.IN_PROCESS
                obj_alarm.save()

                second_towait = obj_alarm.get_time_diff()
                # If second_towait negative then set to 0 to be run directly
                if second_towait <= 0:
                    perform_alarm.delay(obj_alarm.event, obj_alarm)
                else:
                    # Call the Alarm in the future
                    perform_alarm.apply_async(
                        args=[obj_alarm.event, obj_alarm], countdown=second_towait)
            else:
                logger.error("There is no Event attached to this Alarm: %d" % obj_alarm.id)
                ## Mark the Alarm as ERROR
                obj_alarm.status = ALARM_STATUS.FAILURE
                obj_alarm.save()


@task()
def perform_alarm(obj_event, obj_alarm):
    """
    Task to perform the alarm, this will send the alarms via several mean such
    as Call, SMS and Email
    """
    logger.info("TASK :: perform_alarm -> %s" % obj_alarm.method)

    if obj_alarm.method == ALARM_METHOD.CALL:
        # send alarm via CALL
        print "perform_alarm ALARM_METHOD.CALL"
        AlarmRequest.objects.create(
            alarm=obj_alarm,
            date=datetime.utcnow().replace(tzinfo=utc)
        )

    elif obj_alarm.method == ALARM_METHOD.SMS:
        # send alarm via SMS
        print "perform_alarm ALARM_METHOD.SMS"
        # Mark the Alarm as SUCCESS
        obj_alarm.status = ALARM_STATUS.SUCCESS
        obj_alarm.save()

    elif obj_alarm.method == ALARM_METHOD.EMAIL:
        # send alarm via EMAIL
        print "perform_alarm ALARM_METHOD.EMAIL"

        if obj_alarm.alarm_email and obj_alarm.mail_template:
            # create MailSpooler object
            MailSpooler.objects.create(
                mailtemplate=obj_alarm.mail_template,
                contact_email=obj_alarm.alarm_email
            )
        # Mark the Alarm as SUCCESS
        obj_alarm.status = ALARM_STATUS.SUCCESS
        obj_alarm.save()


class alarmrequest_dispatcher(PeriodicTask):
    """A periodic task that checks for scheduled AlarmRequest and create CallRequests.

    For each AlarmRequest found, the PeriodicTask alarmrequest_dispatcher will ::

        - create new CallRequest

    **Usage**:

        alarmrequest_dispatcher.delay()
    """
    run_every = timedelta(seconds=FREQ_DISPATCHER)

    @only_one(ikey="alarmrequest_dispatcher", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.info("TASK :: alarmrequest_dispatcher")

        # Select AlarmRequest where date >= now() - 60 minutes
        start_time = datetime.utcnow().replace(tzinfo=utc) + relativedelta(minutes=-60)
        alarmreq_list = AlarmRequest.objects.filter(date__gte=start_time, status=ALARMREQUEST_STATUS.PENDING)
        no_alarmreq = alarmreq_list.count()
        if no_alarmreq == 0:
            logger.error("alarmrequest_dispatcher - no alarmreq found!")
            return False

        # Set time to wait for balanced dispatching of calls
        #time_to_wait = int(60 / DIV_MIN) / no_subscriber
        time_to_wait = 6.0 / no_alarmreq
        count = 0

        # Browse all the AlarmRequest found
        for obj_alarmreq in alarmreq_list:
            # Loop on AlarmRequest and start to the initcall's task
            count = count + 1
            second_towait = floor(count * time_to_wait)
            ms_addtowait = (count * time_to_wait) - second_towait
            logger.info("Init CallRequest for AlarmRequest in %d seconds (alarmreq:%d)" % (second_towait, obj_alarmreq.id))

            if obj_alarmreq.alarm.maxretry == 0:
                call_type = CALLREQUEST_TYPE.CANNOT_RETRY
            else:
                call_type = CALLREQUEST_TYPE.ALLOW_RETRY

            try:
                caluser_profile = CalendarUserProfile.objects.get(user=obj_alarmreq.alarm.event.creator)
            except CalendarUserProfile.DoesNotExist:
                logger.error("Error retrieving CalendarUserProfile")
                return False

            #manager_profile = UserProfile.objects.get(user=caluser_profile.manager)
            # manager_profile = caluser_profile.manager.get_profile()
            # manager_profile.dialersetting
            # Use manager_profile.dialersetting to retrieve some settings

            # TODO: build settings for this
            calltimeout = caluser_profile.calendar_setting.call_timeout
            callmaxduration = 60 * 60
            callerid = caluser_profile.calendar_setting.callerid
            caller_name = caluser_profile.calendar_setting.caller_name
            aleg_gateway = caluser_profile.calendar_setting.aleg_gateway
            content_type = ContentType.objects.get(model__in=["survey"])
            object_id = caluser_profile.calendar_setting.survey_id

            # Create Callrequest to track the call task
            new_callrequest = Callrequest(
                status=CALLREQUEST_STATUS.PENDING,
                call_type=call_type,
                call_time=datetime.utcnow().replace(tzinfo=utc),
                timeout=calltimeout,
                callerid=callerid,
                caller_name=caller_name,
                phone_number=obj_alarmreq.alarm.alarm_phonenumber,
                alarm_request_id=obj_alarmreq.id,
                aleg_gateway=aleg_gateway,
                content_type=content_type,
                object_id=object_id,
                user=caluser_profile.manager,
                extra_data='',
                timelimit=callmaxduration)
            new_callrequest.save()

            init_callrequest.apply_async(
                args=[new_callrequest.id, None, callmaxduration, ms_addtowait, obj_alarmreq.id],
                countdown=second_towait)

            obj_alarmreq.callrequest = new_callrequest
            obj_alarmreq.status = ALARMREQUEST_STATUS.IN_PROCESS
            obj_alarmreq.save()
            # Increment num_attempt
            obj_alarmreq.alarm.num_attempt = obj_alarmreq.alarm.num_attempt + 1
            obj_alarmreq.alarm.save()
