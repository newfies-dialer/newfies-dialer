from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from dialer_campaign.models import *
from dialer_cdr.models import *
from django.db import IntegrityError
from random import choice
from uuid import uuid1
import random

VOIPCALL_DISPOSITION = ['ANSWER','BUSY', 'NOANSWER', 'CANCEL', 'CONGESTION',
                        'CHANUNAVAIL', 'DONTCALL', 'TORTURE', 'INVALIDARGS',
                        'NOROUTE', 'FORBIDDEN']

class Command(BaseCommand):
    # Use : create_callrequest_cdr '13843453|1' '324242|1'
    #                              'phone_no|campaign_id'
    args = '"campaign_id|no_of_record" "campaign_id|no_of_record"'
    help = "Creates no of new call requests and CDRs for a given campaign_id & no of records \
            \n--------------------------------------------------------------------------------\n"

    def handle(self, *args, **options):
        """Note that subscriber created this way are only for devel purposes"""

        for newinst in args:
            print newinst
            res = newinst.split('|')
            campaign_id = res[0]
            no_of_record = res[1]

            try:
                admin_user = User.objects.get(pk=1)
                try:
                    obj_campaign = Campaign.objects.get(id=campaign_id)
                except:
                    print 'Can\'t find this Campaign : %s' % campaign_id
                    return False

                try:
                    length=5
                    chars="1234567890"
                    for i in range(1, int(no_of_record) + 1):
                        phonenumber = '' . join([choice(chars) for i in range(length)])
                        new_callrequest = Callrequest.objects.create(
                                            request_uuid=uuid1(),
                                            user=admin_user,
                                            phone_number=phonenumber,
                                            campaign=obj_campaign,
                                            aleg_gateway_id=1,
                                            status=choice("12345678"),
                                            call_type=1)
                        new_cdr = VoIPCall.objects.create(
                                            request_uuid=uuid1(),
                                            user=admin_user,
                                            callrequest=new_callrequest,
                                            phone_number=phonenumber,
                                            duration=random.randint(1, 100),
                                            disposition=choice(VOIPCALL_DISPOSITION))
                    print "No of Callrequest & CDR created :%d" % int(no_of_record)
                except IntegrityError:
                    print ("Callrequest & CDR are not created!")
                    return False
            except:
                print "No admin user"
                return False
