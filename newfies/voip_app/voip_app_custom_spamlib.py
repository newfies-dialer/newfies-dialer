from voip_app.models import *
from dilla import spam
import string
import random
import decimal
import logging
import datetime


log = logging.getLogger('dilla')


@spam.strict_handler('voip_app.VoipApp.data')
def get_voip_app_data(field):
    return random.choice(string.ascii_letters)
