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
from common.utils import BaseAuthenticatedClient
from dialer_gateway.models import Gateway
from dialer_gateway.utils import prepare_phonenumber


class GatewayView(BaseAuthenticatedClient):
    """Test Function to check Gateway Admin pages"""

    def test_admin_gateway_view_list(self):
        """Test Function to check admin gateway list"""
        response = self.client.get("/admin/dialer_gateway/gateway/")
        self.assertEqual(response.status_code, 200)

    def test_admin_gateway_view_add(self):
        """Test Function to check admin gateway add"""
        response = self.client.get("/admin/dialer_gateway/gateway/add/")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/admin/dialer_gateway/gateway/add/',
            data={
                "status": "1",
                "name": "Default_Gateway",
                "gateway_codecs": "PCMA,PCMU",
                "gateway_timeouts": "10,10",
                "gateway_retries": "2,1",
                "gateways": "user/,user",
            }, follow=True)
        self.assertEqual(response.status_code, 200)


class GatewayModel(TestCase):
    """Test Gateway model"""

    def setUp(self):
        self.gateway = Gateway(
            name='test gateway',
            status=2,
            removeprefix='94'
        )
        self.gateway.set_name("MyGateway")
        self.gateway.save()
        self.assertEqual(self.gateway.__unicode__(), u'MyGateway')

        response = prepare_phonenumber('9897525414', '91', '+', self.gateway.status)
        self.assertEqual(response, False)

        response = prepare_phonenumber('', '91', '+', self.gateway.status)
        self.assertEqual(response, False)

        response = prepare_phonenumber('+9897525414', '91', '+', self.gateway.status)
        self.assertEqual(response, False)

        self.gateway.status = 1
        self.gateway.save()
        response = prepare_phonenumber('9897525414', '91', '+', self.gateway.status)
        self.assertEqual(response, '919897525414')

    def test_name(self):
        self.assertEqual(self.gateway.name, "MyGateway")

    def teardown(self):
        self.gateway.delete()
