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
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from user_profile.models import Manager, Profile_abstract
from survey.models import Survey


class CalendarSetting(models.Model):
    """This defines the Calender settings to apply to a ar_user

    **Attributes**:

        * ``cid_number`` - CID number.
        * ``cid_name`` - CID name
        * ``call_timeout`` - call timeout
        * ``user`` - Newfies User
        * ``survey`` - Frozen Survey

    **Name of DB table**: calendar_setting
    """
    cid_number = models.CharField(max_length=50, blank=False, null=True,
                                  verbose_name=_("CID number"),
                                  help_text=_("CID number"))
    cid_name = models.CharField(max_length=50, blank=False, null=True,
                                verbose_name=_("CID name"),
                                help_text=_("CID name"))
    call_timeout = models.IntegerField(default='3', blank=True, null=True,
                                       verbose_name=_('call timeout'),
                                       help_text=_("call timeout"))
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=_("user"),
                             help_text=_("select user"),
                             related_name="calendar_user")
    survey = models.ForeignKey(Survey, null=True, blank=True,
                               verbose_name=_('frozen survey'),
                               related_name="calendar_survey")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.cid_name)

    class Meta:
        verbose_name = _("Calender setting")
        verbose_name_plural = _("calendar settings")
        db_table = "calendar_setting"
        app_label = "appointment"


class CalendarUser(User):
    """Calendar User Model"""

    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('calendar user')
        verbose_name_plural = _('calendar users')

    def save(self, **kwargs):
        if not self.pk:
            self.is_staff = 0
            self.is_superuser = 0
        super(CalendarUser, self).save(**kwargs)

    def is_calendar_user(self):
        try:
            CalendarUserProfile.objects.get(user=self)
            return True
        except:
            return False
    User.add_to_class('is_calendar_user', is_calendar_user)


class CalendarUserProfile(Profile_abstract):
    """This defines extra features for the AR_user

    **Attributes**:

        * ``calendar_setting`` - appointment reminder settings


    **Name of DB table**: calendar_user_profile
    """
    manager = models.ForeignKey(Manager, verbose_name=_("manager"), related_name="manager_of_calendar_user",
                                help_text=_("select manager"))
    calendar_setting = models.ForeignKey(CalendarSetting, null=True, blank=True,
                                         verbose_name=_('calendar settings'))

    class Meta:
        db_table = 'calendar_user_profile'
        verbose_name = _("calendar user profile")
        verbose_name_plural = _("calendar user profiles")
        app_label = "appointment"

    def __unicode__(self):
        return u"%s" % str(self.user)


# Create calendar user profile object
CalendarUser.profile = property(lambda u: CalendarUserProfile.objects.get_or_create(user=u)[0])
