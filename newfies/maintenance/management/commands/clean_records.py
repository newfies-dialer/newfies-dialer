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
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.core.management.base import BaseCommand
from optparse import make_option
from dialer_campaign.models import Campaign, Subscriber
from dialer_cdr.models import Callrequest, VoIPCall
from dialer_contact.models import Phonebook, Contact
#from survey.models import Section
from datetime import datetime
from django.utils.timezone import utc
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
    args = 'older-than-day'
    help = "Clean records older than the giving older-than-day setting (default=365)\n" \
           "------------------------------------------------------------------------\n" \
           "python manage.py clen_records --older-than-day=365"

    option_list = BaseCommand.option_list + (
        make_option('--older-than-day', default=None, dest='older-than-day', help=help),
    )

    def handle(self, *args, **options):
        """
        We will parse and set default values to parameters
        """
        older_than_day = 365  # default
        if options.get('older-than-day'):
            try:
                older_than_day = int(options.get('older-than-day'))
            except ValueError:
                older_than_day = 365

        clean_records(older_than_day)


def clean_records(older_than_day):
    """
    This function delete older database records in order to clean the database:
        * older_than_day

    """
    old_date = datetime.utcnow().replace(tzinfo=utc) + relativedelta(days=-abs(older_than_day))

    print "We will deleted from the database all the records older than: %d days" % older_than_day
    print "The following models will be cleaned:"
    print "  - Campaign"
    print "  - Subscriber"
    print "  - Callrequest"
    print "  - VoIPCall"
    print "  - Phonebook"
    print "  - Contact"
    print ""
    raw_input('Press a key to continue or [CTRL-C] to exit!')

    #Delete olds
    print "Deleting old Campaigns => number to delete: %(count)s" % \
        {'count': Campaign.objects.filter(created_date__lt=old_date).count()}

    Campaign.objects.filter(created_date__lt=old_date).delete()

    #Delete olds
    print "Deleting old Subscribers => number to delete: %(count)s" % \
        {'count': Subscriber.objects.filter(created_date__lt=old_date).count()}

    Subscriber.objects.filter(created_date__lt=old_date).delete()

    #Delete olds
    print "Deleting old Callrequests => number to delete: %(count)s" % \
        {'count': Callrequest.objects.filter(created_date__lt=old_date).count()}

    Callrequest.objects.filter(created_date__lt=old_date).delete()

    #Delete olds
    print "Deleting old VoIPCalls => number to delete: %(count)s" % \
        {'count': VoIPCall.objects.filter(starting_date__lt=old_date).count()}

    VoIPCall.objects.filter(starting_date__lt=old_date).delete()

    #Delete olds
    print "Deleting old Phonebooks => number to delete: %(count)s" % \
        {'count': Phonebook.objects.filter(created_date__lt=old_date).count()}

    Phonebook.objects.filter(created_date__lt=old_date).delete()

    #Delete olds
    print "Deleting old Contacts => number to delete: %(count)s" % \
        {'count': Contact.objects.filter(created_date__lt=old_date).count()}

    Contact.objects.filter(created_date__lt=old_date).delete()

    print "The cleaning is finished!"
