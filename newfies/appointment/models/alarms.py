# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from appointment.constants import ALARM_METHOD, ALARM_STATUS, ALARM_RESULT, \
    ALARMREQUEST_STATUS
from appointment.models.events import Event
from survey.models import Survey
from dialer_cdr.models import Callrequest
from mod_mailer.models import MailTemplate
from datetime import datetime
from django.utils.timezone import utc
from sms_module.models import SMSTemplate


class Alarm(models.Model):
    """
    This is for Alarms / Reminders on events models.
    """
    alarm_phonenumber = models.CharField(max_length=50, blank=True, null=True,
                                         verbose_name=_("notify to phone number"))
    alarm_email = models.EmailField(blank=True, null=True,
                                    verbose_name=_('notify to email'))
    daily_start = models.TimeField(verbose_name=_('daily start'), default='00:00:00')
    daily_stop = models.TimeField(verbose_name=_('daily stop'), default='23:59:59')
    advance_notice = models.IntegerField(null=True, blank=True, default=0,
                                         verbose_name=_('advance notice'),
                                         help_text=_("Seconds to start processing an alarm before the alarm date/time"))
    maxretry = models.IntegerField(null=True, blank=True, default=0,
                                   verbose_name=_('max retry'),
                                   help_text=_("number of retries"))
    retry_delay = models.IntegerField(null=True, blank=True, default=0,
                                      verbose_name=_('retry delay'),
                                      help_text=_("Seconds to wait between retries"))
    num_attempt = models.IntegerField(null=True, blank=True, default=0,
                                     verbose_name=_('number of attempts'))
    method = models.IntegerField(choices=list(ALARM_METHOD),
                                 default=ALARM_METHOD.CALL,
                                 verbose_name=_("method"), blank=True, null=True)
    survey = models.ForeignKey(Survey, verbose_name=_("survey"),
                               blank=True, null=True,
                               related_name="survey")
    mail_template = models.ForeignKey(MailTemplate, verbose_name=_("mail"),
                                      blank=True, null=True,
                                      related_name="mail template")
    sms_template = models.ForeignKey(SMSTemplate, verbose_name=_("SMS"),
                                     blank=True, null=True,
                                     related_name="sms template")
    event = models.ForeignKey(Event, verbose_name=_("related to event"),
                              related_name="event")
    date_start_notice = models.DateTimeField(verbose_name=_('alarm date'),
                                             default=(lambda: datetime.utcnow().replace(tzinfo=utc)))
    status = models.IntegerField(choices=list(ALARM_STATUS),
                                 default=ALARM_STATUS.PENDING,
                                 verbose_name=_("status"))
    result = models.IntegerField(choices=list(ALARM_RESULT), default=ALARM_RESULT.NORESULT,
                                 verbose_name=_("result"), blank=True, null=True)
    # URL Cancel is used if an appointment is cancelled, we will need to do a mapping on IVR result
    url_cancel = models.CharField(max_length=250, blank=True, null=True,
                                  verbose_name=_("URL cancel"))
    # URL Confirm is used if an appointment is confirmed
    url_confirm = models.CharField(max_length=250, blank=True, null=True,
                                   verbose_name=_("URL confirm"))
    # When transfering for reschedule
    phonenumber_transfer = models.CharField(max_length=50, blank=True, null=True,
                                            verbose_name=_("phone number transfer"))
    #send SMS if all attempts to contact that persons didn't work
    phonenumber_sms_failure = models.CharField(max_length=50, blank=True, null=True,
                                              verbose_name=_("phone number SMS failure"))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('created date'))

    class Meta:
        permissions = (
            ("view_alarm", _('can see Alarm list')),
        )
        verbose_name = _('alarm')
        verbose_name_plural = _('alarms')
        app_label = "appointment"

    def __unicode__(self):
        if self.method:
            method = dict(ALARM_METHOD)[self.method]
            return u"%s - method:%s - %s" % (self.id, method, self.event)
        else:
            return u"%s - %s" % (self.id, self.event)

    def get_time_diff(self):
        if self.date_start_notice:
            tday = datetime.utcnow().replace(tzinfo=utc)
            timediff = self.date_start_notice - tday
            return timediff.total_seconds()

    def copy_alarm(self, new_event):
        """
        Create a copy of the Alarm
        """
        new_alarm = Alarm.objects.create(
            alarm_phonenumber=self.alarm_phonenumber,
            alarm_email=self.alarm_email,
            event=new_event,
            daily_start=self.daily_start,
            daily_stop=self.daily_stop,
            advance_notice=self.advance_notice,
            maxretry=self.maxretry,
            retry_delay=self.retry_delay,
            num_attempt=self.num_attempt,
            method=self.method,
            survey=self.survey,
            mail_template=self.mail_template,
            sms_template=self.sms_template,
            date_start_notice=self.date_start_notice,
            #result=self.result,
            url_cancel=self.url_cancel,
            phonenumber_sms_failure=self.phonenumber_sms_failure,
            url_confirm=self.url_confirm,
            phonenumber_transfer=self.phonenumber_transfer,
        )
        return new_alarm

    def retry_alarm(self):
        """
        Task to check if Alarm needs to be respooled after it failed
        """
        from appointment.tasks import perform_alarm
        # Use as follow:
        # if obj_alarmreq.alarm.maxretry >= obj_alarmreq.alarm.num_attempt:
        #     obj_alarmreq.update_status(ALARMREQUEST_STATUS.RETRY)
        #     retry_alarm(obj_alarmreq.alarm)
        #
        self.status = ALARM_STATUS.IN_PROCESS
        self.save()
        second_towait = self.retry_delay
        # If second_towait negative then set to 0 to be run directly
        if second_towait <= 0:
            perform_alarm.delay(self.event, self)
        else:
            # Call the Alarm in the future
            perform_alarm.apply_async(
                args=[self.event, self], countdown=second_towait)


class AlarmRequest(models.Model):
    """
    AlarmRequest : request for Alarms
    """
    alarm = models.ForeignKey(Alarm, blank=True, null=True, verbose_name=_("alarm"),
                              help_text=_("select alarm"),
                              related_name="request_alarm")
    date = models.DateTimeField(verbose_name=_('date'),
                                help_text=_("date when the alarm will be scheduled"))
    status = models.IntegerField(choices=list(ALARMREQUEST_STATUS),
                                 default=ALARMREQUEST_STATUS.PENDING,
                                 verbose_name=_("status"), blank=True, null=True)
    callstatus = models.IntegerField(null=True, blank=True, default=0)
    duration = models.IntegerField(null=True, blank=True, default=0)

    callrequest = models.ForeignKey(Callrequest, blank=True, null=True,
                                    verbose_name=_("Call Request"),
                                    help_text=_("select call request"),
                                    related_name="callrequest_alarm")
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date'))

    class Meta:
        permissions = (
            ("view_alarm_request", _('can see Alarm request list')),
        )
        verbose_name = _('alarm request')
        verbose_name_plural = _('alarm requests')
        app_label = "appointment"

    def update_status(self, status):
        self.status = status
        self.save()
        if status != ALARMREQUEST_STATUS.PENDING:
            self.alarm.status = self.status
            self.alarm.save()

    def __unicode__(self):
        return u"%s" % (self.id)
