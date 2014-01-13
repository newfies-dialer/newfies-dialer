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
from dialer_contact.models import Phonebook, Contact
from optparse import make_option
from django.db import IntegrityError
from random import choice


class Command(BaseCommand):
    args = "phonebook_id, amount"
    help = "Create a new contacts for a given phonebook\n"\
           "-------------------------------------------\n"\
           "python manage.py create_contact --phonebook_id=1 --amount=100 --prefix=@myip"

    option_list = BaseCommand.option_list + (
        make_option('--amount',
                    default=None,
                    dest='amount',
                    help='Amount to create, by default 1 contact will be created'),
        make_option('--phonebook_id',
                    default=None,
                    dest='phonebook_id',
                    help='Phonebook ID for the new contact'),
        make_option('--prefix',
                    default=None,
                    dest='prefix',
                    help='Prefix to be added after the phonenumber, ie. @myip'),
    )

    def handle(self, *args, **options):
        """
        Note that contacts created this way are only for devel purposes
        """
        amount = 1  # default
        if options.get('amount'):
            try:
                amount = int(options.get('amount'))
            except ValueError:
                amount = 1

        phonebook_id = 1
        if options.get('phonebook_id'):
            try:
                phonebook_id = options.get('phonebook_id')
                phonebook_id = int(phonebook_id)
            except ValueError:
                phonebook_id = 1

        prefix = ''
        if options.get('prefix'):
            prefix = options.get('prefix')

        try:
            obj_phonebook = Phonebook.objects.get(id=phonebook_id)
        except:
            print 'Can\'t find this Phonebook : %(id)s' % {'id': phonebook_id}
            return False

        length = 15
        chars = "1234567890"
        for k in range(1, int(amount) + 1):
            if k % 1000 == 0:
                print "%d contacts created..." % k
            phone_no = ''.join([choice(chars) for i in range(length)])

            #TODO: Use generate_series to speed up the contact creation
            #INSERT INTO numbers (num) VALUES ( generate_series(1,1000));

            try:
                Contact.objects.create(
                    contact=phone_no + prefix,
                    phonebook=obj_phonebook)
            except IntegrityError:
                print "Error : Duplicate contact - %s" % phone_no

        print "\nTotal contacts created : %(count)s" % {'count': amount}
