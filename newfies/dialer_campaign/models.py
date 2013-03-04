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

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from dateutil.relativedelta import relativedelta
from dialer_campaign.constants import SUBSCRIBER_STATUS, \
    CAMPAIGN_STATUS, AMD_BEHAVIOR
from dialer_contact.constants import CONTACT_STATUS
from dialer_contact.models import Phonebook, Contact
from dialer_gateway.models import Gateway
from audiofield.models import AudioFile
from user_profile.models import UserProfile
from datetime import datetime
from common.intermediate_model_base_class import Model
from common.common_functions import get_unique_code
import logging
import re

logger = logging.getLogger('newfies.filelog')


class CampaignManager(models.Manager):
    """Campaign Manager"""

    def get_running_campaign(self):
        """Return all the active campaigns which will be running based on
        the expiry date, the daily start/stop time and days of the week"""
        kwargs = {}
        kwargs['status'] = 1
        tday = datetime.now()
        kwargs['startingdate__lte'] = datetime(tday.year, tday.month, tday.day,
                                               tday.hour, tday.minute,
                                               tday.second, tday.microsecond)
        kwargs['expirationdate__gte'] = datetime(tday.year, tday.month, tday.day,
                                                 tday.hour, tday.minute,
                                                 tday.second, tday.microsecond)

        s_time = "%s:%s:%s" % (
            str(tday.hour), str(tday.minute), str(tday.second))
        kwargs['daily_start_time__lte'] = datetime.strptime(s_time, '%H:%M:%S')
        kwargs['daily_stop_time__gte'] = datetime.strptime(s_time, '%H:%M:%S')

        # weekday status 1 - YES
        # self.model._meta.get_field(tday.strftime("%A").lower()).value()
        kwargs[tday.strftime("%A").lower()] = 1

        return Campaign.objects.filter(**kwargs)

    def get_expired_campaign(self):
        """
        Return all the campaigns which are expired or going to expire
        based on the expiry date but status is not 'END'
        """
        kwargs = {}
        kwargs['expirationdate__lte'] = datetime.now()
        return Campaign.objects.filter(**kwargs).exclude(status=CAMPAIGN_STATUS.END)


def common_contact_authorization(dialersetting, str_contact):
    """
    Common Function to check contact no is authorized or not.
    For this we will check the dialer settings : whitelist and blacklist
    """
    whitelist = dialersetting.whitelist
    blacklist = dialersetting.blacklist

    if whitelist == '*':
        whitelist = ''
    if blacklist == '*':
        blacklist = ''

    if whitelist and len(whitelist) > 0:
        try:
            result = re.search(whitelist, str_contact)
            if result:
                return True
        except ValueError:
            logger.error('Error to identify the whitelist')

    if blacklist and len(blacklist) > 0:
        try:
            result = re.search(blacklist, str_contact)
            if result:
                return False
        except ValueError:
            logger.error('Error to identify the blacklist')

    return True


