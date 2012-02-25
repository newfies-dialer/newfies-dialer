#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public 
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
# 
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from dateutil.relativedelta import *
from django_countries import CountryField
from dialer_gateway.models import Gateway
from voice_app.models import VoiceApp
from user_profile.models import UserProfile
from datetime import datetime, timedelta
from common.intermediate_model_base_class import Model
from random import *


CONTACT_STATUS = (
    (1, _('ACTIVE')),
    (0, _('INACTIVE')),
)

CAMPAIGN_SUBSCRIBER_STATUS = (
    (1, u'PENDING'),
    (2, u'PAUSE'),
    (3, u'ABORT'),
    (4, u'FAIL'),
    (5, u'COMPLETE'),
    (6, u'IN PROCESS'),
    (7, u'NOT AUTHORIZED'),
)

CAMPAIGN_STATUS = (
    (1, u'START'),
    (2, u'PAUSE'),
    (3, u'ABORT'),
    (4, u'END'),
)

CAMPAIGN_STATUS_COLOR = { 1: "green", 2: "blue", 3: "orange", 4: "red" }

DAY_STATUS = (
    (1, _('YES')),
    (0, _('NO')),
)


def get_unique_code(length):
    """Get unique code"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join([choice(chars) for i in range(length)])


class Phonebook(Model):
    """This defines the Phonebook

    **Attributes**:

        * ``name`` - phonebook name.
        * ``description`` - description about the phonebook.

    **Relationships**:

        * ``user`` - Foreign key relationship to the User model.\
        Each phonebook is assigned to a User

    **Name of DB table**: dialer_phonebook
    """
    name = models.CharField(unique=True, max_length=90, verbose_name=_('Name'))
    description = models.TextField(null=True, blank=True,
                  help_text=_("Phonebook Notes"))
    user = models.ForeignKey('auth.User', related_name='Phonebook owner')
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('Date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'dialer_phonebook'
        verbose_name = _("Phonebook")
        verbose_name_plural = _("Phonebooks")

    def __unicode__(self):
            return u"%s" % self.name

    def phonebook_contacts(self):
        """This will return a count of the contacts in the phonebook"""
        return Contact.objects.filter(phonebook=self.id).count()
    phonebook_contacts.allow_tags = True
    phonebook_contacts.short_description = _('Contacts')


class Contact(Model):
    """This defines the Contact

    **Attributes**:

        * ``contact`` - Contact no
        * ``last_name`` - Contact's last name
        * ``first_name`` - Contact's first name
        * ``email`` - Contact's e-mail address
        * ``city`` - city name
        * ``description`` - description about a Contact
        * ``status`` - contact status
        * ``additional_vars`` - Additional variables

    **Relationships**:

        * ``phonebook`` - Foreign key relationship to the Phonebook model.\
        Each contact mapped with a phonebook
        * ``country`` - Foreign key relationship to the Country model.\
        Each contact mapped with a country

    **Name of DB table**: dialer_contact
    """
    phonebook = models.ForeignKey(Phonebook, verbose_name=_('Phonebook'),
                                help_text=_("Select Phonebook"))
    contact = models.CharField(max_length=90, verbose_name=_('Contact Number'))
    last_name = models.CharField(max_length=120, blank=True, null=True,
                                 verbose_name=_('Last Name'))
    first_name = models.CharField(max_length=120, blank=True, null=True,
                                  verbose_name=_('First Name'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('Email'))
    country = CountryField(blank=True, null=True, verbose_name=_('Country'))
    city = models.CharField(max_length=120, blank=True, null=True,
                            verbose_name=_('City'))
    description = models.TextField(null=True, blank=True,
                  help_text=_("Contact Notes"))
    status = models.IntegerField(choices=CONTACT_STATUS, default='1',
                verbose_name=_("Status"), blank=True, null=True)
    additional_vars = models.CharField(max_length=100, blank=True,
                      verbose_name=_('Additional parameters'))
    created_date = models.DateTimeField(auto_now_add=True,
                   verbose_name=_('Date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'dialer_contact'
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
        unique_together = ['contact', 'phonebook']

    def __unicode__(self):
        return u"%s (%s)" % (self.contact, self.last_name)

    def contact_name(self):
        """Return Contact Name"""
        return u"%s %s" % (self.first_name, self.last_name)
    contact_name.allow_tags = True
    contact_name.short_description = _('Name')


class CampaignManager(models.Manager):
    """Campaign Manager"""

    def get_running_campaign(self):
        """Return all the active campaigns which will be running based on
        the expiry date, the daily start/stop time and days of the week"""
        kwargs = {}
        kwargs['status'] = 1
        tday = datetime.now()
        kwargs['startingdate__lte'] = datetime(tday.year, tday.month,
            tday.day, tday.hour, tday.minute, tday.second, tday.microsecond)
        kwargs['expirationdate__gte'] = datetime(tday.year, tday.month,
            tday.day, tday.hour, tday.minute, tday.second, tday.microsecond)

        s_time = str(tday.hour) + ":" + str(tday.minute) + ":" + str(tday.second)
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

    import re

    if whitelist and len(whitelist) > 0:
        try:
            result = re.search(whitelist, str_contact)
            if result:
                return True
        except ValueError:
            print _("Error to identify the whitelist")

    if blacklist and len(blacklist) > 0:
        try:
            result = re.search(blacklist, str_contact)
            if result:
                return False
        except ValueError:
            print _("Error to identify the blacklist")
    
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
        * ``calltimeout`` - Number of seconds to timeout on calls
        * ``aleg_gateway`` - Gateway to use to reach the contact
        * ``extra_data`` - Additional data to pass to the application

    **Relationships**:

        * ``content_type`` - Defines the application (``voice_app`` or ``survey``) \
        to use when the call is established on the A-Leg

        * ``object_id`` - Defines the object of content_type application

        * ``content_object`` - Used to define the Voice App or the Survey with generic ForeignKey

        * ``phonebook`` - Many-To-Many relationship to the Phonebook model.

        * ``user`` - Foreign key relationship to the a User model. \
        Each campaign assigned to a User

    **Name of DB table**: dialer_campaign
    """
    campaign_code = models.CharField(unique=True, max_length=20, blank=True,
                    verbose_name=_("Campaign Code"),
    help_text=_('This code is auto-generated by the platform, this is used to identify the campaign'),
                    default=(lambda:get_unique_code(length=5)))

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(verbose_name=_('Description'), blank=True,
                  null=True, help_text=_("Campaign description"))
    user = models.ForeignKey('auth.User', related_name='Campaign owner')
    status = models.IntegerField(choices=CAMPAIGN_STATUS, default='2',
                verbose_name=_("Status"), blank=True, null=True)
    callerid = models.CharField(max_length=80, blank=True,
                verbose_name=_("CallerID"),
                help_text=_("Outbound caller-ID"))
    #General Starting & Stopping date
    startingdate = models.DateTimeField(default=(lambda:datetime.now()),
                   verbose_name=_('Start'),
                   help_text =_("Date Format: YYYY-mm-DD HH:MM:SS"))

    expirationdate = models.DateTimeField(                        
                     default=(lambda:datetime.now()+relativedelta(months=+1)),
                     verbose_name=_('Finish'),
                     help_text=_("Date Format: YYYY-mm-DD HH:MM:SS"))
    #Per Day Starting & Stopping Time
    daily_start_time = models.TimeField(default='00:00:00',
                       help_text=_("Time Format: HH:MM:SS"))
    daily_stop_time = models.TimeField(default='23:59:59',
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

    callmaxduration = models.IntegerField(default='1800', blank=True,
                        null=True, verbose_name=_('Max Call Duration'),
                        help_text=_("Maximum call duration in seconds"))

    maxretry = models.IntegerField(default='0', blank=True, null=True,
               verbose_name=_('Max Retries'),
               help_text=_("Maximum retries per contact"))
    intervalretry = models.IntegerField(default='300', blank=True, null=True,
                    verbose_name=_('Time between Retries'),
    help_text=_("Time delay in seconds before retrying contact"))

    calltimeout = models.IntegerField(default='45', blank=True, null=True,
                    verbose_name=_('Timeout on Call'),
                    help_text=_("Connection timeout in seconds"))
    #Gateways
    aleg_gateway = models.ForeignKey(Gateway, verbose_name=_("A-Leg Gateway"),
                    related_name="A-Leg Gateway", 
                    help_text=_("Select outbound gateway"))
    content_type = models.ForeignKey(ContentType, verbose_name=_("Type"),
                   limit_choices_to = {"model__in": ("surveyapp", "voiceapp")})
    object_id = models.PositiveIntegerField(verbose_name=_("Application"))
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    extra_data = models.CharField(max_length=120, blank=True,
                verbose_name=_("Extra Parameters"),
                help_text=_("Additional application parameters."))

    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    phonebook = models.ManyToManyField(Phonebook, blank=True, null=True)

    objects = CampaignManager()

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        db_table = u'dialer_campaign'
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

    def update_campaign_status(self):
        """Update the campaign's status

        For example,
        If campaign is active, you can change status to 'Pause' or 'Stop'
        """
        # active - 1 | pause - 2 | abort - 3 | stop - 4
        if self.status == 1:
            return "<a href='%s'>Pause</a> | <a href='%s'>Abort</a> \
            | <a href='%s'>Stop</a>" % \
            (reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 2]),
             reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 3]),
             reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 4]))

        if self.status == 2:
            return "<a href='%s'>Start</a> | <a href='%s'>Abort</a> |\
             <a href='%s'>Stop</a>" % \
            (reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 1]),
             reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 3]),
             reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 4]))

        if self.status == 3:
            return "<a href='%s'>Start</a> | <a href='%s'>Pause</a> |\
             <a href='%s'>Stop</a>" % \
            (reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 1]),
             reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 2]),
             reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 4]))

        if self.status == 4:
            return "<a href='%s'>Start</a> | <a href='%s'>Pause</a> \
            | <a href='%s'>Abort</a>" % \
            (reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 1]),
             reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 2]),
             reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 3]))
    update_campaign_status.allow_tags = True
    update_campaign_status.short_description = _('Action')

    def count_contact_of_phonebook(self, status=None):
        """Count the no. of Contacts in a phonebook"""
        if status and status == 1:
            count_contact = \
            Contact.objects.filter(status=1,
                                   phonebook__campaign=self.id).count()
        else:
            count_contact = \
            Contact.objects.filter(phonebook__campaign=self.id).count()
        if not count_contact:
            return _("Phonebook Empty")

        return count_contact
    count_contact_of_phonebook.allow_tags = True
    count_contact_of_phonebook.short_description = _('Contact')

    def is_authorized_contact(self, str_contact):
        """Check if a contact is authorized"""
        return common_contact_authorization(self.user, str_contact)


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

    def get_active_contact_no_subscriber(self):
        """List of active contacts that do not exist in Campaign Subscriber"""
        # The list of active contacts that doesn't
        # exist in CampaignSubscriber
        query = \
        'SELECT dc.id, dc.phonebook_id, dc.contact, dc.last_name, \
        dc.first_name, dc.email, dc.city, dc.description, \
        dc.status, dc.additional_vars, dc.created_date, dc.updated_date \
        FROM dialer_contact as dc \
        INNER JOIN dialer_phonebook ON \
        (dc.phonebook_id = dialer_phonebook.id) \
        INNER JOIN dialer_campaign_phonebook ON \
        (dialer_phonebook.id = dialer_campaign_phonebook.phonebook_id) \
        WHERE dialer_campaign_phonebook.campaign_id = %s \
        AND dc.status = 1 \
        AND dc.id NOT IN \
        (SELECT  dialer_campaign_subscriber.contact_id \
        FROM dialer_campaign_subscriber \
        WHERE dialer_campaign_subscriber.campaign_id = %s)' % \
        (str(self.id), str(self.id),)

        raw_contact_list = Contact.objects.raw(query)
        return raw_contact_list

    def progress_bar(self):
        """Progress bar generated based on no of contacts"""
        # Cache campaignsubscriber_count
        count_contact = \
        Contact.objects.filter(phonebook__campaign=self.id).count()

        # Cache need to be set per campaign
        # campaignsubscriber_count_key_campaign_id_1
        campaignsubscriber_count = \
        cache.get('campaignsubscriber_count_key_campaign_id_' + str(self.id))
        #campaignsubscriber_count = None
        if campaignsubscriber_count is None:
            list_contact = \
            Contact.objects.filter(phonebook__campaign=self.id).all()
            campaignsubscriber_count = 0
            for a in list_contact:
                campaignsubscriber_count += CampaignSubscriber.objects\
                .filter(contact=a.id, campaign=self.id, status=5).count()

            cache.set("campaignsubscriber_count_key_campaign_id_" \
            + str(self.id), campaignsubscriber_count, 5)

        campaignsubscriber_count = int(campaignsubscriber_count)
        count_contact = int(count_contact)

        if count_contact > 0:
            percentage_pixel = \
            (float(campaignsubscriber_count) / count_contact) * 100
            percentage_pixel = int(percentage_pixel)
        else:
            percentage_pixel = 0
        campaignsubscriber_count_string = \
        "campaign-subscribers (" + str(campaignsubscriber_count) + ")"
        return "<div title='%s' style='width: 100px; border: 1px solid #ccc;'>\
                <div style='height: 4px; width: %dpx; background: #555; '>\
                </div></div>" % \
                (campaignsubscriber_count_string, percentage_pixel)
    progress_bar.allow_tags = True
    progress_bar.short_description = _('Progress')

    def campaignsubscriber_detail(self):
        """This will link to campaign subscribers who are associated with
        the campaign"""
        model_name = CampaignSubscriber._meta.object_name.lower()
        app_label = self._meta.app_label
        link = '/admin/%s/%s/' % (app_label, model_name)
        link += '?campaign__id=%d' % self.id # &status__exact=5
        display_link = _("<a href='%(link)s'>%(name)s</a>") % {'link': link, 'name': _('Details')}
        return display_link
    campaignsubscriber_detail.allow_tags = True
    campaignsubscriber_detail.short_description = _('Campaign Subscriber')

    def get_pending_subscriber(self, limit=1000):
        """Get all the pending subscribers from the campaign"""
        list_subscriber = \
        CampaignSubscriber.objects.filter(campaign=self.id, status=1)\
        .all()[:limit]
        if not list_subscriber:
            return False
        return list_subscriber


