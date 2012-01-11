from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import *


class DialerSetting(models.Model):
    """This defines the settings to apply to a user

    **Attributes**:

        * ``name`` - Settings name.
        * ``max_frequency`` - Max frequency, speed of the campaign.\
        This is the number of calls per minute.
        * ``callmaxduration`` - Max retries allowed
        * ``maxretry`` - Max retries allowed per user
        * ``max_calltimeout`` - Maximum number of seconds to timeout on calls
        * ``max_number_campaign`` - Max Number of campaigns
        * ``max_number_subscriber_campaign`` - Max Number of subscribera
        * ``blacklist`` - Used to blacklist phone numbers to be called
        * ``whitelist`` - Used to whitelist phone numbers to be called

    **Name of DB table**: dialer_setting
    """
    name = models.CharField(max_length=50, blank=False, null=True, verbose_name=_("Name"),
                    help_text=_("Settings name"))

    #Campaign Settings
    max_frequency = models.IntegerField(default='100', blank=True, null=True, verbose_name=_("Max frequency"),
                               help_text=_("Maximum calls per minute"))
    callmaxduration = models.IntegerField(default='1800', blank=True,
                      null=True, verbose_name=_('Call Max Duration'),
    help_text=_("Maximum call duration in seconds (1800 = 30 Minutes)"))

    maxretry = models.IntegerField(default='3', blank=True, null=True,
                               verbose_name=_('Max Retries'),
                               help_text=_("Maximum retries per user."))
    max_calltimeout = models.IntegerField(default='45', blank=True, null=True,
                      verbose_name=_('Timeout on Call'),
                      help_text=_("Maximum call timeout in seconds"))

    max_number_campaign = models.IntegerField(default=10,
                               help_text=_("Maximum number of campaigns"))
    max_number_subscriber_campaign = models.IntegerField(default=10000,
                               help_text=_("Maximum subscribers per campaign"))

    blacklist = models.TextField(blank=True, null=True, default='', verbose_name=_("Blacklist"),
    help_text=_("Use regular expressions to blacklist phone numbers. For example, '^[2-4][1]+' will prevent all phone numbers starting with 2,3 or 4 and followed by 1 being called."))

    whitelist = models.TextField(blank=True, null=True, default='', verbose_name=_("Whitelist"),
    help_text=_("Use regular expressions to whitelist phone numbers"))

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.name)

    class Meta:
        verbose_name = _("Dialer Setting")
        verbose_name_plural = _("Dialer Setting")
        db_table = "dialer_setting"
