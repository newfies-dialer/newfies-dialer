from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("campaign_started",
                                        _("Campaign Started"),
                                        _("you have started campaign"),
                                        1)
        notification.create_notice_type("campaign_paused",
                                        _("Campaign Paused"),
                                        _("you have paused campaign"),
                                        2)
        notification.create_notice_type("campaign_aborted",
                                        _("Campaign Aborted"),
                                        _("you have aborted campaign"),
                                        3)
        notification.create_notice_type("campaign_stopped",
                                        _("Campaign Stopped"),
                                        _("you have stopped campaign"),
                                        4)
        notification.create_notice_type("campaign_limit_reached",
                                        _("Campaign Limit Reached"),
                                        _("you have reached the no of campaign limit"),
                                        5)
        notification.create_notice_type("contact_limit_reached",
                                        _("Contact Limit Reached"),
                                        _("you have reached the no of contact limit"),
                                        6)
        notification.create_notice_type("dialer_setting_configuration",
                                        _("Dialer setting configuration"),
                                        _("User need to be mapped with dialer setting by administrator"),
                                        7)
        notification.create_notice_type("callrequest_not_found",
                                        _("Callrequest not found"),
                                        _("Callrequest is not found"),
                                        8)
    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
