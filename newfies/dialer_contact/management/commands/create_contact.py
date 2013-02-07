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
from dialer_contact.models import Phonebook, Contact
from django.db import IntegrityError
from random import choice


class Command(BaseCommand):
    # Use : create_contact '1|100' '2|50'
    args = _('"phonebook_id|no_of_record" "phonebook_id|no_of_record"')
    help = _("Creates new contacts for a given phonebook and no of records")

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
                print _('Can\'t find this Phonebook : %(id)s' % {'id': myphonebook_id})
                return False

            try:
                length = 5
                chars = "1234567890"
                for i in range(1, int(no_of_record) + 1):
                    phone_no = ''.join([choice(chars) for i in range(length)])
                    Contact.objects.create(
                        contact=phone_no,
                        phonebook=obj_phonebook)
                print _("No of Contact created : %(count)s" % {'count': no_of_record})
            except IntegrityError:
                print _("Duplicate contact!")
                return False
