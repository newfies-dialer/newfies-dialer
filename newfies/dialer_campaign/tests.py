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
from django.template import Template, Context, TemplateSyntaxError
from django.core.management import call_command
from django.test import TestCase
from dialer_contact.models import Phonebook
from dialer_campaign.models import Campaign, CampaignSubscriber
from dialer_campaign.forms import CampaignForm
from dialer_campaign.views import campaign_list, campaign_add, \
                                  campaign_change, campaign_del, \
                                  campaign_grid, notify_admin,\
                                  update_campaign_status_admin,\
                                  update_campaign_status_cust
from dialer_campaign.tasks import check_campaign_pendingcall,\
                                  campaign_running,\
                                  collect_subscriber,\
                                  campaign_expire_check
from utils.helper import grid_test_data
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

        response = self.client.post(
            '/admin/dialer_campaign/campaign/add/',
            data={
                "name": "mycampaign_admin",
                "description": "xyz",
                "startingdate": "1301392136.0",
                "expirationdate": "1301332136.0",
                "frequency": "20",
                "callmaxduration": "50",
                "maxretry": "3",
                "intervalretry": "3000",
                "calltimeout": "60",
                "aleg_gateway": "1",
                "user": "1",
                "content_object": "type:30-id:1",
                "extra_data": "2000"})
        self.assertEqual(response.status_code, 200)

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

        response = self.client.post(
            '/admin/dialer_campaign/campaignsubscriber/add/',
            data={
                "status": "1",
                "campaign": "1",
                "duplicate_contact": "1234567",
                "count_attempt": "1",
                })
        self.assertEqual(response.status_code, 200)


class DialerCampaignCustomerView(BaseAuthenticatedClient):
    """Test cases for Campaign, CampaignSubscriber Customer Interface."""

    fixtures = ['dialer_setting.json', 'auth_user.json', 'gateway.json',
                'voiceapp.json', 'phonebook.json', 'contact.json',
                'campaign.json', 'campaign_subscriber.json']

    def test_campaign_view_list(self):
        """Test Function to check campaign list"""
        request = self.factory.post('/campaign_grid/', grid_test_data)
        request.user = self.user
        request.session = {}
        response = campaign_grid(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/campaign/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/campaign/list.html')

        request = self.factory.get('/campaign/')
        request.user = self.user
        request.session = {}
        response = campaign_list(request)
        self.assertEqual(response.status_code, 200)

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
            "extra_data": "2000"}, follow=True)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/campaign/add/', {
            "name": "mycampaign",
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
            "extra_data": "2000"}, follow=True)

        request.user = self.user
        request.session = {}
        response = campaign_add(request)
        self.assertEqual(response['Location'], '/campaign/')
        self.assertEqual(response.status_code, 302)

        out = Template(
                '{% block content %}'
                    '{% if msg %}'
                        '{{ msg|safe }}'
                    '{% endif %}'
                    '{% if error_msg %}'
                        '{{ error_msg|safe }}'
                    '{% endif %}'
                '{% endblock %}'
            ).render(Context({
                'msg': request.session.get('msg'),
                'error_msg': request.session.get('error_msg'),
            }))
        self.assertEqual(out,
            'In order to add a campaign, '
            'you need to have your settings configured properly, '
            'please contact the admin.')

    def test_campaign_view_update(self):
        """Test Function to check update campaign"""
        request = self.factory.post('/campaign/1/', {
            "name": "Sample campaign",
            "content_object": "type:30-id:1",
            }, follow=True)
        request.user = self.user
        request.session = {}
        response = campaign_change(request, 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/campaign/')

        request = self.factory.post('/campaign/1/', {
            'delete': True
        }, follow=True)
        request.user = self.user
        request.session = {}
        response = campaign_change(request, 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/campaign/')


    def test_campaign_view_delete(self):
        """Test Function to check delete campaign"""
        # delete campaign through campaign_change
        request = self.factory.post('/campaign/del/1/', follow=True)
        request.user = self.user
        request.session = {}
        response = campaign_del(request, 1)
        self.assertEqual(response['Location'], '/campaign/')
        self.assertEqual(response.status_code, 302)

        out = Template(
                '{% block content %}'
                    '{% if msg %}'
                        '{{ msg|safe }}'
                    '{% endif %}'
                '{% endblock %}'
            ).render(Context({
                'msg': request.session.get('msg'),
            }))
        self.assertEqual(out, '"Sample campaign" is deleted.')

        request = self.factory.post('/campaign/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = campaign_del(request, 0)
        self.assertEqual(response['Location'], '/campaign/')
        self.assertEqual(response.status_code, 302)

    def test_notify_admin(self):
        """Test Function to check notify_admin"""
        request = self.factory.post('/notify/admin/', follow=True)
        request.user = self.user
        request.session = {}
        request.session['has_notified'] = False
        response = notify_admin(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/dashboard/')

    def test_update_campaign_status_admin(self):
        request = self.factory.post('update_campaign_status_admin/1/1/',
            follow=True)
        request.user = self.user
        request.session = {}
        response = update_campaign_status_admin(request, 1, 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],
            '/admin/dialer_campaign/campaign/')

    def test_update_campaign_status_admin(self):
        request = self.factory.post(
            'campaign/update_campaign_status_cust/1/1/',
            follow=True)
        request.user = self.user
        request.session = {}
        response = update_campaign_status_cust(request, 1, 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],
            '/campaign/')

class DialerCampaignCeleryTaskTestCase(TestCase):
    """Test cases for celery task"""

    fixtures = ['gateway.json', 'voiceapp.json', 'auth_user.json',
                'dialer_setting.json', 'contenttype.json',
                'phonebook.json', 'contact.json',
                'campaign.json', 'campaign_subscriber.json',
                'user_profile.json']

    #def test_check_campaign_pendingcall(self):
    #    """Test that the ``check_campaign_pendingcall``
    #    task runs with no errors, and returns the correct result."""
    #    result = check_campaign_pendingcall.delay(1)
    #    self.assertEqual(result.successful(), True)

    def test_campaign_running(self):
        """Test that the ``campaign_running``
        periodic task runs with no errors, and returns the correct result."""
        result = campaign_running.delay()
        self.assertEqual(result.successful(), True)

    def test_collect_subscriber(self):
        """Test that the ``collect_subscriber``
        task runs with no errors, and returns the correct result."""
        result = collect_subscriber.delay(1)
        self.assertEqual(result.successful(), True)

    def test_campaign_expire_check(self):
        """Test that the ``campaign_expire_check``
        periodic task runs with no errors, and returns the correct result."""
        result = campaign_expire_check.delay()
        self.assertEqual(result.successful(), True)


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

        # Test mgt command
        call_command("create_subscriber", "'123456|1, 546234|1")

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
