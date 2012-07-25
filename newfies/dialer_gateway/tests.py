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
from dialer_gateway.models import Gateway
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


class TestGatewayView(BaseAuthenticatedClient):
    """
    TODO: Add documentation
    """
    def setup(self):
        self.client = Client()

    def test_gateway_index(self):
        response = self.client.get("/admin/dialer_gateway/gateway/")
        self.assertEqual(response.status_code, 200)

    def test_gateway_add(self):
        response = self.client.get("/admin/dialer_gateway/gateway/add/")
        self.assertEqual(response.status_code, 200)


class TestGatewayModel(object):
    """
    TODO: Add documentation
    """
    def setup(self):
        self.gateway = Gateway(
            name='test gateway',
            status=1,
            )
        self.gateway.set_name("MyGateway")
        self.gateway.save()

    def test_name(self):
        nt.assert_equal(self.gateway.name, "MyGateway")

    def teardown(self):
        self.gateway.delete()
