from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from dialer_campaign.models import *
from django.db import IntegrityError


class Command(BaseCommand):
    # Use : create_contact '13843453|1' '324242|1'
    args = 'phonenumber|phonebook_id' 'phonenumber|phonebook_id'
    help = "Creates a new contact for a given phonenumber \
            and phonebook \n---------------------------------\n"

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
                print 'Can\'t find this Phonebook : %s' % myphonebook_id
                return False

            try:
                new_contact = Contact.objects.create(
                                    contact=myphonenumber,
                                    phonebook=obj_phonebook)
            except IntegrityError:
                print ("The contact is duplicated!")
                return False

            print "Contact created id:%s" % new_contact.id
