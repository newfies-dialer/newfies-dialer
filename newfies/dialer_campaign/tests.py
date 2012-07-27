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
from dialer_campaign.models import Phonebook, Contact, Campaign, \
                            CampaignSubscriber
from common.utils import BaseAuthenticatedClient
import nose.tools as nt


class DialerCampaignView(BaseAuthenticatedClient):
    """Test cases for Phonebook, Contact, Campaign, CampaignSubscriber
       Admin Interface.
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
    """Test cases for Phonebook, Contact, Campaign, CampaignSubscriber
       Customer Interface.
    """

    fixtures = ['dialer_setting.json', 'auth_user.json', 'gateway.json',
                'voiceapp.json', 'phonebook.json', 'contact.json',
                'campaign.json', 'campaign_subscriber.json']

    def test_phonebook_view_list(self):
        """Test Function to check phonebook list"""
        response = self.client.get('/phonebook/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/phonebook/list.html')

    def test_phonebook_view_add(self):
        """Test Function to check add phonebook"""
        response = self.client.get('/phonebook/add/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/phonebook/add/',
            data={
                'name': 'My Phonebook',
                'description': 'phonebook',
                'user': self.user
            })
        self.assertEqual(response.status_code, 302)

    def test_phonebook_view_update(self):
        response = self.client.get('/phonebook/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/phonebook/change.html')

    def test_contact_view_list(self):
        """Test Function to check Contact list"""
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/contact/list.html')

    def test_contact_view_add(self):
        """Test Function to check add Contact"""
        response = self.client.get('/contact/add/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/contact/add/',
            data={'phonebook_id': '1', 'contact': '1234',
                  'last_name': 'xyz', 'first_name': 'abc',
                  'status': '1'})
        self.assertEqual(response.status_code, 200)

    def test_contact_view_update(self):
        """Test Function to check update Contact"""
        response = self.client.get('/contact/1/')
        self.assertTemplateUsed(response, 'frontend/contact/change.html')

    def test_contact_view_import(self):
        """Test Function to check import Contact"""
        response = self.client.get('/contact/import/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                'frontend/contact/import_contact.html')

    def test_campaign_view_list(self):
        """Test Function to check campaign list"""
        response = self.client.get('/campaign/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/campaign/list.html')

    def test_campaign_view_add(self):
        """Test Function to check add campaign"""
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
    """Test Phonebook, Contact, Campaign, CampaignSubscriber models"""

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
        nt.assert_equal(self.phonebook.name, 'test_phonebook')
        nt.assert_equal(self.contact.phonebook, self.phonebook)
        nt.assert_equal(self.campaign.name, "sample_campaign")
        nt.assert_equal(self.campaignsubscriber.contact, self.contact)

    def teardown(self):
        self.phonebook.delete()
        self.contact.delete()
        self.campaign.delete()
        self.campaignsubscriber.delete()
