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

from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from user_profile.constants import NOTIFICATION_NAME


#Info about management.py
#http://stackoverflow.com/questions/4455533/what-is-management-py-in-django

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type(
            "campaign_started",
            _("campaign started"),
            _("campaign started"),
            NOTIFICATION_NAME.campaign_started)
        notification.create_notice_type(
            "campaign_paused",
            _("campaign paused"),
            _("campaign paused"),
            NOTIFICATION_NAME.campaign_paused)
        notification.create_notice_type(
            "campaign_aborted",
            _("campaign aborted"),
            _("campaign aborted"),
            NOTIFICATION_NAME.campaign_aborted)
        notification.create_notice_type(
            "campaign_stopped",
            _("campaign stopped"),
            _("campaign stopped"),
            NOTIFICATION_NAME.campaign_stopped)
        notification.create_notice_type(
            "campaign_limit_reached",
            _("campaign limit reached"),
            _("campaign limit reached"),
            NOTIFICATION_NAME.campaign_limit_reached)
        notification.create_notice_type(
            "contact_limit_reached",
            _("contact limit reached"),
            _("contact limit reached"),
            NOTIFICATION_NAME.contact_limit_reached)
        notification.create_notice_type(
            "dialer_setting_configuration",
            _("dialer setting configuration"),
            _("the user needs to be mapped with dialer settings by the administrator"),
            NOTIFICATION_NAME.dialer_setting_configuration)
        notification.create_notice_type(
            "callrequest_not_found",
            _("call request not found"),
            _("call request not found"),
            NOTIFICATION_NAME.callrequest_not_found)
    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
