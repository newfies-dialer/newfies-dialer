# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from appointment.constants import ALARM_METHOD, ALARM_STATUS, ALARM_RESULT, \
    ALARMREQUEST_STATUS
from appointment.models.events import Event
from survey.models import Survey
from dialer_cdr.models import Callrequest
from mod_mailer.models import MailTemplate
from datetime import datetime
from django.utils.timezone import utc


class SMSTemplate(models.Model):
    """
    This table store the SMS Template
    """
    label = models.CharField(max_length=75, help_text=_('SMS template name'))
    template_key = models.CharField(max_length=30, unique=True,
                                    help_text=_('Unique name used to pick some template for recurring action, such as activation or warning'))
    sender_phonenumber = models.CharField(max_length=75)
    sms_text = models.TextField(max_length=500)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('SMS template')
        verbose_name_plural = _('SMS templates')
        app_label = "appointment"

    def __unicode__(self):
        return force_unicode(self.template_key)


class Alarm(models.Model):
    '''
    This is for Alarms / Reminders on events models.
    '''
    alarm_phonenumber = models.CharField(max_length=50, blank=True, null=True,
                                         verbose_name=_("alarm phonenumber"))
    alarm_email = models.EmailField(blank=True, null=True, verbose_name=_('alarm email'))

    daily_start = models.TimeField(verbose_name=_('daily start'), default='00:00:00',
                                   help_text=_("time format: HH:MM:SS"))
    daily_stop = models.TimeField(verbose_name=_('daily stop'), default='23:59:59',
                                  help_text=_("time format: HH:MM:SS"))
    advance_notice = models.IntegerField(null=True, blank=True, default=0,
                                         verbose_name=_('advance notice'))
    maxretry = models.IntegerField(null=True, blank=True, default=0,
                                   verbose_name=_('max retry'))
    retry_delay = models.IntegerField(null=True, blank=True, default=0,
                                      verbose_name=_('retry delay'))
    num_attempt = models.IntegerField(null=True, blank=True, default=0,
                                     verbose_name=_('number of attempts'))
    method = models.IntegerField(choices=list(ALARM_METHOD),
                                 default=ALARM_METHOD.CALL,
                                 verbose_name=_("method"), blank=True, null=True)

    survey = models.ForeignKey(Survey, verbose_name=_("survey"),
                               blank=True, null=True,
                               related_name="survey")
    mail_template = models.ForeignKey(MailTemplate, verbose_name=_("mail template"),
                                      blank=True, null=True,
                                      related_name="mail template")
    sms_template = models.ForeignKey(SMSTemplate, verbose_name=_("sms template"),
                                     blank=True, null=True,
                                     related_name="sms template")
    event = models.ForeignKey(Event, verbose_name=_("event"),
                              related_name="event")
    date_start_notice = models.DateTimeField(verbose_name=_('alarm date'),
                                             default=(lambda: datetime.now()))

    status = models.IntegerField(choices=list(ALARM_STATUS),
                                 default=ALARM_STATUS.PENDING,
                                 verbose_name=_("status"))
    result = models.IntegerField(choices=list(ALARM_RESULT),
                                 verbose_name=_("result"), blank=True, null=True)
    url_cancel = models.CharField(max_length=250, blank=True, null=True,
                                  verbose_name=_("URL cancel"))
    phonenumber_sms_cancel = models.CharField(max_length=50, blank=True, null=True,
                                              verbose_name=_("phonenumber SMS cancel"))
    url_confirm = models.CharField(max_length=250, blank=True, null=True,
                                   verbose_name=_("URL confirm"))
    phonenumber_transfer = models.CharField(max_length=50, blank=True, null=True,
                                            verbose_name=_("phonenumber transfer"))

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
            now = datetime.utcnow().replace(tzinfo=utc)
            timediff = self.date_start_notice - now
            return timediff.total_seconds()

    def copy_alarm(self, new_event):
        """
        copy alarm
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
            #url_cancel=self.url_cancel,
            #phonenumber_sms_cancel=self.phonenumber_sms_cancel,
            #url_confirm=self.url_confirm,
            #phonenumber_transfer=self.phonenumber_transfer,
        )

        return new_alarm


class AlarmRequest(models.Model):
    '''
    AlarmRequest : request for Alarms
    '''
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

    def __unicode__(self):
        return u"%s" % (self.id)
