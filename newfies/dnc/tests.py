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

from django.test import TestCase
from dnc.models import DNC, DNCContact


class DNCModel(TestCase):
    """Test DNC model"""

    fixtures = ['auth_user.json']

    def setUp(self):
        self.user = User.objects.get(username='admin')
        self.dnc = DNC(
            name='test_dnc',
            user=self.user
        )
        self.dnc.save()

        self.assertTrue(self.dnc.__unicode__())
        self.dnc_contact = DNCContact(
            dnc=self.dnc,
            phone_number='123456'
        )
        self.dnc_contact.save()

        self.assertTrue(self.dnc_contact.__unicode__())

    def test_name(self):
        self.assertEqual(self.dnc.name, "test_dnc")
        self.assertEqual(self.dnc_contact.phone_number, "123456")

    def teardown(self):
        self.dnc.delete()
        self.dnc_contact.delete()
