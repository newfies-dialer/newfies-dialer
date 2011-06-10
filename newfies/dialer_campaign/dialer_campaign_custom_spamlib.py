from dialer_campaign.models import *
from dilla import spam
import string
import random
import decimal
import logging
import datetime


log = logging.getLogger('dilla')


@spam.global_handler('TextField')
def spam_campaign_char_field2(field):
    return random.choice(string.ascii_letters)
