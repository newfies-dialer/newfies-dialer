from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from dialer_campaign.models import *
from django.db import IntegrityError


class Command(BaseCommand):
    # Use : create_contact '1|100' '2|50'
    args = '"phonebook_id|no_of_record" "phonebook_id|no_of_record"'
    help = "Creates new contacts for a given phonebook and no of records \
            \n-----------------------------------------------------------\n"

    def handle(self, *args, **options):
        """Note that subscriber created this way are only for devel purposes"""

        for newinst in args:
            print newinst
            res = newinst.split('|')
            myphonebook_id = res[0]
            no_of_record = res[1]

            try:
                obj_phonebook = Phonebook.objects.get(id=myphonebook_id)
            except:
                print 'Can\'t find this Phonebook : %s' % myphonebook_id
                return False

            try:
                length=5
                chars="1234567890"
                for i in range(1, int(no_of_record) + 1):
                    phone_no = '' . join([choice(chars) for i in range(length)])
                    new_contact = Contact.objects.create(
                                        contact=phone_no,
                                        phonebook=obj_phonebook)
                print "No of Contact created : %d" % int(no_of_record)
            except IntegrityError:
                print ("The contact is duplicated!")
                return False
