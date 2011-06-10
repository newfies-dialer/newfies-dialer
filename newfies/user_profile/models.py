from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from dialer_gateway.models import Gateway
from voip_server.models import VoipServerGroup
from dialer_settings.models import DialerSetting


class UserProfile(models.Model):
    """This defines extra feature on the user

    **Attributes**:

        * ``accountcode`` - Account name.

    Relationships:

        * ``user`` - Foreign key relationship to the User model.
        * ``userprofile_gateway`` - ManyToMany
        * ``userprofile_voipservergroup`` - ManyToMany
        * ``dialersetting`` - Foreign key relationship to the DialerSetting \
        model.

    **Name of DB table**: user_profile
    """
    user = models.OneToOneField(User)
    accountcode = models.PositiveIntegerField(null=True, blank=True)
    #voip_gateway = models.ForeignKey(Gateway, verbose_name='VoIP Gateway',
    #                            help_text=_("Select VoIP Gateway"))
    userprofile_gateway = models.ManyToManyField(Gateway,
                                            verbose_name='Gateway')
    userprofile_voipservergroup = models.ManyToManyField(VoipServerGroup,
                                            verbose_name='Server Group')
    dialersetting = models.OneToOneField(DialerSetting,
                      verbose_name='Dialer Setting', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profile'
        app_label = _('user_profile')
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profile")


class Customer(User):

    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')


class Staff(User):

    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('Admin')
        verbose_name_plural = _('Admins')

    def save(self, **kwargs):
        if not self.pk:
            self.is_staff = 1
            self.is_superuser = 1
        super(Staff, self).save(**kwargs)
