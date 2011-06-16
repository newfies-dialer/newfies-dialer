from django.db import models
from django.utils.translation import ugettext as _
from datetime import *
from dialer_gateway.models import Gateway
from voip_app.models import VoipApp
from common.intermediate_model_base_class import Model
from prefix_country.models import Prefix


CALLREQUEST_STATUS = (
    (1, u'PENDING'),
    (2, u'FAILURE'),
    (3, u'RETRY'), # spawn for retry
    (4, u'SUCCESS'),
    (5, u'ABORT'),
    (6, u'PAUSE'),
    (7, u'PROCESS'),
)

CALLREQUEST_TYPE = (
    (1, u'ORIGINAL'),
    (2, u'RETRY'),
)

VOIPCALL_DISPOSITION = (
    (1, _('ANSWER')),
    (2, _('BUSY')),
    (3, _('NOANSWER')),
    (4, _('CANCEL')),
    (5, _('CONGESTION')),
    (6, _('CHANUNAVAIL')),
    (7, _('DONTCALL')),
    (8, _('TORTURE')),
    (9, _('INVALIDARGS')),
    (20, _('NOROUTE')),
    (30, _('FORBIDDEN')),
)


class CallRequestManager(models.Manager):
    """CallRequest Manager"""

    def get_pending_callrequest(self):
        """Return all the pending callrequest based on call time and status"""
        kwargs = {}
        kwargs['status'] = 1
        tday = datetime.now()
        kwargs['startingdate__lte'] = datetime(tday.year, tday.month,
            tday.day, tday.hour, tday.minute, tday.second, tday.microsecond)
        kwargs['expirationdate__gte'] = datetime(tday.year, tday.month,
            tday.day, tday.hour, tday.minute, tday.second, tday.microsecond)

        s_time = str(tday.hour) + ":" + str(tday.minute) + ":"\
                 + str(tday.second)
        kwargs['daily_start_time__lte'] = datetime.strptime(s_time, '%H:%M:%S')
        kwargs['daily_stop_time__gte'] = datetime.strptime(s_time, '%H:%M:%S')

        #return Campaign.objects.filter(**kwargs)
        return Callrequest.objects.all()

    
class Callrequest(Model):
    """This defines the call request, the dialer will read those new request
    and attempt to deliver the call

    **Attributes**:

        * ``request_uuid`` -
        * ``call_time`` -
        * ``call_type`` -
        * ``status`` -
        * ``subscriber`` -
        * ``campaign`` -
        * ``extra_data`` -
        * ``last_attempt_time`` -
        * ``result`` -
        * ``context`` -
        * ``timeout`` -
        * ``callerid`` -
        * ``variable`` -
        * ``account`` -
        * ``parent_callrequest`` -
        * ``hangup_cause`` -


    Relationships:

        * ``voipapp`` - Foreign key relationship to the VoipApp model.
                        VoIP Application to use with this campaign

        * ``aleg_gateway`` - Foreign key relationship to the Gateway model.
                             Gateway to use to reach the subscriber

    **Name of DB table**: dialer_callrequest
    """
    from uuid import uuid1

    request_uuid = models.CharField(verbose_name=_("RequestUUID"),
                        default=uuid1(), db_index=True,
                        max_length=120, null=True, blank=True)
    call_time = models.DateTimeField(default=(lambda:datetime.now()))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)
    call_type = models.IntegerField(choices=CALLREQUEST_TYPE, default='1',
                verbose_name=_("Call Request Type"), blank=True, null=True)
    status = models.IntegerField(choices=CALLREQUEST_STATUS, default='1',
                blank=True, null=True)

    callerid = models.CharField(max_length=80, blank=True)
    phone_number = models.CharField(max_length=80, blank=True)
    timeout = models.IntegerField(blank=True, default=30)
    timelimit = models.IntegerField(blank=True, default=3600)
    extra_dial_string = models.CharField(max_length=500, blank=True)

    subscriber = models.IntegerField(null=True, blank=True,
                 verbose_name="Campaign Subscriber", help_text=_("Campaign \
                 Subscriber related to this callrequest"))
    campaign = models.IntegerField(null=True, blank=True,
                                help_text=_("Select Campaign"))
    aleg_gateway = models.ForeignKey(Gateway, null=True, blank=True,
                verbose_name="A-Leg Gateway",
                help_text=_("Select Gateway to use to reach the subscriber"))
    voipapp = models.ForeignKey(VoipApp, null=True, blank=True,
                verbose_name="VoIP Application", help_text=_("Select VoIP \
                Application to use with this campaign"))
    extra_data = models.CharField(max_length=120, blank=True,
                verbose_name=_("Extra Data"), help_text=_("Define the \
                additional data to pass to the application"))

    num_attempt = models.IntegerField(default=0)
    last_attempt_time = models.DateTimeField(null=True, blank=True)
    result = models.CharField(max_length=180, blank=True)
    hangup_cause = models.CharField(max_length=80, blank=True)

    # if the call fail, create a new pending instance and link them
    parent_callrequest = models.ForeignKey('self', null=True, blank=True)

    objects = CallRequestManager()

    class Meta:
        db_table = u'dialer_callrequest'
        verbose_name = _("Call Request")
        verbose_name_plural = _("Call Requests")

    def __unicode__(self):
            return u"%s [%s]" % (self.id, self.request_uuid)


