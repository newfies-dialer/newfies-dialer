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
        """Return all the campaigns which are expired or going to expire
         based on the expiry date but status is not 'END'"""
        kwargs = {}
        kwargs['expirationdate__lte'] = datetime.now()
        return Campaign.objects.filter(**kwargs).exclude(status=4)


def common_contact_authorization(user, str_contact):
    """Common Function to check contact no is authorized or not.
    For this we will check the dialer settings : whitelist and blacklist
    """
    try:
        obj_userprofile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return False

    if not obj_userprofile.dialersetting:
        return False

    whitelist = obj_userprofile.dialersetting.whitelist
    blacklist = obj_userprofile.dialersetting.blacklist

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
                                     verbose_name=_("Campaign Code"),
                                     help_text=_('This code is auto-generated by the platform, this is used to identify the campaign'),
                                     default=(lambda: get_unique_code(length=5)))
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(verbose_name=_('Description'), blank=True,
                                   null=True, help_text=_("Campaign description"))
    user = models.ForeignKey('auth.User', related_name='Campaign owner')
    status = models.IntegerField(choices=list(CAMPAIGN_STATUS),
                                 default=CAMPAIGN_STATUS.PAUSE,
                                 verbose_name=_("Status"), blank=True, null=True)
    callerid = models.CharField(max_length=80, blank=True,
                                verbose_name=_("CallerID"),
                                help_text=_("Outbound caller-ID"))
    caller_name = models.CharField(max_length=80, blank=True,
                                   verbose_name=_("Caller name"),
                                   help_text=_("Outbound caller-Name"))
    #General Starting & Stopping date
    startingdate = models.DateTimeField(default=(lambda: datetime.now()),
                                        verbose_name=_('Start'),
                                        help_text=_("Date Format: YYYY-mm-DD HH:MM:SS"),
                                        db_index=True)
    expirationdate = models.DateTimeField(default=(lambda: datetime.now() + relativedelta(days=+1)),
                                          verbose_name=_('Finish'),
                                          help_text=_("Date Format: YYYY-mm-DD HH:MM:SS"))
    #Per Day Starting & Stopping Time
    daily_start_time = models.TimeField(default='00:00:00',
                                        verbose_name=_('Daily start time'),
                                        help_text=_("Time Format: HH:MM:SS"))
    daily_stop_time = models.TimeField(default='23:59:59',
                                       verbose_name=_('Daily stop time'),
                                       help_text=_("Time Format: HH:MM:SS"))
    monday = models.BooleanField(default=True, verbose_name=_('Monday'))
    tuesday = models.BooleanField(default=True, verbose_name=_('Tuesday'))
    wednesday = models.BooleanField(default=True, verbose_name=_('Wednesday'))
    thursday = models.BooleanField(default=True, verbose_name=_('Thursday'))
    friday = models.BooleanField(default=True, verbose_name=_('Friday'))
    saturday = models.BooleanField(default=True, verbose_name=_('Saturday'))
    sunday = models.BooleanField(default=True, verbose_name=_('Sunday'))
    #Campaign Settings
    frequency = models.IntegerField(default='10', blank=True, null=True,
                                    verbose_name=_('Frequency'),
                                    help_text=_("Calls per Minute"))
    callmaxduration = models.IntegerField(default='1800', blank=True, null=True,
                                          verbose_name=_('Max Call Duration'),
                                          help_text=_("Maximum call duration in seconds"))
    #max retry on failure - Note that the answered call not completed are counted
    maxretry = models.IntegerField(default='0', blank=True, null=True,
                                   verbose_name=_('Max Retries'),
                                   help_text=_("Maximum retries per contact"))
    intervalretry = models.IntegerField(default='300', blank=True, null=True,
                                        verbose_name=_('Time between Retries'),
                                        help_text=_("Time delay in seconds before retrying contact"))
    completion_maxretry = models.IntegerField(default='0', blank=True, null=True,
                                              verbose_name=_('Completion Max Retries'),
                                              help_text=_("Amount of retries until a contact is completed"))
    completion_intervalretry = models.IntegerField(default='900', blank=True, null=True,
                                                   verbose_name=_('Completion Time between Retries'),
                                                   help_text=_("Time delay in seconds before retrying contact for completion"))
    calltimeout = models.IntegerField(default='45', blank=True, null=True,
                                      verbose_name=_('Timeout on Call'),
                                      help_text=_("Connection timeout in seconds"))
    aleg_gateway = models.ForeignKey(Gateway, verbose_name=_("A-Leg Gateway"),
                                     related_name="A-Leg Gateway",
                                     help_text=_("Select outbound gateway"))
    content_type = models.ForeignKey(ContentType, verbose_name=_("Type"),
                                     limit_choices_to={"model__in": ("survey_template",
                                                                     "voiceapp_template")})
    object_id = models.PositiveIntegerField(verbose_name=_("Application"))
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    extra_data = models.CharField(max_length=120, blank=True,
                                  verbose_name=_("Extra Parameters"),
                                  help_text=_("Additional application parameters."))
    phonebook = models.ManyToManyField(Phonebook, blank=True, null=True)
    imported_phonebook = models.CharField(max_length=500, default='', blank=True,
                                          verbose_name=_('Imported Phonebook'))
    totalcontact = models.IntegerField(default=0, blank=True, null=True,
                                       verbose_name=_('Total Contact'),
                                       help_text=_("Total Contact for this campaign"))
    completed = models.IntegerField(default=0, blank=True, null=True,
                                    verbose_name=_('Completed'),
                                    help_text=_("Total Contact that completed Call / Survey"))
    has_been_started = models.BooleanField(default=False, verbose_name=_('Has been started'))
    #Voicemail
    voicemail = models.BooleanField(default=False, verbose_name=_('Enable Voicemail Detection'))
    amd_behavior = models.IntegerField(choices=list(AMD_BEHAVIOR),
                                 default=AMD_BEHAVIOR.ALWAYS,
                                 verbose_name=_("Detection Behaviour"), blank=True, null=True)
    voicemail_audiofile = models.ForeignKey(AudioFile, null=True, blank=True,
                                  verbose_name=_("Voicemail Audio File"))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    objects = CampaignManager()

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        permissions = (
            ("view_campaign", _('Can see Campaign')),
            ("view_dashboard", _('Can see Campaign Dashboard'))
        )
        db_table = u'dialer_campaign'
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

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
    update_campaign_status.short_description = _('Action')

    def is_authorized_contact(self, str_contact):
        """Check if a contact is authorized"""
        return common_contact_authorization(self.user, str_contact)

    def get_campaign_type(self):
        """Get campaign type"""
        if self.content_type.name[0:6] == 'Survey':
            return ugettext('Survey')
        return ugettext('Voice App')

    def get_active_max_frequency(self):
        """Get the active max frequency"""
        try:
            obj_userprofile = UserProfile.objects.get(user=self.user_id)
        except UserProfile.DoesNotExist:
            return self.frequency

        max_frequency = obj_userprofile.dialersetting.max_frequency
        if max_frequency < self.frequency:
            return max_frequency

        return self.frequency

    def get_active_callmaxduration(self):
        """Get the active call max duration"""
        try:
            obj_userprofile = UserProfile.objects.get(user=self.user_id)
        except UserProfile.DoesNotExist:
            return self.frequency

        callmaxduration = obj_userprofile.dialersetting.callmaxduration
        if callmaxduration < self.callmaxduration:
            return callmaxduration

        return self.callmaxduration

    def get_active_contact(self):
        """Get all the active Contacts from the phonebook"""
        list_contact =\
            Contact.objects.filter(phonebook__campaign=self.id, status=1).all()
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
    progress_bar.short_description = _('Progress')

    def subscriber_detail(self):
        """This will link to subscribers who are associated with
        the campaign"""
        model_name = Subscriber._meta.object_name.lower()
        app_label = self._meta.app_label
        link = '/admin/%s/%s/' % (app_label, model_name)
        link += '?campaign__id=%d' % self.id
        display_link = _("<a href='%(link)s'>%(name)s</a>") % \
            {'link': link, 'name': _('Details')}
        return display_link
    subscriber_detail.allow_tags = True
    subscriber_detail.short_description = _('Subscriber')

    def get_pending_subscriber(self, limit=1000):
        """Get all the pending subscribers from the campaign"""
        list_subscriber = \
            Subscriber.objects.filter(campaign=self.id, status=1)\
            .all()[:limit]
        if not list_subscriber:
            return False
        return list_subscriber

    def get_pending_subscriber_update(self, limit=1000, status=SUBSCRIBER_STATUS.IN_PROCESS):
        """Get all the pending subscribers from the campaign"""
        list_subscriber = Subscriber.objects.select_for_update()\
            .filter(campaign=self.id, status=SUBSCRIBER_STATUS.PENDING)\
            .all()[:limit]
        if not list_subscriber:
            return False
        for elem_subscriber in list_subscriber:
            elem_subscriber.status = status
            elem_subscriber.save()
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
                                help_text=_("Select Contact"))
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                                 help_text=_("Select Campaign"))
    last_attempt = models.DateTimeField(null=True, blank=True,
                                        verbose_name=_("Last attempt"))
    count_attempt = models.IntegerField(default=0, null=True, blank=True,
                                        verbose_name=_("Count attempts"))
    #Count the amount of attempt to call in order to achieve completion
    completion_count_attempt = models.IntegerField(default=0, null=True, blank=True,
                                                   verbose_name=_("Completion Count attempts"))
    #We duplicate contact to create a unique constraint
    duplicate_contact = models.CharField(max_length=90,
                                         verbose_name=_("Contact"))
    status = models.IntegerField(choices=list(SUBSCRIBER_STATUS),
                                 default=SUBSCRIBER_STATUS.PENDING,
                                 verbose_name=_("Status"), blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'dialer_subscriber'
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")
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
