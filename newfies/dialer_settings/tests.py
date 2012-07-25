#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.contrib.auth.models import User
from django.test import TestCase, Client
from dialer_settings.models import DialerSetting
import nose.tools as nt
import base64


class BaseAuthenticatedClient(TestCase):
    """Common Authentication to setup test"""

    def setUp(self):
        """To create admin user"""
        self.client = Client()
        self.user = \
        User.objects.create_user('admin', 'admin@world.com', 'admin')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.is_active = True
        self.user.save()
        auth = '%s:%s' % ('admin', 'admin')
        auth = 'Basic %s' % base64.encodestring(auth)
        auth = auth.strip()
        self.extra = {
            'HTTP_AUTHORIZATION': auth,
        }
        login = self.client.login(username='admin', password='admin')
        self.assertTrue(login)


class TestDialerSettingView(BaseAuthenticatedClient):
    """
    TODO: Add documentation
    """
    def setup(self):
        self.client = Client()

    def test_dialer_setting(self):
        response = self.client.get('/admin/dialer_settings/dialersetting/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get("/admin/dialer_settings/dialersetting/add/")
        self.assertEqual(response.status_code, 200)


class TestDialerSettingModel(object):
    """
    TODO: Add documentation
    """
    def setup(self):
        self.dialer_setting = DialerSetting(
            name='test setting',
            max_frequency=100,
            callmaxduration=1800,
            maxretry=3,
            max_calltimeout=45,
            max_number_campaign=10,
            max_number_subscriber_campaign=1000,
            )
        self.dialer_setting.save()

    def test_name(self):
        nt.assert_equal(self.dialer_setting.name, "test setting")

    def teardown(self):
        self.dialer_setting.delete()
