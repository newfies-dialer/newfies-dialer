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
from user_profile.models import Profile_abstract
from survey.models import Survey


class Calender_Setting(models.Model):
    """This defines the Calender settings to apply to a ar_user

    **Attributes**:

        * ``cid_number`` - CID number.
        * ``cid_name`` - CID name
        * ``call_timeout`` - call timeout
        * ``user`` - Newfies User
        * ``survey`` - Frozen Survey

    **Name of DB table**: calender_setting
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
                             related_name="calender_user")
    survey = models.ForeignKey(Survey, null=True, blank=True,
                               verbose_name=_('frozen survey'),
                               related_name="calender_survey")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.cid_name)

    class Meta:
        verbose_name = _("Calender setting")
        verbose_name_plural = _("calender settings")
        db_table = "calender_setting"


class Calender_User(User):
    """Calender User Model"""

    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('calender user')
        verbose_name_plural = _('calender users')

    def save(self, **kwargs):
        if not self.pk:
            self.is_staff = 0
            self.is_superuser = 0
        super(Calender_User, self).save(**kwargs)

    def is_calender_user(self):
        try:
            Calender_UserProfile.objects.get(user=self)
            return True
        except:
            return False
    User.add_to_class('is_calender_user', is_calender_user)


class Calender_UserProfile(Profile_abstract):
    """This defines extra features for the AR_user

    **Attributes**:

        * ``ar_dialersetting`` - appointment reminder settings


    **Name of DB table**: ar_user_profile
    """
    calender_dialersetting = models.ForeignKey(Calender_Setting, null=True, blank=True,
                                               verbose_name=_('calender settings'))

    class Meta:
        db_table = 'calender_user_profile'
        verbose_name = _("calender user profile")
        verbose_name_plural = _("calender user profiles")

    def __unicode__(self):
        return u"%s" % str(self.user)