class Campaign(Model):
    """This defines the Campaign

    **Attributes**:

        * ``campaign_code`` - Auto-generated campaign code to identify the campaign
        * ``name`` - Campaign name
        * ``description`` - Description about the Campaign
        * ``status`` - Campaign status
        * ``callerid`` - Caller ID
        * ``startingdate`` - Starting date of the Campaign
        * ``expirationdate`` - Expiry date of the Campaign
        * ``daily_start_time`` - Start time
        * ``daily_stop_time`` - End time
        * ``week_day_setting`` (monday, tuesday, wednesday, thursday, friday, \
        saturday, sunday)
        * ``frequency`` - Frequency, speed of the campaign. number of calls/min
        * ``callmaxduration`` - Max retry allowed per user
        * ``maxretry`` - Max retry allowed per user
        * ``intervalretry`` - Time to wait between retries in seconds
        * ``completion_maxretry`` - Amount of retries until a contact is completed
        * ``completion_intervalretry`` - Time delay in seconds before retrying \
        contact for completion
        * ``calltimeout`` - Number of seconds to timeout on calls
        * ``aleg_gateway`` - Gateway to use to reach the contact
        * ``extra_data`` - Additional data to pass to the application
        * ``totalcontact`` - Total Contact for this campaign
        * ``completed`` - Total Contact that completed Call / Survey
        * ``voicemail`` - Enable Voicemail Detection
        * ``amd_behavior`` - Detection Behaviour

    **Relationships**:

        * ``content_type`` - Defines the application (``voice_app`` or ``survey``) \
        to use when the call is established on the A-Leg

        * ``object_id`` - Defines the object of content_type application

        * ``content_object`` - Used to define the Voice App or the Survey with generic ForeignKey

        * ``phonebook`` - Many-To-Many relationship to the Phonebook model.

        * ``user`` - Foreign key relationship to the a User model. \
        Each campaign assigned to a User

        * ``voicemail_audiofile`` - Foreign key relationship to the a AudioFile model.

    **Name of DB table**: dialer_campaign
    """
    campaign_code = models.CharField(unique=True, max_length=20, blank=True,
                                     verbose_name=_("campaign code"),
                                     help_text=_('this code is auto-generated by the platform, this is used to identify the campaign'),
                                     default=(lambda: get_unique_code(length=5)))
    name = models.CharField(max_length=100, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'), blank=True,
                                   null=True, help_text=_("campaign description"))
    user = models.ForeignKey('auth.User', related_name='Campaign owner')
    status = models.IntegerField(choices=list(CAMPAIGN_STATUS),
                                 default=CAMPAIGN_STATUS.PAUSE,
                                 verbose_name=_("status"), blank=True, null=True)
    callerid = models.CharField(max_length=80, blank=True,
                                verbose_name=_("callerID"),
                                help_text=_("outbound caller-ID"))
    caller_name = models.CharField(max_length=80, blank=True,
                                   verbose_name=_("caller name"),
                                   help_text=_("outbound caller-Name"))
    #General Starting & Stopping date
    startingdate = models.DateTimeField(default=(lambda: datetime.now()),
                                        verbose_name=_('start'),
                                        help_text=_("date format: YYYY-mm-DD HH:MM:SS"))
    expirationdate = models.DateTimeField(default=(lambda: datetime.now() + relativedelta(days=+1)),
                                          verbose_name=_('finish'),
                                          help_text=_("date format: YYYY-mm-DD HH:MM:SS"))
    #Per Day Starting & Stopping Time
    daily_start_time = models.TimeField(default='00:00:00',
                                        verbose_name=_('daily start time'),
                                        help_text=_("time format: HH:MM:SS"))
    daily_stop_time = models.TimeField(default='23:59:59',
                                       verbose_name=_('daily stop time'),
                                       help_text=_("time format: HH:MM:SS"))
    monday = models.BooleanField(default=True, verbose_name=_('monday'))
    tuesday = models.BooleanField(default=True, verbose_name=_('tuesday'))
    wednesday = models.BooleanField(default=True, verbose_name=_('wednesday'))
    thursday = models.BooleanField(default=True, verbose_name=_('thursday'))
    friday = models.BooleanField(default=True, verbose_name=_('friday'))
    saturday = models.BooleanField(default=True, verbose_name=_('saturday'))
    sunday = models.BooleanField(default=True, verbose_name=_('sunday'))
    #Campaign Settings
    frequency = models.IntegerField(default='10', blank=True, null=True,
                                    verbose_name=_('frequency'),
                                    help_text=_("calls per minute"))
    callmaxduration = models.IntegerField(default='1800', blank=True, null=True,
                                          verbose_name=_('max call duration'),
                                          help_text=_("maximum call duration in seconds"))
    #max retry on failure - Note that the answered call not completed are counted
    maxretry = models.IntegerField(default='0', blank=True, null=True,
                                   verbose_name=_('max retries'),
                                   help_text=_("maximum retries per contact"))
    intervalretry = models.IntegerField(default='300', blank=True, null=True,
                                        verbose_name=_('time between Retries'),
                                        help_text=_("time delay in seconds before retrying contact"))
    completion_maxretry = models.IntegerField(default='0', blank=True, null=True,
                                              verbose_name=_('completion max retries'),
                                              help_text=_("amount of retries until a contact is completed"))
    completion_intervalretry = models.IntegerField(default='900', blank=True, null=True,
                                                   verbose_name=_('completion Time between Retries'),
                                                   help_text=_("time delay in seconds before retrying contact for completion"))
    calltimeout = models.IntegerField(default='45', blank=True, null=True,
                                      verbose_name=_('timeout on call'),
                                      help_text=_("connection timeout in seconds"))
    aleg_gateway = models.ForeignKey(Gateway, verbose_name=_("A-Leg gateway"),
                                     related_name="A-Leg Gateway",
                                     help_text=_("select outbound gateway"))
    content_type = models.ForeignKey(ContentType, verbose_name=_("type"),
                                     limit_choices_to={"model__in": ("survey_template",
                                                                     "voiceapp_template")})
    object_id = models.PositiveIntegerField(verbose_name=_("application"))
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    extra_data = models.CharField(max_length=120, blank=True,
                                  verbose_name=_("extra parameters"),
                                  help_text=_("additional application parameters."))
    phonebook = models.ManyToManyField(Phonebook, blank=True, null=True)
    imported_phonebook = models.CharField(max_length=500, default='', blank=True,
                                          verbose_name=_('imported phonebook'))
    totalcontact = models.IntegerField(default=0, blank=True, null=True,
                                       verbose_name=_('total contact'),
                                       help_text=_("total contact for this campaign"))
    completed = models.IntegerField(default=0, blank=True, null=True,
                                    verbose_name=_('completed'),
                                    help_text=_("total contact that completed call / survey"))
    has_been_started = models.BooleanField(default=False, verbose_name=_('has been started'))
    #Voicemail
    voicemail = models.BooleanField(default=False, verbose_name=_('enable voicemail detection'))
    amd_behavior = models.IntegerField(choices=list(AMD_BEHAVIOR),
                                 default=AMD_BEHAVIOR.ALWAYS,
                                 verbose_name=_("detection behaviour"), blank=True, null=True)
    voicemail_audiofile = models.ForeignKey(AudioFile, null=True, blank=True,
                                  verbose_name=_("voicemail audio file"))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
    updated_date = models.DateTimeField(auto_now=True)

    objects = CampaignManager()

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        permissions = (
            ("view_campaign", _('can see campaign')),
            ("view_dashboard", _('can see campaign dashboard'))
        )
        db_table = u'dialer_campaign'
        verbose_name = _("campaign")
        verbose_name_plural = _("campaigns")

    def update_campaign_status(self):
        """Update the campaign's status

        For example,
        If campaign is active, you can change status to 'Pause' or 'Stop'
        """
        if self.status == CAMPAIGN_STATUS.START:
            return "<a href='%s'>Pause</a> | <a href='%s'>Abort</a> | <a href='%s'>Stop</a>" % \
                (reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.PAUSE]),
                 reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.ABORT]),
                 reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.END]))

        if self.status == CAMPAIGN_STATUS.PAUSE:
            return "<a href='%s'>Start</a> | <a href='%s'>Abort</a> | <a href='%s'>Stop</a>" % \
                (reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.START]),
                 reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.ABORT]),
                 reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.END]))

        if self.status == CAMPAIGN_STATUS.ABORT:
            return "<a href='%s'>Start</a> | <a href='%s'>Pause</a> | <a href='%s'>Stop</a>" % \
                (reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.START]),
                 reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.PAUSE]),
                 reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.END]))

        if self.status == CAMPAIGN_STATUS.END:
            return "<a href='%s'>Start</a> | <a href='%s'>Pause</a> | <a href='%s'>Abort</a>" % \
                (reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.START]),
                 reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.PAUSE]),
                 reverse('dialer_campaign.views.update_campaign_status_admin',
                         args=[self.pk, CAMPAIGN_STATUS.ABORT]))
    update_campaign_status.allow_tags = True
    update_campaign_status.short_description = _('action')

    def is_authorized_contact(self, dialersetting, str_contact):
        """Check if a contact is authorized"""
        return common_contact_authorization(dialersetting, str_contact)

    def get_campaign_type(self):
        """Get campaign type"""
        if self.content_type.name[0:6] == 'Survey':
            return ugettext('survey')
        return ugettext('voice app')

    def get_active_max_frequency(self):
        """Get the active max frequency"""
        try:
            obj_userprofile = self.user.get_profile()
        except UserProfile.DoesNotExist:
            return self.frequency

        max_frequency = obj_userprofile.dialersetting.max_frequency
        if max_frequency < self.frequency:
            return max_frequency

        return self.frequency

    def get_active_callmaxduration(self):
        """Get the active call max duration"""
        try:
            obj_userprofile = self.user.get_profile()
        except UserProfile.DoesNotExist:
            return self.frequency

        callmaxduration = obj_userprofile.dialersetting.callmaxduration
        if callmaxduration < self.callmaxduration:
            return callmaxduration

        return self.callmaxduration

    def get_active_contact(self):
        """Get all the active Contacts from the phonebook"""
        list_contact =\
            Contact.objects.filter(phonebook__campaign=self.id, status=CONTACT_STATUS.ACTIVE).all()
        if not list_contact:
            return False
        return list_contact

    def progress_bar(self):
        """Progress bar generated based on no of contacts"""
        # Cache subscriber_count
        count_contact = \
            Contact.objects.filter(phonebook__campaign=self.id).count()

        # Cache need to be set per campaign
        # subscriber_count_key_campaign_id_1
        subscriber_count = cache.get(
            'subscriber_count_key_campaign_id_' + str(self.id))

        if subscriber_count is None:
            list_contact = Contact.objects.values_list('id', flat=True)\
                .filter(phonebook__campaign=self.id)

            subscriber_count = 0
            try:
                subscriber_count += Subscriber.objects\
                    .filter(contact__in=list_contact,
                            campaign=self.id,
                            status=SUBSCRIBER_STATUS.SENT)\
                    .count()
            except:
                pass

            cache.set("subscriber_count_key_campaign_id_%s"
                      % str(self.id), subscriber_count, 5)

        subscriber_count = int(subscriber_count)
        count_contact = int(count_contact)

        if count_contact > 0:
            percentage_pixel = \
                (float(subscriber_count) / count_contact) * 100
            percentage_pixel = int(percentage_pixel)
        else:
            percentage_pixel = 0
        subscriber_count_string = "subscribers (" + str(subscriber_count) + ")"
        return "<div title='%s' style='width: 100px; border: 1px solid #ccc;'><div style='height: 4px; width: %dpx; background: #555; '></div></div>" % \
            (subscriber_count_string, percentage_pixel)
    progress_bar.allow_tags = True
    progress_bar.short_description = _('progress')

    def subscriber_detail(self):
        """This will link to subscribers who are associated with
        the campaign"""
        model_name = Subscriber._meta.object_name.lower()
        app_label = self._meta.app_label
        link = '/admin/%s/%s/' % (app_label, model_name)
        link += '?campaign__id=%d' % self.id
        display_link = _("<a href='%(link)s'>%(name)s</a>") % \
            {'link': link, 'name': _('details')}
        return display_link
    subscriber_detail.allow_tags = True
    subscriber_detail.short_description = _('subscriber')

    # OPTIMIZATION - GOOD
    def get_pending_subscriber_update(self, limit, status):
        """Get all the pending subscribers from the campaign"""
        #We cannot use select_related here as it' 's not compliant with locking the rows
        list_subscriber = Subscriber.objects.select_for_update()\
            .filter(campaign=self.id, status=SUBSCRIBER_STATUS.PENDING)\
            .all()[:limit]
        if not list_subscriber:
            return False
        id_list_sb = []
        for elem_subscriber in list_subscriber:
            id_list_sb.append(elem_subscriber.id)
        #Update in bulk
        Subscriber.objects.filter(id__in=id_list_sb).update(status=status)
        return list_subscriber


