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

from django.test import TestCase
from dialer_settings.models import DialerSetting


class DialerSettingModel(TestCase):
    """Test DialerSetting model"""

    fixtures = ['auth_user.json']

    def setUp(self):
        self.dialer_setting = DialerSetting(
            name='test_setting',
            max_frequency=100,
            callmaxduration=1800,
            maxretry=3,
            max_calltimeout=45,
            max_cpg=10,
            max_subr_cpg=1000,
        )
        self.dialer_setting.save()

        self.assertTrue(self.dialer_setting.__unicode__())

    def test_name(self):
        self.assertEqual(self.dialer_setting.name, "test_setting")

    def teardown(self):
        self.dialer_setting.delete()
