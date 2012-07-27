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

from common.utils import BaseAuthenticatedClient
from dialer_gateway.models import Gateway
import nose.tools as nt


class GatewayView(BaseAuthenticatedClient):
    """Test Function to check Gateway Admin pages"""

    def test_gateway(self):
        response = self.client.get("/admin/dialer_gateway/gateway/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/dialer_gateway/gateway/add/")
        self.assertEqual(response.status_code, 200)


class GatewayModel(object):
    """Test Gateway model"""

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