class VoIPCall(models.Model):
    """This gives information of all the calls made with
    the carrier charges and revenue of each call.

    **Attributes**:

        * ``callid`` - callid.
        * ``uniqueid`` -
        * ``callerid`` -
        * ``dnid`` -
        * ``recipient_number`` -
        * ``recipient_dialcode`` -
        * ``nasipaddress`` -
        * ``starting_date`` -
        * ``sessiontime`` -
        * ``sessiontime_real`` -
        * ``disposition`` -

    Relationships:

        * ``user`` - Foreign key relationship to the User model.
        * ``used_gateway`` - Foreign key relationship to the Gateway model.
        * ``callrequest`` - Foreign key relationship to the Callrequest model.

    **Name of DB table**: dialer_cdr
    """
    user = models.ForeignKey('auth.User', related_name='Call Sender')
    used_gateway = models.ForeignKey(Gateway, null=True, blank=True)
    callrequest = models.ForeignKey(Callrequest, null=True, blank=True)
    callid = models.CharField(max_length=120, help_text=_("VoIP Call-ID"))
    uniqueid = models.CharField(max_length=90,
                               help_text=_("UniqueID from VoIP server"))
    callerid = models.CharField(max_length=120, verbose_name='CallerID')
    dnid = models.CharField(max_length=120, verbose_name='DNID')
    recipient_number = models.CharField(max_length=32,
                    help_text=_(u'The international number of the \
                    recipient, without the leading +'), null=True, blank=True)
    recipient_dialcode = models.ForeignKey(Prefix, db_column="prefix",
                               verbose_name="Destination", null=True,
                               blank=True, help_text=_("Select Prefix"))
    nasipaddress = models.CharField(max_length=90)
    starting_date = models.DateTimeField(auto_now_add=True)
    sessiontime = models.IntegerField(null=True, blank=True)
    sessiontime_real = models.IntegerField(null=True, blank=True)

    disposition = models.IntegerField(null=True, blank=True,
                        choices=VOIPCALL_DISPOSITION)

    def destination_name(self):
        """Return Recipient dialcode"""
        if self.recipient_dialcode is None:
            return "0"
        else:
            return self.recipient_dialcode.name

    def duration(self):
        """Return duration in min & sec"""
        min = int(self.sessiontime_real / 60)
        sec = int(self.sessiontime_real % 60)
        return "%02d" % min + ":" + "%02d" % sec

    class Meta:
        db_table = 'dialer_cdr'
        verbose_name = _("VoIP Call")
        verbose_name_plural = _("VoIP Call")

    def __unicode__(self):
            return u"%s" % self.callid
