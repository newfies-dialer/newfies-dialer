#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.db import IntegrityError
from dialer_campaign.models import Phonebook, Contact, Campaign
from dialer_campaign.tasks import collect_subscriber


class Command(BaseCommand):
    args = _('<phonenumber|phonebook_id, phonenumber|phonebook_id,...>')
    help = _("Creates a new contact for a given phonenumber and phonebook")

    def handle(self, *args, **options):
        """Note that subscriber created this way are only for devel purposes"""

        for newinst in args:
            print newinst
            res = newinst.split('|')
            myphonenumber = res[0]
            myphonebook_id = res[1]

            try:
                obj_phonebook = Phonebook.objects.get(id=myphonebook_id)
            except:
                print _('Can\'t find this Phonebook : %(id)s' % {'id': myphonebook_id})
                return False

            try:
                new_contact = Contact.objects.create(
                    contact=myphonenumber,
                    phonebook=obj_phonebook)
            except IntegrityError:
                print _("Duplicate contact!")
                return False

            print _("Contact created id:%(id)s" % {'id': new_contact.id})

            try:
                obj_campaign = Campaign.objects.get(phonebook=obj_phonebook)
            except:
                print _('Can\'t find a Campaign with this phonebook')
                return False

            print _("Launch Task : collect_subscriber(%(id)s)" %
                {'id': str(obj_campaign.id)})
            collect_subscriber.delay(obj_campaign.id)
