#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.core.management.base import BaseCommand
from optparse import make_option
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from dialer_campaign.models import Campaign
from dialer_cdr.models import Callrequest, VoIPCall
#from survey.models import Section
from random import choice
from uuid import uuid1
from datetime import datetime, timedelta
from django.utils.timezone import utc
import random
import bisect

VOIPCALL_DISPOSITION = [('ANSWER', 80), ('BUSY', 10), ('NOANSWER', 20), ('CANCEL', 5), ('CONGESTION', 4), ('FAILED', 10)]
SURVEY_RESULT_QUE = [
    'Please rank our support from 1 to 9, 1 being low and 9 being high',
    'Were you satisfy by the technical expertise of our agent, '
    'press 1 for yes press 2 for no and 3 to go back',
    'lease record a message to comment on our agent after the beep'
]
VOIPCALL_AMD_STATUS = [1, 2, 3]
RESPONSE = ['apple', 'orange', 'banana', 'mango', 'greps', 'watermelon']


def weighted_choice(choices):
    values, weights = zip(*choices)
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)
    x = random.random() * total
    i = bisect.bisect(cum_weights, x)
    return values[i]


def create_callrequest(campaign_id, no_of_record, day_delta_int):
    """
    Create Callrequest
    """
    try:
        obj_campaign = Campaign.objects.get(id=campaign_id)
    except:
        print _('Can\'t find this Campaign : %(id)s' % {'id': campaign_id})
        return False

    length = 5
    chars = "1234567890"

    #content_type_id is survey
    try:
        content_type_id = ContentType.objects.get(model='survey').id
    except:
        content_type_id = 1

    for i in range(1, int(no_of_record) + 1):
        delta_days = random.randint(0, day_delta_int)
        delta_minutes = random.randint(-720, 720)
        created_date = datetime.utcnow().replace(tzinfo=utc) \
            - timedelta(minutes=delta_minutes) \
            - timedelta(days=delta_days)

        phonenumber = '' . join([choice(chars) for i in range(length)])
        new_callrequest = Callrequest.objects.create(
            request_uuid=uuid1(),
            user=obj_campaign.user,
            phone_number=phonenumber,
            campaign=obj_campaign,
            aleg_gateway_id=1,
            status=choice("12345678"),
            call_type=1,
            content_type_id=content_type_id,
            call_time=created_date,
            created_date=created_date,
            object_id=1)
        print "new_callrequest: " + str(new_callrequest)

        voipcall = VoIPCall.objects.create(
            request_uuid=uuid1(),
            callid=uuid1(),
            user=obj_campaign.user,
            callrequest=new_callrequest,
            starting_date=created_date,
            phone_number=phonenumber,
            duration=random.randint(50, 1000),
            disposition=weighted_choice(VOIPCALL_DISPOSITION),
            amd_status=choice(VOIPCALL_AMD_STATUS))
        print "voipcall: " + str(voipcall)
        voipcall.starting_date = created_date
        voipcall.save()

        """
        alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        response_count = choice("1234567890")

        # print "Get list section:"
        from survey.models import Section, ResultAggregate
        list_section = Section.objects.filter(survey_id=obj_campaign.object_id)
        #list_section = Section.objects.all()


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
        #response = '' . join([choice(alpha) for i in range(length)])
        ResultAggregate.objects.create(
                            survey_id=obj_campaign.object_id,
                            section=list_section[section_id],
                            response=choice(RESPONSE),
                            #response=response,
                            count=response_count)
        """
    print _("Callrequests and CDRs created : %(count)s" %
        {'count': no_of_record})


class Command(BaseCommand):
    args = 'campaign_id, no_of_record, delta_day'
    help = "Generate random call-requests and CDRs for a given campaign_id\n" \
           "--------------------------------------------------------------\n" \
           "python manage.py create_callrequest_cdr --campaign_id=1 --number-call=100 --delta-day=0"

    option_list = BaseCommand.option_list + (
        make_option('--number-call',
                    default=None,
                    dest='number-call',
                    help=help),
        make_option('--delta-day',
                    default=None,
                    dest='delta-day',
                    help=help),
        make_option('--campaign_id',
                    default=None,
                    dest='campaign_id',
                    help=help),
    )

    def handle(self, *args, **options):
        """
        Note that subscriber created this way are only for devel purposes
        """
        no_of_record = 1  # default
        if options.get('number-call'):
            try:
                no_of_record = int(options.get('number-call'))
            except ValueError:
                no_of_record = 1

        day_delta_int = 30  # default
        if options.get('delta-day'):
            try:
                day_delta_int = int(options.get('delta-day'))
            except ValueError:
                day_delta_int = 30

        campaign_id = 1
        if options.get('campaign_id'):
            try:
                campaign_id = options.get('campaign_id')
                campaign_id = int(campaign_id)
            except ValueError:
                campaign_id = 1

        create_callrequest(campaign_id, no_of_record, day_delta_int)
