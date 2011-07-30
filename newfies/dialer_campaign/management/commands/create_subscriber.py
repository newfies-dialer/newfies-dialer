from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from dialer_campaign.models import *
from django.db import IntegrityError
from dialer_campaign.tasks import collect_subscriber


class Command(BaseCommand):
    args = '<phonenumber|phonebook_id, phonenumber|phonebook_id, \
             phonenumber|phonebook_id,...>'
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

            try:
                obj_campaign = Campaign.objects.get(phonebook=obj_phonebook)
            except:
                print 'Can\'t find a Campaign with this phonebook'
                return False

            print "Launch Task : collect_subscriber(%s)" % str(obj_campaign.id)
            collect_subscriber.delay(obj_campaign.id)
 