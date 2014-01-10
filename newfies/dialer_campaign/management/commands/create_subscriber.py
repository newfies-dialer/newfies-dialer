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
from django.db import IntegrityError
from optparse import make_option
from dialer_campaign.models import Phonebook, Contact, Campaign
from dialer_campaign.tasks import collect_subscriber


class Command(BaseCommand):
    args = 'phonebook_id, list_of_phonenumber'
    help = "Create a new contact for a given phonenumber and phonebook\n" \
           "--------------------------------------------------------------\n" \
           "python manage.py create_subscriber --phonebook_id=1 --list_of_phonenumber=123456,9867456"

    option_list = BaseCommand.option_list + (
        make_option('--list_of_phonenumber',
                    default=None,
                    dest='list_of_phonenumber',
                    help=help),
        make_option('--phonebook_id',
                    default=None,
                    dest='phonebook_id',
                    help=help),
    )

    def handle(self, *args, **options):
        """Note that subscriber created this way are only for devel purposes"""
        list_of_phonenumber = ''  # default
        if options.get('list_of_phonenumber'):
            try:
                list_of_phonenumber = options.get('list_of_phonenumber').split(',')
            except ValueError:
                list_of_phonenumber = ''

        phonebook_id = ''
        if options.get('phonebook_id'):
            try:
                phonebook_id = options.get('phonebook_id')
                phonebook_id = int(phonebook_id)
            except ValueError:
                phonebook_id = ''

        try:
            obj_phonebook = Phonebook.objects.get(id=phonebook_id)
        except:
            print 'Can\'t find this Phonebook : %(id)s' % {'id': phonebook_id}
            return False

        for phonenumber in list_of_phonenumber:
            try:
                new_contact = Contact.objects.create(
                    contact=int(phonenumber),
                    phonebook=obj_phonebook)
            except IntegrityError:
                print "Duplicate contact!"
                return False

            print "Contact created id:%(id)s" % {'id': new_contact.id}

        try:
            obj_campaign = Campaign.objects.get(phonebook=obj_phonebook)
        except:
            print 'Can\'t find a Campaign with this phonebook'
            return False

        print "Launch Task : collect_subscriber(%(id)s)" % {'id': str(obj_campaign.id)}
        collect_subscriber.delay(obj_campaign.id)
