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

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from dialer_campaign.models import Campaign
from dialer_cdr.models import Callrequest, VoIPCall
from survey.models import Result, ResultAggregate, Section
from random import choice
from uuid import uuid1
import random

VOIPCALL_DISPOSITION = ['ANSWER', 'BUSY', 'NOANSWER', 'CANCEL', 'CONGESTION',
                        'CHANUNAVAIL', 'DONTCALL', 'TORTURE', 'INVALIDARGS',
                        'NOROUTE', 'FORBIDDEN']
VOIPCALL_DISPOSITION = ['ANSWER']

SURVEY_RESULT_QUE = [
    'Please rank our support from 1 to 9, 1 being low and 9 being high',
    'Were you satisfy by the technical expertise of our agent, '
    'press 1 for yes press 2 for no and 3 to go back',
    'lease record a message to comment on our agent after the beep'
]
VOIPCALL_AMD_STATUS = [1, 2, 3]

RESPONSE = ['apple', 'orange', 'banana']


def create_callrequest(campaign_id, quantity):
    """
    Create Callrequest
    """

    admin_user = User.objects.get(pk=1)
    try:
        obj_campaign = Campaign.objects.get(id=campaign_id)
    except:
        print _('Can\'t find this Campaign : %(id)s' % {'id': campaign_id})
        return False

    length = 5
    chars = "1234567890"

    #'survey' | 'voiceapp'
    try:
        content_type_id = ContentType.objects.get(model='voiceapp').id
    except:
        content_type_id = 1

    for i in range(1, int(quantity) + 1):
        phonenumber = '' . join([choice(chars) for i in range(length)])
        new_callrequest = Callrequest.objects.create(
                            request_uuid=uuid1(),
                            user=admin_user,
                            phone_number=phonenumber,
                            campaign=obj_campaign,
                            aleg_gateway_id=1,
                            status=choice("12345678"),
                            call_type=1,
                            content_type_id=content_type_id,
                            object_id=1)
        print "new_callrequest:"
        print new_callrequest

        voipcall = VoIPCall.objects.create(
                            request_uuid=uuid1(),
                            user=admin_user,
                            callrequest=new_callrequest,
                            phone_number=phonenumber,
                            duration=random.randint(1, 100),
                            disposition=choice(VOIPCALL_DISPOSITION),
                            amd_status=choice(VOIPCALL_AMD_STATUS))
        print "voipcall:"
        print voipcall.id

        response_count = choice("1234567890")

        print "Get list section:"
        list_section = Section.objects.filter(survey=obj_campaign.object_id)

        """
        # for elem in list_section:
        #     print elem[1]
        for j in range(1, 3):
            section_id = random.randint(0, len(list_section) - 1)
            print section_id
            print list_section[section_id]
            print "-----------------"
            try:
                cpg_result = Result.objects.create(
                                    section=list_section[section_id],
                                    response=choice(RESPONSE),
                                    record_file='xyz.mp3',
                                    recording_duration=10,
                                    callrequest=new_callrequest)
            except:
                pass
        #print "cpg_result:"
        #print cpg_result

        ResultAggregate.objects.create(
                            campaign=obj_campaign,
                            survey_id=obj_campaign.object_id,
                            section=list_section[section_id],
                            response=choice(RESPONSE),
                            count=response_count)
        """
    print _("No of Callrequest & CDR created :%(count)s" % \
                {'count': quantity})


class Command(BaseCommand):
    # Use : create_callrequest_cdr '1|1324242' '3|124242'
    #                              'campaign_id|quantity'
    args = _('"campaign_id|quantity" "campaign_id|quantity"')
    help = _("Create new call requests and CDRs for a given campaign_id")

    def handle(self, *args, **options):
        """Note that subscriber created this way are only for devel purposes"""

        for newinst in args:
            res = newinst.split('|')
            campaign_id = res[0]
            quantity = res[1]

            create_callrequest(campaign_id, quantity)
