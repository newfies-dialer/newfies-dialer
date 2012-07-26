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
from common.test_utils import BaseAuthenticatedClient
from django.contrib.contenttypes.models import ContentType
from dialer_cdr.models import Callrequest, VoIPCall
import nose.tools as nt


class DialerCdrView(BaseAuthenticatedClient):
    """Test cases for Callrequest, VoIPCall Admin Interface."""

    def test_admin(self):
        """Test Function to check Newfies-Dialer Admin pages"""
        response = self.client.get('/admin/dialer_cdr/callrequest/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/dialer_cdr/callrequest/add/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/dialer_cdr/voipcall/')
        self.failUnlessEqual(response.status_code, 200)


class DialerCdrCustomerView(BaseAuthenticatedClient):
    """Test cases for Callrequest, VoIPCall Customer Interface."""

    def test_customer(self):
        """Test Function to check VoIP call report"""
        response = self.client.get('/voipcall_report/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
        'frontend/report/voipcall_report.html')


class DialerCdrModel(object):
    """Test Callrequest, VoIPCall models"""

    def setup(self):
        self.user =\
            User.objects.get(username='admin')

        try:
            content_type_id = ContentType.objects.get(model='voiceapp').id
        except:
            content_type_id = 1

        # Callrequest model
        self.callrequest = Callrequest(
            call_type=1,
            status=1,
            user=self.user,
            phone_number='123456',
            campaign_subscriber_id=1,
            campaign_id=1,
            aleg_gateway_id=1,
            content_type_id=content_type_id,
            object_id=1,

        )
        self.callrequest.save()

        # VoIPCall model
        self.voipcall = VoIPCall(
            user=self.user,
            used_gateway_id=1,
            callrequest=self.callrequest,
            phone_number='123456',
            leg_type=1
        )
        self.voipcall.save()


    def test_name(self):
        nt.assert_equal(self.callrequest.phone_number, "123456")
        nt.assert_equal(self.voipcall.phone_number, "123456")


    def teardown(self):
        self.callrequest.delete()
        self.voipcall.delete()


