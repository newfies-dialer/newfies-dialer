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

from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from sms_module.constants import SMS_NOTIFICATION_NAME


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("sms_campaign_started",
                                        _("SMS Campaign started"),
                                        _("SMS Campaign started"),
            SMS_NOTIFICATION_NAME.sms_campaign_started)
        notification.create_notice_type("sms_campaign_paused",
                                        _("SMS Campaign paused"),
                                        _("SMS Campaign paused"),
            SMS_NOTIFICATION_NAME.sms_campaign_paused)
        notification.create_notice_type("sms_campaign_aborted",
                                        _("SMS Campaign aborted"),
                                        _("SMS Campaign aborted"),
            SMS_NOTIFICATION_NAME.sms_campaign_aborted)
        notification.create_notice_type("sms_campaign_stopped",
                                        _("SMS Campaign stopped"),
                                        _("SMS Campaign stopped"),
            SMS_NOTIFICATION_NAME.sms_campaign_stopped)
        notification.create_notice_type("sms_campaign_limit_reached",
                                        _("SMS Campaign limit reached"),
                                        _("SMS Campaign limit reached"),
            SMS_NOTIFICATION_NAME.sms_campaign_limit_reached)
        notification.create_notice_type("sms_contact_limit_reached",
                                        _("SMS Contact limit reached"),
                                        _("SMS Contact limit reached"),
            SMS_NOTIFICATION_NAME.sms_contact_limit_reached)
        notification.create_notice_type("sms_dialer_setting_configuration",
                                        _("SMS Dialer setting configuration"),
                                        _("The SMS Dialer settings needs to be mapped with dialer settings by the administrator"),
            SMS_NOTIFICATION_NAME.sms_dialer_setting_configuration)
    signals.post_syncdb.connect(create_notice_types, sender=notification)
#else:
#    print "Skipping creation of NoticeTypes as notification app not found"
