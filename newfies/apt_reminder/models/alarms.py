# -*- coding: utf-8 -*-
import pytz
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import datetime
from django.utils import timezone
from .users import Calendar_User


class Alarm(models.Model):
    '''
    This is for Alarms / Reminders on events models.
    '''
    #TODO: maybe integer ?
    daily_start = models.DateTimeField(verbose_name=_('daily start'))
    daily_stop = models.DateTimeField(verbose_name=_('daily stop'))
    advance_notice = models.IntegerField(null=True, blank=True, default=0)
    retry_count = models.IntegerField(null=True, blank=True, default=0)
    retry_delay = models.IntegerField(null=True, blank=True, default=0)
    sent_count = models.IntegerField(null=True, blank=True, default=0)
    #TODO: method should be a CHOICE
    method = models.IntegerField(null=True, blank=True, default=0)

    # TODO: Add missing fields
    # ...
    # ...
    # ...
    # ...
    # ...

    date_start_notice = models.DateTimeField(verbose_name=_('starting date'))

    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date'))

    class Meta:
        verbose_name = _('alarm')
        verbose_name_plural = _('alarms')

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

    # callrequest = models.ForeignKey(CallRequest, blank=True, null=True, verbose_name=_("Call Request"),
    #                          help_text=_("select call request"),
    #                          related_name="callrequest_alarm")

    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date'))

    class Meta:
        verbose_name = _('alarm request')
        verbose_name_plural = _('alarm requests')

    def __unicode__(self):
        return self.id
