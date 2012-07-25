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
import base64
import simplejson


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


class AdminTestCase(TestCase):
    """Test cases for Admin Interface."""

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

    def test_admin_index(self):
        """Test Function to check Admin index page"""
        response = self.client.get('/admin/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/base_site.html')
        response = self.client.login(username=self.user.username,
                                     password='admin')
        self.assertEqual(response, True)

    def test_admin_newfies(self):
        """Test Function to check Newfies-Dialer Admin pages"""
        response = self.client.get('/admin/auth/')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/admin/dialer_settings/')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/admin/dialer_campaign/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/dialer_campaign/contact/')
        self.failUnlessEqual(response.status_code, 200)
        response = \
        self.client.get('/admin/dialer_campaign/contact/import_contact/')
        self.failUnlessEqual(response.status_code, 200)
        response = \
        self.client.get('/admin/dialer_campaign/campaignsubscriber/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/dialer_campaign/campaign/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/dialer_campaign/phonebook/')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/admin/dialer_cdr/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/dialer_cdr/voipcall/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/dialer_cdr/callrequest/')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/admin/dialer_gateway/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/dialer_gateway/gateway/')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/admin/voice_app/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/voice_app/voiceapp/')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/admin/survey/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/survey/surveyapp/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/survey/surveyquestion/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/survey/surveyresponse/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/survey/surveycampaignresult/')
        self.failUnlessEqual(response.status_code, 200)


class CustomerPanelTestCase(BaseAuthenticatedClient):
    """Test cases for Newfies-Dialer Customer Interface."""
    fixtures = ['gateway.json', 'auth_user', 'voiceapp', 'phonebook',
                'contact', 'campaign', 'campaign_subscriber', 'survey',
                'surve_question', 'survey_response']

    def test_index(self):
        """Test Function to check customer index page"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/index.html')
        response = self.client.post('/login/',
                    {'username': 'userapi',
                     'password': 'passapi'})
        self.assertEqual(response.status_code, 200)

    def test_dashboard(self):
        """Test Function to check customer dashboard"""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/dashboard.html')

    def test_voiceapp_view(self):
        """Test Function to check voiceapp"""
        response = self.client.get('/voiceapp/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'frontend/voiceapp/list.html')
        response = self.client.get('/voiceapp/add/')
        self.assertTemplateUsed(response,
                                'frontend/voiceapp/change.html')
        response = self.client.get('/voiceapp/1/')
        self.assertEqual(response.status_code, 200)

    def test_phonebook_view(self):
        """Test Function to check phonebook"""
        response = self.client.get('/phonebook/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'frontend/phonebook/list.html')
        response = self.client.get('/phonebook/add/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/phonebook/add/',
                   data={'name': 'My Phonebook', 'description': 'phonebook',
                         'user': self.user})
        response = self.client.get('/phonebook/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'frontend/phonebook/change.html')

    def test_contact_view(self):
        """Test Function to check Contact"""
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'frontend/contact/list.html')
        response = self.client.get('/contact/add/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/contact/add/',
                   data={'phonebook_id': '1', 'contact': '1234',
                         'last_name': 'xyz', 'first_name': 'abc',
                         'status': '1'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/contact/1/')
        self.assertTemplateUsed(response,
                                'frontend/contact/change.html')
        response = self.client.get('/contact/import/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'frontend/contact/import_contact.html')

    def test_campaign_view(self):
        """Test Function to check campaign"""
        response = self.client.get('/campaign/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'frontend/campaign/list.html')
        response = self.client.post('/campaign/add/', data={
                    "name": "mylittlecampaign",
                    "description": "xyz",
                    "startingdate": "1301392136.0",
                    "expirationdate": "1301332136.0",
                    "frequency": "20",
                    "callmaxduration": "50",
                    "maxretry": "3",
                    "intervalretry": "3000",
                    "calltimeout": "60",
                    "aleg_gateway": "1",
                    "content_object": "type:30-id:1",
                    "extra_data": "2000"})
        self.assertEqual(response.status_code, 302)

    def test_voip_call_report(self):
        """Test Function to check VoIP call report"""
        response = self.client.get('/voipcall_report/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
        'frontend/report/voipcall_report.html')

    def test_user_settings(self):
        """Test Function to check User settings"""
        response = self.client.get('/user_detail_change/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
        'frontend/registration/user_detail_change.html')

    def test_audio_view(self):
        """Test Function audio view"""
        response = self.client.get('/audio/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
            'frontend/audio/audio_list.html')
        response = self.client.get('/audio/add/')
        self.assertEqual(response.status_code, 200)

    def test_survey_view(self):
        """Test Function survey view"""
        response = self.client.get('/survey/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'frontend/survey/survey_list.html')
        response = self.client.get('/survey/add/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'frontend/survey/survey_change.html')
        response = self.client.get('/survey/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'frontend/survey/survey_change.html')
        response = self.client.get('/survey_report/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'frontend/survey/survey_report.html')


class ForgotPassTestCase(TestCase):
    """Test cases for Newfies-Dialer Customer Interface. for forgot password"""

    def test_check_password_reset(self):
        """Test Function to check password reset"""
        response = self.client.get('/password_reset/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
        'frontend/registration/password_reset_form.html')

        response = self.client.get('/password_reset/done/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
        'frontend/registration/password_reset_done.html')

        response = self.client.get(
                   '/reset/1-2xc-5791af4cc6b67e88ce8e/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
        'frontend/registration/password_reset_confirm.html')

        response = self.client.get('/reset/done/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
        'frontend/registration/password_reset_complete.html')