class CampaignSubscriber(Model):
    """This defines the Contact imported to a Campaign

    **Attributes**:

        * ``last_attempt`` -
        * ``count_attempt`` -
        * ``duplicate_contact`` -
        * ``status`` -

    **Relationships**:

        * ``contact`` - Foreign key relationship to the Contact model.
        * ``campaign`` - Foreign key relationship to the Campaign model.

    **Name of DB table**: dialer_campaign_subscriber
    """
    contact = models.ForeignKey(Contact, null=True, blank=True,
                                help_text=_("Select Contact"))
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                                help_text=_("Select Campaign"))
    last_attempt = models.DateTimeField(null=True, blank=True,
                                        verbose_name=_("Last attempt"))
    count_attempt = models.IntegerField(null=True, blank=True, 
                    verbose_name=_("Count attempts"), default='0')

    #We duplicate contact to create a unique constraint
    duplicate_contact = models.CharField(max_length=90,
                        verbose_name=_("Contact"))
    status = models.IntegerField(choices=CAMPAIGN_SUBSCRIBER_STATUS,
             default='1', verbose_name=_("Status"), blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'dialer_campaign_subscriber'
        verbose_name = _("Campaign Subscriber")
        verbose_name_plural = _("Campaign Subscribers")
        unique_together = ['contact', 'campaign']

    def __unicode__(self):
            return u"%s" % str(self.id)

    def contact_name(self):
        return self.contact.name


def post_save_add_contact(sender, **kwargs):
    """A ``post_save`` signal is sent by the Contact model instance whenever
    it is going to save.

    **Logic Description**:

        * When new contact is added into ``Contact`` model, active the
          campaign list will be checked with the contact status.
        * If the active campaign list count is more than one & the contact 
          is active, the contact will be added into ``CampaignSubscriber`` 
          model.
    """
    obj = kwargs['instance']
    active_campaign_list = \
    Campaign.objects.filter(phonebook__contact__id=obj.id, status=1)
    # created instance = True + active contact + active_campaign
    if kwargs['created'] and obj.status == 1 \
       and active_campaign_list.count() >= 1:
        for elem_campaign in active_campaign_list:
            try:
                CampaignSubscriber.objects.create(
                                     contact=obj,
                                     duplicate_contact=obj.contact,
                                     status=1, # START
                                     campaign=elem_campaign)
            except:
                pass

post_save.connect(post_save_add_contact, sender=Contact)
