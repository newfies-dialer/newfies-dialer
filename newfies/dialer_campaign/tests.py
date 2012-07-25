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
from dialer_campaign.models import Phonebook, Contact, Campaign, CampaignSubscriber
from django.contrib.contenttypes.models import ContentType
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


class DialerCampaignView(BaseAuthenticatedClient):
    """
    TODO: Add documentation
    """

    def test_dialer_campaign(self):
        response = self.client.get("/admin/dialer_campaign/phonebook/")
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get("/admin/dialer_campaign/phonebook/add/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/admin/dialer_campaign/contact/")
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get("/admin/dialer_campaign/contact/add/")
        self.assertEqual(response.status_code, 200)
        response =\
            self.client.get('/admin/dialer_campaign/contact/import_contact/')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/admin/dialer_campaign/campaign/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/admin/dialer_campaign/campaign/add/')
        self.failUnlessEqual(response.status_code, 200)

        response =\
            self.client.get('/admin/dialer_campaign/campaignsubscriber/')
        self.failUnlessEqual(response.status_code, 200)
        response =\
            self.client.get('/admin/dialer_campaign/campaignsubscriber/add/')
        self.failUnlessEqual(response.status_code, 200)


class DialerCampaignCustomerView(BaseAuthenticatedClient):
    """
    TODO: Add documentation
    """
    fixtures = ['gateway.json', 'auth_user', 'voiceapp', 'phonebook',
                'contact', 'campaign', 'campaign_subscriber']

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


class DialerCampaignModel(object):
    """
    TODO: Add documentation
    """
    def setup(self):
        self.user = User.objects.get(username='admin')
        # Phonebook model
        self.phonebook = Phonebook(
            name='test_phonebook',
            user=self.user,
            )
        self.phonebook.save()
        # Contact model
        self.contact = Contact(
            phonebook=self.phonebook,
            contact=123456789,
        )
        self.contact.save()
        # Campaign model
        try:
            content_type_id = ContentType.objects.get(model='voiceapp').id
        except:
            content_type_id = 1

        self.campaign = Campaign(
            name="sample_campaign",
            user=self.user,
            aleg_gateway_id=1,
            content_type_id=content_type_id,
            object_id=1,
        )
        self.campaign.save()
        # CampaignSubscriber model
        self.campaignsubscriber = CampaignSubscriber(
            contact=self.contact,
            campaign=self.campaign,
            count_attempt=0,
            status=1,
        )
        self.campaignsubscriber.save()

    def test_name(self):
        nt.assert_equal(self.phonebook.name, "test_phonebook")
        nt.assert_equal(self.contact.phonebook, self.phonebook)
        nt.assert_equal(self.campaign.name, "sample_campaign")
        nt.assert_equal(self.campaignsubscriber.contact, self.contact)

    def teardown(self):
        self.phonebook.delete()
        self.contact.delete()
        self.campaign.delete()
        self.campaignsubscriber.delete()
