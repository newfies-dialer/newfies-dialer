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
from math import pow


class Command(BaseCommand):
    args = ""
    help = "Create a test phonebook with contacts\n"\
           "-------------------------------------------\n"\
           "python manage.py create_phonebook_stresstest --prefix=@myip"

    option_list = BaseCommand.option_list + (
        make_option('--user_id',
                    default=None,
                    dest='user_id',
                    help='User ID under which create phonebooks/contacts'),
        make_option('--prefix',
                    default=None,
                    dest='prefix',
                    help='Prefix to be added after the phonenumber, ie. @myip'),
    )

    def handle(self, *args, **options):
        """
        Note that contacts created this way are only for devel purposes
        """
        length = 15
        chars = "1234567890"

        user_id = 1
        if options.get('user_id'):
            try:
                user_id = int(options.get('user_id'))
            except ValueError:
                user_id = 1

        if options.get('prefix'):
            prefix = options.get('prefix')
        else:
            print 'Need a prefix'
            return False

        for l in range(0, 6):
            amount = int(pow(10, l))  # pow 5 will be 100.000
            try:
                pn_name = 'Phonebook-%d' % amount
                obj_phonebook = Phonebook.objects.create(name=pn_name, user_id=user_id)
            except:
                print 'Can\'t create Phonebook'
                return False

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
