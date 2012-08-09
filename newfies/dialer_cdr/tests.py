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
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from common.utils import BaseAuthenticatedClient
from dialer_cdr.models import Callrequest, VoIPCall
from dialer_cdr.forms import VoipSearchForm
from dialer_cdr.views import export_voipcall_report, voipcall_report
from dialer_cdr.tasks import init_callrequest, \
                             dummy_testcall, \
                             dummy_test_answerurl, \
                             dummy_test_hangupurl
from datetime import datetime


class DialerCdrView(BaseAuthenticatedClient):
    """Test cases for Callrequest, VoIPCall Admin Interface."""

    def test_admin_callrequest_view_list(self):
        """Test Function to check admin callrequest list"""
        response = self.client.get('/admin/dialer_cdr/callrequest/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_callrequest_view_add(self):
        """Test Function to check admin callrequest add"""
        response = self.client.get('/admin/dialer_cdr/callrequest/add/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_voipcall_view_list(self):
        """Test Function to check admin voipcall list"""
        response = self.client.get('/admin/dialer_cdr/voipcall/')
        self.failUnlessEqual(response.status_code, 200)


class DialerCdrCustomerView(BaseAuthenticatedClient):
    """Test cases for Callrequest, VoIPCall Customer Interface."""

    def test_customer_voipcall(self):
        """Test Function to check VoIP call report"""
        response = self.client.get('/voipcall_report/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'], VoipSearchForm())
        self.assertTemplateUsed(response,
            'frontend/report/voipcall_report.html')

        response = self.client.post('/voipcall_report/',
                                    data={'from_date': datetime.now(),
                                          'to_date': datetime.now()})
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/voipcall_report/')
        request.user = self.user
        request.session = {}
        response = voipcall_report(request)
        self.assertEqual(response.status_code, 200)


class DialerCdrCeleryTaskTestCase(TestCase):
    """Test cases for celery task"""

    fixtures = ['gateway.json', 'voiceapp.json', 'auth_user.json',
                'dialer_setting.json', 'contenttype.json',
                'phonebook.json', 'contact.json',
                'campaign.json', 'campaign_subscriber.json',
                'callrequest.json', 'user_profile.json']

    def test_init_callrequest(self):
        """Test that the ``init_callrequest``
        task runs with no errors, and returns the correct result."""
        result = init_callrequest.delay(1, 1)
        self.assertEqual(result.successful(), False)

    def test_dummy_testcall(self):
        """Test that the ``dummy_testcall``
        periodic task runs with no errors, and returns the correct result."""
        result = dummy_testcall.delay(1, '1234567890', 1)
        self.assertEqual(result.successful(), False)

    def test_dummy_test_answerurl(self):
        """Test that the ``dummy_test_answerurl``
        task runs with no errors, and returns the correct result."""
        result = dummy_test_answerurl.delay('e8fee8f6-40dd-11e1-964f-000c296bd875')
        self.assertEqual(result.successful(), False)

    def test_dummy_test_hangupurl(self):
        """Test that the ``dummy_test_hangupurl``
        periodic task runs with no errors, and returns the correct result."""
        result = dummy_test_hangupurl.delay('e8fee8f6-40dd-11e1-964f-000c296bd875')
        self.assertEqual(result.successful(), False)


class DialerCdrModel(TestCase):
    """Test Callrequest, VoIPCall models"""

    fixtures = ['gateway.json', 'auth_user.json', 'contenttype.json',
                'phonebook.json', 'contact.json',
                'campaign.json', 'campaign_subscriber.json',
                'callrequest.json']

    def setUp(self):
        self.user = User.objects.get(username='admin')

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
        self.assertEqual(self.callrequest.phone_number, "123456")
        self.assertEqual(self.voipcall.phone_number, "123456")

    def teardown(self):
        self.callrequest.delete()
        self.voipcall.delete()