class Subscriber(Model):
    """This defines the Contact imported to a Campaign

    **Attributes**:

        * ``last_attempt`` - last call attempt date
        * ``count_attempt`` - Count the amount of call attempt
        * ``completion_count_attempt`` - Count the amount of attempt to call in order to achieve completion
        * ``duplicate_contact`` - copy of the contact phonenumber
        * ``status`` - subscriber status

    **Relationships**:

        * ``contact`` - Foreign key relationship to the Contact model.
        * ``campaign`` - Foreign key relationship to the Campaign model.

    **Name of DB table**: dialer_subscriber
    """
    contact = models.ForeignKey(Contact, null=True, blank=True,
                                help_text=_("select contact"))
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                                 help_text=_("select campaign"))
    last_attempt = models.DateTimeField(null=True, blank=True,
                                        verbose_name=_("last attempt"))
    count_attempt = models.IntegerField(default=0, null=True, blank=True,
                                        verbose_name=_("count attempts"))
    #Count the amount of attempt to call in order to achieve completion
    completion_count_attempt = models.IntegerField(default=0, null=True, blank=True,
                                                   verbose_name=_("completion count attempts"))
    #We duplicate contact to create a unique constraint
    duplicate_contact = models.CharField(max_length=90,
                                         verbose_name=_("contact"))
    status = models.IntegerField(choices=list(SUBSCRIBER_STATUS),
                                 default=SUBSCRIBER_STATUS.PENDING,
                                 verbose_name=_("status"), blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'dialer_subscriber'
        verbose_name = _("subscriber")
        verbose_name_plural = _("subscribers")
        unique_together = ['contact', 'campaign']

    def __unicode__(self):
            return u"%s" % str(self.id)

    def contact_name(self):
        return self.contact.name

    # static method to perform a stored procedure
    # Ref link - http://www.chrisumbel.com/article/django_python_stored_procedures.aspx
    """
    @staticmethod
    def importcontact_pl_sql(campaign_id, phonebook_id):
        # create a cursor
        from django.db import connection
        cur = connection.cursor()

        # execute the stored procedure passing in
        # campaign_id, phonebook_id as a parameter
        cur.callproc('importcontact_pl_sql', [campaign_id, phonebook_id])

        cur.close()
        return True
    """


#Note : This will cause the running campaign to add the new contacts to the subscribers list
def post_save_add_contact(sender, **kwargs):
    """A ``post_save`` signal is sent by the Contact model instance whenever
    it is going to save.

    **Logic Description**:

        * When new contact is added into ``Contact`` model, active the
          campaign list will be checked with the contact status.
        * If the active campaign list count is more than one & the contact
          is active, the contact will be added into ``Subscriber``
          model.
    """
    obj = kwargs['instance']
    active_campaign_list = \
        Campaign.objects.filter(phonebook__contact__id=obj.id, status=CAMPAIGN_STATUS.START)
    # created instance = True + active contact + active_campaign
    if kwargs['created'] and obj.status == CONTACT_STATUS.ACTIVE \
            and active_campaign_list.count() >= 1:
        for elem_campaign in active_campaign_list:
            try:
                Subscriber.objects.create(
                    contact=obj,
                    duplicate_contact=obj.contact,
                    status=SUBSCRIBER_STATUS.PENDING,
                    campaign=elem_campaign)
            except:
                pass

post_save.connect(post_save_add_contact, sender=Contact)


def post_update_campaign_status(sender, **kwargs):
    """A ``post_save`` signal is sent by the Campaign model instance whenever
    it is going to save.

    If Campaign Status is start, perform collect_subscriber task
    """
    obj = kwargs['instance']
    #Start tasks to import subscriber
    if int(obj.status) == CAMPAIGN_STATUS.START:
        from dialer_campaign.tasks import collect_subscriber
        collect_subscriber.delay(obj.id)

post_save.connect(post_update_campaign_status, sender=Campaign)
