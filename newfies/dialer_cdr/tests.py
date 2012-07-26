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
from django.contrib.contenttypes.models import ContentType
from dialer_cdr.models import Callrequest, VoIPCall
import nose.tools as nt
import base64


class BaseAuthenticatedClient(TestCase):
    """Common Authentication"""

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


class DialerCdrView(BaseAuthenticatedClient):
    """Test cases for Admin Interface."""

    def test_admin_newfies(self):
        """Test Function to check Newfies-Dialer Admin pages"""
        response = self.client.get('/admin/dialer_cdr/callrequest/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/dialer_cdr/callrequest/add/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/dialer_cdr/voipcall/')
        self.failUnlessEqual(response.status_code, 200)


class DialerCdrCustomerView(BaseAuthenticatedClient):
    """Test cases for Newfies-Dialer Customer Interface."""

    def test_voip_call_report(self):
        """Test Function to check VoIP call report"""
        response = self.client.get('/voipcall_report/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
        'frontend/report/voipcall_report.html')


class TestCallrequestModel(object):
    """
    TODO: Add documentation
    """
    fixtures = ['dialer_setting.json', 'gateway.json', 'auth_user.json']

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


