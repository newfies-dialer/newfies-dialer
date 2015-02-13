from __future__ import absolute_import

import factory
from django.contrib.auth.models import Group, Permission, User
from user_profile.models import CalendarUserProfile, CalendarUser
from calendar_settings.models import CalendarSetting
from user_profile.models import UserProfile, Manager
from dialer_gateway.models import Gateway
from dialer_settings.models import DialerSetting
from survey.models import Survey_template, Survey
from dialer_campaign.constants import AMD_BEHAVIOR
from sms.models import Gateway as SMSGateway

# label = models.CharField(max_length=80, blank=False, verbose_name=_("label"))
# callerid = models.CharField(max_length=80, verbose_name=_("Caller ID Number"),
#                             help_text=_("outbound Caller ID"))
# caller_name = models.CharField(max_length=80, blank=True, verbose_name=_("caller name"),
#                                help_text=_("outbound caller-Name"))
# call_timeout = models.IntegerField(default='60', null=False, blank=False, verbose_name=_('call timeout'),
#                                    help_text=_("call timeout"))
# user = models.ForeignKey(User, blank=False, null=False, verbose_name=_("manager"),
#                          help_text=_("select manager"), related_name="manager_user")
# survey = models.ForeignKey(Survey, null=False, blank=False, verbose_name=_('sealed survey'),
#                            related_name="calendar_survey")
# aleg_gateway = models.ForeignKey(Gateway, null=False, blank=False, verbose_name=_("a-leg gateway"),
#                                  help_text=_("select gateway to use"))
# sms_gateway = models.ForeignKey(SMS_Gateway, verbose_name=_("SMS gateway"), null=False, blank=False,
#                                 related_name="sms_gateway", help_text=_("select SMS gateway"))
# #Voicemail Detection
# voicemail = models.BooleanField(default=False, verbose_name=_('voicemail detection'))
# amd_behavior = models.IntegerField(choices=list(AMD_BEHAVIOR), default=AMD_BEHAVIOR.ALWAYS,
#                                    verbose_name=_("detection behaviour"), blank=True, null=True)
# voicemail_audiofile = models.ForeignKey(AudioFile, null=True, blank=True,
#                                         verbose_name=_("voicemail audio file"))


def _get_perm(perm_name):
    """
    Returns permission instance with given name.
    Permission name is a string like 'auth.add_user'.
    """
    app_label, codename = perm_name.split('.')
    return Permission.objects.get(
        content_type__app_label=app_label, codename=codename)


# class GroupFactory(factory.django.DjangoModelFactory):
#     FACTORY_FOR = Group

#     name = factory.Sequence(lambda n: 'group{0}'.format(n))


class SMSGatewayFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SMSGateway
    name = factory.Sequence(lambda n: 'name{0}'.format(n))
    base_url = "http://domain.ip/api/"
    content_keyword = 'mykeyword'


class GatewayFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Gateway
    name = factory.Sequence(lambda n: 'name{0}'.format(n))
    gateways = factory.Sequence(lambda n: 'sofia/gateway/provider-n{0}'.format(n))


class DialerSettingFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = DialerSetting
    name = factory.Sequence(lambda n: 'name{0}'.format(n))


class UserProfileFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = UserProfile

    # user = factory.SubFactory(UserFactory)
    # userprofile_gateway is a M2M
    # userprofile_gateway = factory.SubFactory(GatewayFactory)
    dialersetting = factory.SubFactory(DialerSettingFactory)


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    first_name = factory.Sequence(lambda n: 'John {0}'.format(n))
    last_name = factory.Sequence(lambda n: 'Doe {0}'.format(n))
    email = factory.Sequence(lambda n: 'user{0}@example.com'.format(n))
    password = '1234'
    # Use a SuperUser for test to not have to deal with permissions
    is_active = True
    is_staff = True
    is_superuser = True

    # Using RelatedFactory http://factoryboy.readthedocs.org/en/latest/reference.html#relatedfactory
    # helps to create the userprofile when we create the User
    userprofile = factory.RelatedFactory(UserProfileFactory, 'user')

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class ManagerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Manager

    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    first_name = factory.Sequence(lambda n: 'John {0}'.format(n))
    last_name = factory.Sequence(lambda n: 'Doe {0}'.format(n))
    email = factory.Sequence(lambda n: 'user{0}@example.com'.format(n))
    password = '1234'
    # Use a SuperUser for test to not have to deal with permissions
    is_active = True
    is_staff = True
    is_superuser = True

    # Using RelatedFactory http://factoryboy.readthedocs.org/en/latest/reference.html#relatedfactory
    # helps to create the userprofile when we create the User
    userprofile = factory.RelatedFactory(UserProfileFactory, 'user')


class SurveyTemplateFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Survey_template

    name = factory.Sequence(lambda n: 'mysurvey-{0}'.format(n))
    user = factory.SubFactory(UserFactory)


class SurveyFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Survey

    name = factory.Sequence(lambda n: 'mysurvey-{0}'.format(n))
    user = factory.SubFactory(UserFactory)


class CalendarSettingFactory(factory.Factory):

    class Meta:
        model = CalendarSetting

    label = factory.Sequence(lambda n: 'Label-{0}'.format(n))
    callerid = "12315456"
    caller_name = factory.Sequence(lambda n: 'callername-{0}'.format(n))
    call_timeout = 60
    user = factory.SubFactory(UserFactory)
    survey = factory.SubFactory(SurveyFactory)
    aleg_gateway = factory.SubFactory(GatewayFactory)
    sms_gateway = factory.SubFactory(SMSGatewayFactory)
    voicemail = False
    amd_behavior = AMD_BEHAVIOR.ALWAYS
    # voicemail_audiofile = None


class CalendarUserProfileFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CalendarUserProfile

    manager = factory.SubFactory(ManagerFactory)
    calendar_setting = factory.SubFactory(CalendarSettingFactory)


class CalendarUserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CalendarUser

    username = factory.Sequence(lambda n: 'caluser{0}'.format(n))
    first_name = factory.Sequence(lambda n: 'John {0}'.format(n))
    last_name = factory.Sequence(lambda n: 'Doe {0}'.format(n))
    email = factory.Sequence(lambda n: 'user{0}@example.com'.format(n))
    password = '1234'
    # Use a SuperUser for test to not have to deal with permissions
    is_active = True
    is_staff = True
    is_superuser = True

    # Using RelatedFactory http://factoryboy.readthedocs.org/en/latest/reference.html#relatedfactory
    # helps to create the userprofile when we create the User
    calendaruserprofile = factory.RelatedFactory(CalendarUserProfileFactory, 'user')

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(CalendarUserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


# class UserFactory(factory.django.DjangoModelFactory):
#     FACTORY_FOR = User

#     username = factory.Sequence(lambda n: 'user{0}'.format(n))
#     first_name = factory.Sequence(lambda n: 'John {0}'.format(n))
#     last_name = factory.Sequence(lambda n: 'Doe {0}'.format(n))
#     email = factory.Sequence(lambda n: 'user{0}@example.com'.format(n))
#     password = '1234'

#     @classmethod
#     def _prepare(cls, create, **kwargs):
#         password = kwargs.pop('password', None)
#         user = super(UserFactory, cls)._prepare(create, **kwargs)
#         if password:
#             user.set_password(password)
#             if create:
#                 user.save()
#         return user

#     @factory.post_generation
#     def permissions(self, create, extracted, **kwargs):
#         if create and extracted:
#             # We have a saved object and a list of permission names
#             self.user_permissions.add(*[_get_perm(pn) for pn in extracted])
