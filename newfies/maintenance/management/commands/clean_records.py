#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.core.management.base import BaseCommand
from optparse import make_option
from dialer_campaign.models import Campaign, Subscriber
from dialer_cdr.models import Callrequest, VoIPCall
# from dialer_contact.models import Phonebook, Contact
from survey.models import Survey, Section, Branching, Result, ResultAggregate
# from django.db import connection
# from survey.models import Section
from datetime import datetime
from django.utils.timezone import utc
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
    args = 'older-than-day'
    help = "Clean records older than the giving older-than-day setting (default=365)\n" \
           "------------------------------------------------------------------------\n" \
           "python manage.py clean_records --older-than-day=365"

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
    # print "  - Phonebook"
    # print "  - Contact"
    print ""

    # Delete old Campaigns
    print "Deleting old Campaigns => number to delete: %(count)s" % \
        {'count': Campaign.objects.filter(created_date__lt=old_date).count()}

    list_obj = Campaign.objects.filter(created_date__lt=old_date)
    for obj in list_obj:
        print "Deleting Campaign => : %s" % obj
        obj.delete()

    # Delete old Subscribers
    print "Deleting old Subscribers => number to delete: %(count)s" % \
        {'count': Subscriber.objects.filter(created_date__lt=old_date).count()}

    list_obj = Subscriber.objects.filter(created_date__lt=old_date)
    for obj in list_obj:
        print "Deleting Subscriber => : %s" % obj
        obj.delete()

    # Delete old Callrequests
    print "Deleting old Callrequests => number to delete: %(count)s" % \
        {'count': Callrequest.objects.filter(created_date__lt=old_date).count()}

    list_obj = Callrequest.objects.filter(created_date__lt=old_date)
    for obj in list_obj:
        print "Deleting Callrequest => : %s" % obj
        obj.delete()

    # Delete old VoIPCalls
    print "Deleting old VoIPCalls => number to delete: %(count)s" % \
        {'count': VoIPCall.objects.filter(starting_date__lt=old_date).count()}

    list_obj = VoIPCall.objects.filter(starting_date__lt=old_date)
    for obj in list_obj:
        print "Deleting VoIPCall => : %s" % obj
        obj.delete()

    # Delete old Phonebooks
    # print "Deleting old Phonebooks => number to delete: %(count)s" % \
    #     {'count': Phonebook.objects.filter(created_date__lt=old_date).count()}

    # list_obj = Phonebook.objects.filter(created_date__lt=old_date)
    # for obj in list_obj:
    #     print "Deleting Phonebook => : %s" % obj
    #     obj.delete()

    # #Delete old Contacts
    # print "Deleting old Contacts => number to delete: %(count)s" % \
    #     {'count': Contact.objects.filter(created_date__lt=old_date).count()}

    # list_obj = Contact.objects.filter(created_date__lt=old_date)
    # for obj in list_obj:
    #     print "Deleting Contact => : %s" % obj
    #     obj.delete()

    # Delete old ResultAggregates
    print "Deleting old ResultAggregates => number to delete: %(count)s" % \
        {'count': ResultAggregate.objects.filter(created_date__lt=old_date).count()}

    list_obj = ResultAggregate.objects.filter(created_date__lt=old_date)
    for obj in list_obj:
        print "Deleting ResultAggregate => : %s" % obj
        obj.delete()

    # Delete old Result
    print "Deleting old Result => number to delete: %(count)s" % \
        {'count': Result.objects.filter(created_date__lt=old_date).count()}

    list_obj = Result.objects.filter(created_date__lt=old_date)
    for obj in list_obj:
        print "Deleting Result => : %s" % obj
        obj.delete()

    # Delete old Branchings
    print "Deleting old Branchings => number to delete: %(count)s" % \
        {'count': Branching.objects.filter(created_date__lt=old_date).count()}

    list_obj = Branching.objects.filter(created_date__lt=old_date)
    for obj in list_obj:
        print "Deleting Branching => : %s" % obj
        obj.delete()

    # Delete old Sections
    print "Deleting old Sections => number to delete: %(count)s" % \
        {'count': Section.objects.filter(created_date__lt=old_date).count()}

    list_obj = Section.objects.filter(created_date__lt=old_date)
    for obj in list_obj:
        print "Deleting Section => : %s" % obj
        obj.delete()

    # Delete old Surveys
    print "Deleting old Surveys => number to delete: %(count)s" % \
        {'count': Survey.objects.filter(created_date__lt=old_date).count()}

    list_obj = Survey.objects.filter(created_date__lt=old_date)
    for obj in list_obj:
        print "Deleting Survey => : %s" % obj
        obj.delete()

    # -------------------------------
    print "The cleaning is finished!"


"""
    DELETE FROM "dialer_campaign_phonebook" WHERE campaign_id IN
        (SELECT id FROM "dialer_campaign" WHERE "dialer_campaign"."created_date" < '2014-07-31 18:57:57');
    DELETE FROM "dialer_campaign" WHERE "dialer_campaign"."created_date" < '2014-07-31 18:57:57';
    DELETE FROM "dialer_subscriber" WHERE "dialer_subscriber"."created_date" < '2014-07-31 18:57:57';
    DELETE FROM "dialer_callrequest" WHERE "dialer_callrequest"."created_date" < '2014-07-31 18:57:57';
    DELETE FROM "dialer_cdr" WHERE "dialer_cdr"."starting_date" < '2014-07-31 18:57:57';
    DELETE FROM "survey_resultaggregate" WHERE "survey_resultaggregate"."created_date" < '2014-07-31 18:57:57';
    DELETE FROM "survey_result" WHERE "survey_result"."created_date" < '2014-07-31 18:57:57';
    DELETE FROM "survey_branching" WHERE "survey_branching"."created_date" < '2014-07-31 18:57:57';
    DELETE FROM "survey_section" WHERE "survey_section"."created_date" < '2014-07-31 18:57:57';
    DELETE FROM "survey_survey" WHERE "survey_survey"."created_date" < '2014-07-31 18:57:57';

    DELETE FROM "dialer_contact" WHERE "created_date" < '2014-07-31 18:57:57';
    DELETE FROM "dialer_phonebook" WHERE "created_date" < '2014-07-31 18:57:57';

"""
