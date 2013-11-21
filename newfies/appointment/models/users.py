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
from dialer_gateway.models import Gateway


class CalendarSetting(models.Model):
    """This defines the Calender settings to apply to a ar_user

    **Attributes**:

        * ``callerid`` - CallerID number.
        * ``caller_name`` - Caller name
        * ``call_timeout`` - call timeout
        * ``user`` - Newfies User (Manager)
        * ``survey`` - Foreign key relationship to the Survey
        * ``aleg_gateway`` - Foreign key relationship to the Gateway model.\
                             Gateway to use to call the subscriber


    **Name of DB table**: calendar_setting
    """
    callerid = models.CharField(max_length=80, blank=True,
                                verbose_name=_("callerID"),
                                help_text=_("outbound caller-ID"))
    caller_name = models.CharField(max_length=80, blank=True,
                                   verbose_name=_("caller name"),
                                   help_text=_("outbound caller-Name"))
    call_timeout = models.IntegerField(default='60', null=False, blank=False,
                                       verbose_name=_('call timeout'),
                                       help_text=_("call timeout"))
    user = models.ForeignKey(User, blank=False, null=False, verbose_name=_("manager"),
                             help_text=_("select manager"),
                             related_name="manager_user")
    survey = models.ForeignKey(Survey, null=False, blank=False,
                               verbose_name=_('frozen survey'),
                               related_name="calendar_survey")
    aleg_gateway = models.ForeignKey(Gateway, null=False, blank=False,
                                     verbose_name=_("a-leg gateway"),
                                     help_text=_("select gateway to use to be used"))

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.caller_name)

    class Meta:
        permissions = (
            ("view_calendarsetting ", _('can see Calendar Setting list')),
        )
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
    manager = models.ForeignKey(Manager, verbose_name=_("manager"),
                                help_text=_("select manager"),
                                related_name="manager_of_calendar_user")
    calendar_setting = models.ForeignKey(CalendarSetting, null=False, blank=False,
                                         verbose_name=_('calendar settings'))

    class Meta:
        permissions = (
            ("view_calendar_user", _('can see Calendar User list')),
        )
        db_table = 'calendar_user_profile'
        verbose_name = _("calendar user profile")
        verbose_name_plural = _("calendar user profiles")
        app_label = "appointment"

    def __unicode__(self):
        return u"%s" % str(self.user)


# Create calendar user profile object
CalendarUser.profile = property(lambda u: CalendarUserProfile.objects.get_or_create(user=u)[0])
