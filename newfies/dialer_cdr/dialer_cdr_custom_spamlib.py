from django.contrib.auth.models import User
from dialer_cdr.models import *
from dilla import spam
import string
import random
import decimal
import logging
import datetime


log = logging.getLogger('dilla')

@spam.strict_handler('dialer_cdr.VoIPCall.duration')
def get_duration(record, field):
    return random.randint(1, 100)


@spam.strict_handler('dialer_cdr.VoIPCall.user')
def get_user(record, field):
    return User.objects.get(pk=1)


