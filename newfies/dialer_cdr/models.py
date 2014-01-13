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

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from dialer_gateway.models import Gateway
from dialer_campaign.models import Campaign, Subscriber
from dialer_cdr.constants import CALLREQUEST_STATUS,\
    CALLREQUEST_TYPE, LEG_TYPE, VOIPCALL_DISPOSITION,\
    VOIPCALL_AMD_STATUS
from common.intermediate_model_base_class import Model
from country_dialcode.models import Prefix
from datetime import datetime
from django.utils.timezone import utc
from uuid import uuid1


class CallRequestManager(models.Manager):
    """CallRequest Manager"""

    def get_pending_callrequest(self):
        """Return all the pending callrequest based on call time and status"""
        kwargs = {}
        kwargs['status'] = 1
        tday = datetime.utcnow().replace(tzinfo=utc)
        kwargs['call_time__lte'] = datetime(tday.year, tday.month,
            tday.day, tday.hour, tday.minute, tday.second, tday.microsecond).replace(tzinfo=utc)

        #return Callrequest.objects.all()
        return Callrequest.objects.filter(**kwargs)


def str_uuid1():
    return str(uuid1())


class Callrequest(Model):
    """This defines the call request, the dialer will read any new request
    and attempt to deliver the call.

    **Attributes**:

        * ``request_uuid`` - Unique id
        * ``call_time`` - Total call time
        * ``call_type`` - Call type
        * ``status`` - Call request status
        * ``callerid`` - Caller ID
        * ``last_attempt_time`` -
        * ``result`` --
        * ``timeout`` -
        * ``timelimit`` -
        * ``extra_dial_string`` -
        * ``phone_number`` -
        * ``parent_callrequest`` -
        * ``extra_data`` -
        * ``num_attempt`` -
        * ``hangup_cause`` -


    **Relationships**:

        * ``user`` - Foreign key relationship to the User model. Each campaign assigned to a User

        * ``content_type`` - Defines the application  (``voip_app`` or ``survey``) \
        to use when the call is established on the A-Leg

        * ``object_id`` - Defines the object of content_type application

        * ``content_object`` - Used to define the VoIP App or the Survey with \
        generic ForeignKey

        * ``aleg_gateway`` - Foreign key relationship to the Gateway model.\
        Gateway to use to call the subscriber

        * ``subscriber`` - Foreign key relationship to the Subscriber Model.

        * ``campaign`` - Foreign key relationship to the Campaign model.

    **Name of DB table**: dialer_callrequest
    """
    user = models.ForeignKey('auth.User')
    request_uuid = models.CharField(verbose_name=_("RequestUUID"),
                                    default=str_uuid1(), db_index=True,
                                    max_length=120, null=True, blank=True)
    aleg_uuid = models.CharField(max_length=120, help_text=_("a-leg call-ID"),
                                 null=True, blank=True)
    call_time = models.DateTimeField(default=(lambda: datetime.utcnow().replace(tzinfo=utc)))
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date'))
    updated_date = models.DateTimeField(auto_now=True)
    call_type = models.IntegerField(choices=list(CALLREQUEST_TYPE),
                                    default=CALLREQUEST_TYPE.ALLOW_RETRY,
                                    verbose_name=_("call request type"),
                                    blank=True, null=True)
    status = models.IntegerField(choices=list(CALLREQUEST_STATUS),
                                 default=CALLREQUEST_STATUS.PENDING,
                                 blank=True, null=True, db_index=True,
                                 verbose_name=_('status'))
    callerid = models.CharField(max_length=80, blank=True,
                                verbose_name=_("Caller ID Number"),
                                help_text=_("outbound Caller ID"))
    caller_name = models.CharField(max_length=80, blank=True,
                                   verbose_name=_("caller name"),
                                   help_text=_("outbound caller-Name"))
    phone_number = models.CharField(max_length=80,
                                    verbose_name=_('phone number'))
    timeout = models.IntegerField(blank=True, default=30,
                                  verbose_name=_('time out'))
    timelimit = models.IntegerField(blank=True, default=3600,
                                    verbose_name=_('time limit'))
    extra_dial_string = models.CharField(max_length=500, blank=True,
                                         verbose_name=_('extra dial string'))

    subscriber = models.ForeignKey(Subscriber, null=True, blank=True,
                                   help_text=_("subscriber related to this call request"))

    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                                 help_text=_("select Campaign"))
    aleg_gateway = models.ForeignKey(Gateway, null=True, blank=True,
                                     verbose_name=_("a-leg gateway"),
                                     help_text=_("select gateway"))
    #used to define the Voice App or the Survey
    content_type = models.ForeignKey(ContentType, verbose_name=_("type"))
    object_id = models.PositiveIntegerField(verbose_name=_("application"))
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    #used to flag if the call is completed
    completed = models.BooleanField(default=False, verbose_name=_('call completed'))

    extra_data = models.CharField(max_length=120, blank=True,
                                  verbose_name=_("extra data"),
                                  help_text=_("define the additional data to pass to the application"))

    num_attempt = models.IntegerField(default=0)
    last_attempt_time = models.DateTimeField(null=True, blank=True)
    result = models.CharField(max_length=180, blank=True)
    hangup_cause = models.CharField(max_length=80, blank=True)

    # if the call fails, create a new pending instance and link them
    parent_callrequest = models.ForeignKey('self', null=True, blank=True)

    #AlarmRequest call / if this value is set then this is not a campaign call
    alarm_request_id = models.IntegerField(default=0, null=True, blank=True,
                                           verbose_name=_('alarm request id'))

    objects = CallRequestManager()

    class Meta:
        db_table = u'dialer_callrequest'
        verbose_name = _("call request")
        verbose_name_plural = _("call requests")

    def __unicode__(self):
        return u"%s [%s]" % (self.id, self.request_uuid)


