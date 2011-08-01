from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from dialer_campaign.models import *
from dialer_cdr.models import *
from django.db import IntegrityError
from random import choice
import random

VOIPCALL_DISPOSITION = ['ANSWER','BUSY', 'NOANSWER', 'CANCEL', 'CONGESTION',
                        'CHANUNAVAIL', 'DONTCALL', 'TORTURE', 'INVALIDARGS',
                        'NOROUTE', 'FORBIDDEN']

class Command(BaseCommand):
    # Use : create_callrequest_cdr '13843453|1' '324242|1'
    #                              'phone_number|campaign_id'
    args = '"phonenumber|campaign_id"'  '"phonenumber|campaign_id"'
    help = "Creates a new call request and CDR for a given phonenumber and campaign_id \
            \n--------------------------------------------------------------------------\n"

    def handle(self, *args, **options):
        """Note that subscriber created this way are only for devel purposes"""

        for newinst in args:
            print newinst
            res = newinst.split('|')
            phonenumber = res[0]
            campaign_id = res[1]

            try:
                obj_campaign = Campaign.objects.get(id=campaign_id)
            except:
                print 'Can\'t find this Campaign : %s' % campaign_id
                return False

            try:
                new_callrequest = Callrequest.objects.create(
                                    user=User.objects.get(pk=1),
                                    phone_number=phonenumber,
                                    campaign=obj_campaign,
                                    voipapp_id=1,
                                    aleg_gateway_id=1,)
            except IntegrityError:
                print ("The callrequest is duplicated!")
                return False

            print "Callrequest created id:%s" % new_callrequest.id

            try:
                new_cdr = VoIPCall.objects.create(
                                    user=User.objects.get(pk=1),
                                    callrequest=new_callrequest,
                                    phone_number=phonenumber,
                                    used_gateway_id=1,
                                    duration=random.randint(1, 100),
                                    disposition=choice(VOIPCALL_DISPOSITION))
            except IntegrityError:
                print ("The cdr is duplicated!")
                return False

            print "CDR created id:%s" % new_cdr.id