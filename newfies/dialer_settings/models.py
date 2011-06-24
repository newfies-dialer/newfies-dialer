from django.db import models
from django.utils.translation import ugettext as _
from datetime import *


class DialerSetting(models.Model):
    """This defines sets of settings to apply on user

    **Attributes**:

        * ``name`` - Setting name.
        * ``max_frequency`` - Max frequency, speed of the campaign.
                              This is the number of calls per minute.
        * ``callmaxduration`` - Max retry allowed
        * ``maxretry`` - Max retry allowed per user
        * ``max_calltimeout`` - Maximum amount of second to timeout on calls
        * ``max_number_campaign`` - Max Number of campaign
        * ``max_number_subscriber_campaign`` - Max Number of subscriber
        * ``blacklist`` - Used to blacklist phonenumbers to be called
        * ``whitelist`` - Used to whitelist phonenumbers to be called

    **Name of DB table**: dialer_setting
    """
    name = models.CharField(max_length=50, blank=False, null=True,
                    help_text=_("Settings name"))

    #Campaign Settings
    max_frequency = models.IntegerField(default='100', blank=True, null=True,
                               help_text=_("Maximum calls per minute"))
    callmaxduration = models.IntegerField(default='1800', blank=True,
                      null=True, verbose_name=_('Call Max Duration'),
                      help_text=_("Maximum call duration in \
                      seconds (1800 = 30 Minutes)"))
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

    blacklist = models.TextField(blank=False, null=True, default='*',
                    help_text=_("Use regular expressions to blacklist phone\
                    numbers. For example, '^[2-4][1]+' will prevent all phone\
                    numbers starting with 2,3 or 4 and followed by\
                    1 being called."))
    whitelist = models.TextField(blank=False, null=True, default='12345*',
                    help_text=_("Use regular expressions to whitelist\
                    phone numbers"))

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.name)

    class Meta:
        verbose_name = _("Dialer Setting")
        verbose_name_plural = _("Dialer Setting")
        db_table = "dialer_setting"
