from dialer_campaign.models import *
from dilla import spam
import string
import random
import decimal
import logging
import datetime


log = logging.getLogger('dilla')




@spam.strict_handler('dialer_campaign.Campaign.campaign_code')
def get_campaign_code(field):
    return random.choice(string.ascii_letters)
