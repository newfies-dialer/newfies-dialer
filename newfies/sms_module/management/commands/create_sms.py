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
from sms_module.models import SMSMessage, SMSCampaign
from random import choice
from uuid import uuid1
import random
from datetime import datetime, timedelta
from django.utils.timezone import utc


MESSAGE_STATUSES = ['Unsent', 'Sent', 'Delivered', 'Failed', 'No_Route', 'Unauthorized']


def create_sms(smscampaign_id, quantity):
    """
    Create sms
    """

    admin_user = User.objects.get(pk=1)
    try:
        obj_campaign = SMSCampaign.objects.get(id=smscampaign_id)
    except:
        print _('Can\'t find this SMS Campaign : %(id)s' % {'id': smscampaign_id})
        return False

    #'survey' | 'voiceapp'
    try:
        content_type_id = ContentType.objects.get(model='survey').id
    except:
        content_type_id = 1

    length = 5
    chars = "1234567890"
    #alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    day_delta_int = 3
    delta_days = random.randint(0, day_delta_int)
    delta_minutes = random.randint(1, 1440)

    send_date = datetime.utcnow().replace(tzinfo=utc) - timedelta(
        minutes=delta_minutes) - timedelta(days=delta_days)

    duration = 10
    delivery_date = str(datetime.utcnow().replace(tzinfo=utc) - timedelta(
        minutes=delta_minutes) - timedelta(days=delta_days)
        + timedelta(seconds=duration))

    for i in range(1, int(quantity) + 1):
        phonenumber = '' . join([choice(chars) for i in range(length)])
        new_sms = SMSMessage.objects.create(
            content='this is test',
            recipient_number=phonenumber,
            sender=obj_campaign.user,
            sender_number=phonenumber,
            send_date=send_date,
            delivery_date=delivery_date,
            uuid=uuid1(),
            content_type_id=content_type_id,
            object_id=1,
            status=choice(MESSAGE_STATUSES),
            sms_campaign=obj_campaign,
            sms_gateway_id=1)
        print "new_sms:"
        print new_sms

    print _("No of SMS :%(count)s" % {'count': quantity})


class Command(BaseCommand):
    # Use : create_sms '1|1324242' '3|124242'
    #                              'campaign_id|quantity'
    args = _('"sms_campaign_id|quantity" "sms_campaign_id|quantity"')
    help = _("Create new SMSs for a given sms_campaign_id")

    def handle(self, *args, **options):
        """Note that subscriber created this way are only for devel purposes"""

        for newinst in args:
            res = newinst.split('|')
            campaign_id = res[0]
            quantity = res[1]

            create_sms(campaign_id, quantity)
