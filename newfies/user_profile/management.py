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


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("campaign_started",
                                        _("Campaign started"),
                                        _("Campaign started"),
                                        1)
        notification.create_notice_type("campaign_paused",
                                        _("Campaign paused"),
                                        _("Campaign paused"),
                                        2)
        notification.create_notice_type("campaign_aborted",
                                        _("Campaign aborted"),
                                        _("Campaign aborted"),
                                        3)
        notification.create_notice_type("campaign_stopped",
                                        _("Campaign stopped"),
                                        _("Campaign stopped"),
                                        4)
        notification.create_notice_type("campaign_limit_reached",
                                        _("Campaign limit reached"),
                                        _("Campaign limit reached"),
                                        5)
        notification.create_notice_type("contact_limit_reached",
                                        _("Contact limit reached"),
                                        _("Contact limit reached"),
                                        6)
        notification.create_notice_type("dialer_setting_configuration",
                                        _("Dialer setting configuration"),
                                        _("The user needs to be mapped with dialer settings by the administrator"),
                                        7)
        notification.create_notice_type("callrequest_not_found",
                                        _("Call request not found"),
                                        _("Call request not found"),
                                        8)
    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
