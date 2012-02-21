#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public 
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
# 
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
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
    args = _('"campaign_id|no_of_record" "campaign_id|no_of_record"')
    help = _("Creates no of new call requests and CDRs for a given campaign_id & no of records")

    def handle(self, *args, **options):
        """Note that subscriber created this way are only for devel purposes"""

        for newinst in args:
            res = newinst.split('|')
            campaign_id = res[0]
            no_of_record = res[1]

            try:
                admin_user = User.objects.get(pk=1)
                try:
                    obj_campaign = Campaign.objects.get(id=campaign_id)
                except:
                    print _('Can\'t find this Campaign : %(id)s' % {'id': campaign_id})
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
                    print _("No of Callrequest & CDR created :%(count)s" % {'count': no_of_record})
                except IntegrityError:
                    print _("Callrequest & CDR are not created!")
                    return False
            except:
                print _("No admin user")
                return False