class VoIPCall(models.Model):
    """This gives information of all the calls made with
    the carrier charges and revenue of each call.

    **Attributes**:

        * ``callid`` - callid of the phonecall
        * ``callerid`` - CallerID used to call out
        * ``phone_number`` - Phone number contacted
        * ``dialcode`` - Dialcode of the phonenumber
        * ``starting_date`` - Starting date of the call
        * ``duration`` - Duration of the call
        * ``billsec`` -
        * ``progresssec`` -
        * ``answersec`` -
        * ``waitsec`` -
        * ``disposition`` - Disposition of the call
        * ``hangup_cause`` -
        * ``hangup_cause_q850`` -

    **Relationships**:

        * ``user`` - Foreign key relationship to the User model.
        * ``used_gateway`` - Foreign key relationship to the Gateway model.
        * ``callrequest`` - Foreign key relationship to the Callrequest model.

    **Name of DB table**: dialer_cdr
    """
    user = models.ForeignKey('auth.User', related_name='Call Sender')
    request_uuid = models.CharField(verbose_name=_("RequestUUID"), null=True, blank=True,
                                    default=str_uuid1(), max_length=120)
    used_gateway = models.ForeignKey(Gateway, null=True, blank=True,
                                     verbose_name=_("used gateway"))
    callrequest = models.ForeignKey(Callrequest, null=True, blank=True,
                                    verbose_name=_("callrequest"))
    callid = models.CharField(max_length=120, help_text=_("VoIP call-ID"))
    callerid = models.CharField(max_length=120, verbose_name=_('CallerID'))
    phone_number = models.CharField(max_length=120, null=True, blank=True,
                                    verbose_name=_("phone number"),
                                    help_text=_(u'the international number of the recipient, without the leading +'))

    dialcode = models.ForeignKey(Prefix, verbose_name=_("destination"),
                                 null=True, blank=True, help_text=_("select prefix"))
    starting_date = models.DateTimeField(auto_now_add=True,
                                         verbose_name=_("starting date"),
                                         db_index=True)
    duration = models.IntegerField(null=True, blank=True, verbose_name=_("duration"))
    billsec = models.IntegerField(null=True, blank=True, verbose_name=_("bill sec"))
    progresssec = models.IntegerField(null=True, blank=True, verbose_name=_("progress sec"))
    answersec = models.IntegerField(null=True, blank=True, verbose_name=_("answer sec"))
    waitsec = models.IntegerField(null=True, blank=True, verbose_name=_("wait sec"))
    disposition = models.CharField(choices=VOIPCALL_DISPOSITION, null=True, blank=True,
                                   max_length=40, verbose_name=_("disposition"))
    hangup_cause = models.CharField(max_length=40, null=True, blank=True,
                                    verbose_name=_("hangup cause"))
    hangup_cause_q850 = models.CharField(max_length=10, null=True, blank=True)
    leg_type = models.SmallIntegerField(choices=list(LEG_TYPE), default=LEG_TYPE.A_LEG,
                                        verbose_name=_("leg"), null=True, blank=True)
    amd_status = models.SmallIntegerField(choices=list(VOIPCALL_AMD_STATUS), default=VOIPCALL_AMD_STATUS.PERSON,
                                          null=True, blank=True, verbose_name=_("AMD Status"))

    def destination_name(self):
        """Return Recipient dialcode"""
        if self.dialcode is None:
            return "0"
        else:
            return self.dialcode.name

    def min_duration(self):
        """Return duration in min & sec"""
        if self.duration:
            min = int(self.duration / 60)
            sec = int(self.duration % 60)
            return "%02d:%02d" % (min, sec)
        else:
            return "00:00"

    class Meta:
        permissions = (
            ("view_call_detail_report", _('can see call detail report')),
        )
        db_table = 'dialer_cdr'
        verbose_name = _("VoIP call")
        verbose_name_plural = _("VoIP calls")

    def __unicode__(self):
        return u"%d - %s" % (self.id, self.callid)
