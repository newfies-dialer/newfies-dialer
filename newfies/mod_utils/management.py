#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from user_profile.constants import NOTIFICATION_NAME
from mod_sms.constants import SMS_NOTIFICATION_NAME


# Info about management.py
# http://stackoverflow.com/questions/4455533/what-is-management-py-in-django

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        kwargs = {}
        kwargs['default'] = NOTIFICATION_NAME.campaign_started
        notification.create_notice_type(
            "campaign_started", _("campaign started"), _("campaign started"), **kwargs)

        kwargs['default'] = NOTIFICATION_NAME.campaign_paused
        notification.create_notice_type(
            "campaign_paused", _("campaign paused"), _("campaign paused"), **kwargs)

        kwargs['default'] = NOTIFICATION_NAME.campaign_aborted
        notification.create_notice_type(
            "campaign_aborted", _("campaign aborted"), _("campaign aborted"), **kwargs)

        kwargs['default'] = NOTIFICATION_NAME.campaign_stopped
        notification.create_notice_type(
            "campaign_stopped", _("campaign stopped"), _("campaign stopped"), **kwargs)

        kwargs['default'] = NOTIFICATION_NAME.campaign_limit_reached
        notification.create_notice_type(
            "campaign_limit_reached", _("campaign limit reached"), _("campaign limit reached"), **kwargs)

        kwargs['default'] = NOTIFICATION_NAME.contact_limit_reached
        notification.create_notice_type(
            "contact_limit_reached", _("contact limit reached"), _("contact limit reached"), **kwargs)

        kwargs['default'] = NOTIFICATION_NAME.dialer_setting_configuration
        notification.create_notice_type(
            "dialer_setting_configuration", _("dialer setting configuration"),
            _("the user needs to be mapped with dialer settings by the administrator"), **kwargs)

        kwargs['default'] = NOTIFICATION_NAME.callrequest_not_found
        notification.create_notice_type(
            "callrequest_not_found", _("call request not found"), _("call request not found"), **kwargs)

        # mod_sms notification
        kwargs['default'] = SMS_NOTIFICATION_NAME.sms_campaign_started
        notification.create_notice_type(
            "sms_campaign_started", _("SMS Campaign started"), _("SMS Campaign started"), **kwargs)

        kwargs['default'] = SMS_NOTIFICATION_NAME.sms_campaign_paused
        notification.create_notice_type(
            "sms_campaign_paused", _("SMS Campaign paused"), _("SMS Campaign paused"), **kwargs)

        kwargs['default'] = SMS_NOTIFICATION_NAME.sms_campaign_aborted
        notification.create_notice_type(
            "sms_campaign_aborted", _("SMS Campaign aborted"), _("SMS Campaign aborted"), **kwargs)

        kwargs['default'] = SMS_NOTIFICATION_NAME.sms_campaign_stopped
        notification.create_notice_type(
            "sms_campaign_stopped", _("SMS Campaign stopped"), _("SMS Campaign stopped"), **kwargs)

        kwargs['default'] = SMS_NOTIFICATION_NAME.sms_campaign_limit_reached
        notification.create_notice_type(
            "sms_campaign_limit_reached", _("SMS Campaign limit reached"),
            _("SMS Campaign limit reached"), **kwargs)

        kwargs['default'] = SMS_NOTIFICATION_NAME.sms_contact_limit_reached
        notification.create_notice_type(
            "sms_contact_limit_reached", _("SMS Contact limit reached"),
            _("SMS Contact limit reached"), **kwargs)

        kwargs['default'] = SMS_NOTIFICATION_NAME.sms_dialer_setting_configuration
        notification.create_notice_type(
            "sms_dialer_setting_configuration", _("SMS Dialer setting configuration"),
            _("The SMS Dialer settings needs to be mapped with dialer settings by the administrator"),
            **kwargs)
    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
