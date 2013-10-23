# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from appointment.constants import ALARM_METHOD, ALARM_STATUS, ALARM_RESULT
from appointment.models.events import Event
from survey.models import Survey
from dialer_cdr.models import Callrequest
from mod_mailer.models import MailTemplate


class SMSTemplate(models.Model):
    """
    This table store the SMS Template
    """
    label = models.CharField(max_length=75,
                    help_text='SMS template name')
    template_key = models.CharField(max_length=30, unique=True,
                    help_text='Unique name used to pick some template for recurring action, such as activation or warning')
    sender_phonenumber = models.EmailField(max_length=75, help_text='Sender Email')
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
    #TODO: maybe integer ?
    daily_start = models.DateTimeField(verbose_name=_('daily start'))
    daily_stop = models.DateTimeField(verbose_name=_('daily stop'))
    advance_notice = models.IntegerField(null=True, blank=True, default=0,
                                         verbose_name=_('advance notice'))
    retry_count = models.IntegerField(null=True, blank=True, default=0,
                                      verbose_name=_('retry count'))
    retry_delay = models.IntegerField(null=True, blank=True, default=0,
                                      verbose_name=_('retry delay'))
    sent_count = models.IntegerField(null=True, blank=True, default=0,
                                     verbose_name=_('sent count'))
    method = models.IntegerField(choices=list(ALARM_METHOD),
                                 default=ALARM_METHOD.CALL,
                                 verbose_name=_("method"), blank=True, null=True)

    # TODO: Add missing fields

    survey = models.ForeignKey(Survey, verbose_name=_("survey"),
                               related_name="survey")
    mail_template = models.ForeignKey(MailTemplate, verbose_name=_("mail template"),
                                     related_name="mail template")
    sms_template = models.ForeignKey(SMSTemplate, verbose_name=_("sms template"),
                                     related_name="sms template")
    event = models.ForeignKey(Event, verbose_name=_("event"),
                              related_name="event")

    date_start_notice = models.DateTimeField(verbose_name=_('starting date'))
    status = models.IntegerField(choices=list(ALARM_STATUS),
                                 default=ALARM_STATUS.PENDING,
                                 verbose_name=_("status"), blank=True, null=True)
    result = models.IntegerField(choices=list(ALARM_RESULT),
                                 verbose_name=_("method"), blank=True, null=True)
    url_cancel = models.CharField(max_length=250, blank=True, null=True,
                                verbose_name=_("URL cancel"))
    phonenumber_sms_cancel = models.CharField(max_length=50, blank=True, null=True,
                                verbose_name=_("phonenumber SMS cancel"))
    url_confirm = models.CharField(max_length=250, blank=True, null=True,
                                verbose_name=_("URL confirm"))
    phonenumber_transfer = models.CharField(max_length=50, blank=True, null=True,
                                verbose_name=_("phonenumber transfer"))

    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date'))

    class Meta:
        verbose_name = _('alarm')
        verbose_name_plural = _('alarms')
        app_label = "appointment"

    def __unicode__(self):
        return self.id


class AlarmRequest(models.Model):
    '''
    AlarmRequest : request for Alarms
    '''
    alarm = models.ForeignKey(Alarm, blank=True, null=True, verbose_name=_("alarm"),
                             help_text=_("select alarm"),
                             related_name="request_alarm")
    date = models.DateTimeField(verbose_name=_('date'))

    #TODO: method should be a CHOICE
    status = models.IntegerField(null=True, blank=True, default=0)
    callstatus = models.IntegerField(null=True, blank=True, default=0)

    calltime = models.DateTimeField(verbose_name=_('call time'))
    duration = models.IntegerField(null=True, blank=True, default=0)

    callrequest = models.ForeignKey(Callrequest, blank=True, null=True,
                                    verbose_name=_("Call Request"),
                                    help_text=_("select call request"),
                                    related_name="callrequest_alarm")

    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date'))

    class Meta:
        verbose_name = _('alarm request')
        verbose_name_plural = _('alarm requests')

    def __unicode__(self):
        return self.id
