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
from dialer_campaign.models import Campaign, CampaignSubscriber
from dialer_campaign.forms import CampaignForm
from common.utils import BaseAuthenticatedClient


class DialerCampaignView(BaseAuthenticatedClient):
    """Test cases for Campaign, CampaignSubscriber Admin Interface."""

    def test_admin_campaign_view_list(self):
        """Test Function to check admin campaign list"""
        response = self.client.get('/admin/dialer_campaign/campaign/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_campaign_view_add(self):
        """Test Function to check admin campaign add"""
        response = self.client.get('/admin/dialer_campaign/campaign/add/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_campaignsubscriber_view_list(self):
        """Test Function to check admin campaignsubscriber list"""
        response =\
            self.client.get('/admin/dialer_campaign/campaignsubscriber/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_campaignsubscriber_view_add(self):
        """Test Function to check admin campaignsubscriber add"""
        response =\
            self.client.get('/admin/dialer_campaign/campaignsubscriber/add/')
        self.failUnlessEqual(response.status_code, 200)


class DialerCampaignCustomerView(BaseAuthenticatedClient):
    """Test cases for Campaign, CampaignSubscriber Customer Interface."""

    fixtures = ['dialer_setting.json', 'auth_user.json', 'gateway.json',
                'voiceapp.json', 'phonebook.json', 'contact.json',
                'campaign.json', 'campaign_subscriber.json']

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


class DialerCampaignModel(TestCase):
    """Test Campaign, CampaignSubscriber models"""

    fixtures = ['gateway.json', 'voiceapp.json', 'auth_user.json',
                'dialer_setting.json', 'contenttype.json',
                'phonebook.json', 'contact.json',
                'campaign.json', 'campaign_subscriber.json',
                'user_profile.json']

    def setUp(self):
        self.user = User.objects.get(username='admin')

        # Campaign model
        try:
            self.content_type_id = ContentType.objects.get(model='voiceapp').id
        except:
            self.content_type_id = 1

        self.campaign = Campaign(
            name="sample_campaign",
            user=self.user,
            aleg_gateway_id=1,
            content_type_id=self.content_type_id,
            object_id=1,
        )
        self.campaign.save()

        # CampaignSubscriber model
        self.campaignsubscriber = CampaignSubscriber(
            contact_id=1,
            campaign=self.campaign,
            count_attempt=0,
            status=1,
        )
        self.campaignsubscriber.save()

    def test_campaign_form(self):
        self.assertEqual(self.campaign.name, "sample_campaign")
        self.assertEqual(self.campaignsubscriber.campaign, self.campaign)

        form = CampaignForm(self.user)

        obj = form.save(commit=False)
        obj.name="new_campaign"
        obj.user = self.user
        obj.phonebook_id = 1
        obj.aleg_gateway_id=1
        obj.content_type_id=self.content_type_id
        obj.object_id=1
        obj.save()

        form = CampaignForm(self.user, instance=self.campaign)
        self.assertTrue(isinstance(form.instance, Campaign))


    def teardown(self):
        self.campaign.delete()
        self.campaignsubscriber.delete()
