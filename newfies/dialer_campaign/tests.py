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

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase
from dialer_campaign.models import Campaign, Subscriber, \
    common_contact_authorization
from dialer_campaign.forms import CampaignForm
from dialer_campaign.views import campaign_list, campaign_add, \
    campaign_change, campaign_del, notify_admin, \
    update_campaign_status_admin, \
    get_url_campaign_status, campaign_duplicate, subscriber_list, \
    subscriber_export
from dialer_campaign.tasks import campaign_running, pending_call_processing,\
    collect_subscriber, campaign_expire_check
from dialer_settings.models import DialerSetting
from dialer_campaign.constants import SUBSCRIBER_STATUS
from common.utils import BaseAuthenticatedClient


class DialerCampaignView(BaseAuthenticatedClient):
    """Test cases for Campaign, Subscriber Admin Interface."""

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
                "sms_gateway": "",
                "user": "1",
                "content_object": "type:32-id:1",
                "extra_data": "2000"})
        self.assertEqual(response.status_code, 200)

    def test_admin_subscriber_view_list(self):
        """Test Function to check admin subscriber list"""
        response = self.client.get('/admin/dialer_campaign/subscriber/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_subscriber_view_add(self):
        """Test Function to check admin subscriber add"""
        response = self.client.get('/admin/dialer_campaign/subscriber/add/')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post(
            '/admin/dialer_campaign/subscriber/add/',
            data={
                "status": "1",
                "campaign": "1",
                "duplicate_contact": "1234567",
                "count_attempt": "1",
                "completion_count_attempt": "1",
            })
        self.assertEqual(response.status_code, 200)


class DialerCampaignCustomerView(BaseAuthenticatedClient):
    """Test cases for Campaign, Subscriber Customer Interface."""

    fixtures = ['auth_user.json', 'gateway.json', 'dialer_setting.json',
                'user_profile.json', 'phonebook.json', 'contact.json',
                'survey.json', 'dnc_list.json', 'dnc_contact.json',
                'campaign.json', 'subscriber.json']

    def test_campaign_view_list(self):
        """Test Function to check campaign list"""
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
        request = self.factory.get('/campaign/add/')
        request.user = self.user
        request.session = {}
        response = campaign_add(request)
        self.assertEqual(response.status_code, 200)

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
            "sms_gateway": "",
            "content_object": "type:43-id:1",
            "extra_data": "2000",
            "ds_user": self.user}, follow=True)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/campaign/add/', {
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
            "sms_gateway": "",
            "content_object": "type:43-id:1",
            "extra_data": "2000",
            "ds_user": self.user}, follow=True)
        request.user = self.user
        request.session = {}
        response = campaign_add(request)
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
            "sms_gateway": "",
            "content_object": "type:43-id:1",
            "extra_data": "2000",
            "ds_user": self.user}, follow=True)

        request.user = self.user
        request.session = {}
        response = campaign_add(request)
        self.assertEqual(response.status_code, 200)

    def test_campaign_view_update(self):
        """Test Function to check update campaign"""
        request = self.factory.post('/campaign/1/', {
            "name": "Sample campaign",
            "content_object": "type:43-id:1",
            "ds_user": self.user,
        }, follow=True)
        request.user = self.user
        request.session = {}
        response = campaign_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/campaign/1/', {'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        response = campaign_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_campaign_view_delete(self):
        """Test Function to check delete campaign"""
        # delete campaign through campaign_change
        request = self.factory.post('/campaign/del/1/', follow=True)
        request.user = self.user
        request.session = {}
        response = campaign_del(request, 1)
        self.assertEqual(response['Location'], '/campaign/')
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/campaign/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = campaign_del(request, 0)
        self.assertEqual(response['Location'], '/campaign/')
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/campaign/del/0/?stop_campaign=True', {'select': '1'})
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

    def test_campaign_duplicate(self):
        """Test duplicate campaign"""
        request = self.factory.get('campaign_duplicate/1/')
        request.user = self.user
        request.session = {}
        response = campaign_duplicate(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post(
            'campaign_duplicate/1/', {'name': 'duplicate', 'campaign_code': 'ZUXSA'},
            follow=True)
        request.user = self.user
        request.session = {}
        response = campaign_duplicate(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_subscriber_list(self):
        """Test Function to check subscriber list"""
        response = self.client.get('/subscribers/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/subscriber/list.html')

        request = self.factory.get('/subscribers/')
        request.user = self.user
        request.session = {}
        response = subscriber_list(request)
        self.assertEqual(response.status_code, 200)

    def test_subscriber_list_export(self):
        """Test Function to check subscriber list"""
        response = self.client.get('/subscribers/export_subscriber/?format=csv')
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/subscribers/export_subscriber/?format=xml')
        request.user = self.user
        request.session = {}
        response = subscriber_export(request)
        self.assertEqual(response.status_code, 200)


class DialerCampaignCeleryTaskTestCase(TestCase):
    """Test cases for celery task"""

    fixtures = ['auth_user.json', 'gateway.json',
                'dialer_setting.json', 'user_profile.json',
                'phonebook.json', 'contact.json', 'survey.json',
                'dnc_list.json', 'dnc_contact.json',
                'campaign.json', 'subscriber.json',
                ]

    def test_check_pending_call_processing(self):
        """Test that the ``check_campaign_pendingcall``
        task runs with no errors, and returns the correct result."""
        result = pending_call_processing.delay(1)
        self.assertEqual(result.successful(), True)

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
    """Test Campaign, Subscriber models"""

    fixtures = ['auth_user.json', 'gateway.json',
                'dialer_setting.json', 'user_profile.json',
                'phonebook.json', 'contact.json', 'survey.json',
                'dnc_list.json', 'dnc_contact.json',
                'campaign.json', 'subscriber.json',
                ]

    def setUp(self):
        self.user = User.objects.get(username='admin')

        # Campaign model
        try:
            self.content_type_id = ContentType.objects.get(model='survey_template').id
        except:
            self.content_type_id = 1

        self.campaign = Campaign(
            name="sample_campaign",
            user=self.user,
            aleg_gateway_id=1,
            content_type_id=self.content_type_id,
            object_id=1,
            status=1
        )
        self.campaign.save()
        self.assertEqual(self.campaign.__unicode__(), u'sample_campaign')

        # Subscriber model
        self.subscriber = Subscriber(
            contact_id=1,
            campaign=self.campaign,
            count_attempt=0,
            completion_count_attempt=0,
            status=1
        )
        self.subscriber.save()
        self.assertTrue(self.subscriber.__unicode__())

        # Test mgt command
        call_command("create_subscriber", "123456|1")

        call_command("create_subscriber", "123456|3")

    def test_campaign_form(self):
        self.assertEqual(self.campaign.name, "sample_campaign")

        Campaign.objects.get_running_campaign()
        Campaign.objects.get_expired_campaign()
        dialersetting = DialerSetting.objects.get(pk=1)
        #self.user.get_profile().dialersetting
        common_contact_authorization(dialersetting, '1234567890')

        # status = 1
        self.campaign.update_campaign_status()
        get_url_campaign_status(self.campaign.pk, self.campaign.status)

        self.campaign.status = 2
        self.campaign.save()
        self.campaign.update_campaign_status()
        get_url_campaign_status(self.campaign.pk, self.campaign.status)

        self.campaign.status = 3
        self.campaign.save()
        self.campaign.update_campaign_status()
        get_url_campaign_status(self.campaign.pk, self.campaign.status)

        self.campaign.status = 4
        self.campaign.save()
        self.campaign.update_campaign_status()
        get_url_campaign_status(self.campaign.pk, self.campaign.status)

        self.campaign.is_authorized_contact(dialersetting, '123456789')
        self.campaign.get_active_max_frequency()
        self.campaign.get_active_callmaxduration()
        self.campaign.get_active_contact()
        self.campaign.progress_bar()
        self.campaign.subscriber_detail()
        self.campaign.get_pending_subscriber_update(10, SUBSCRIBER_STATUS.IN_PROCESS)

        self.assertEqual(self.subscriber.campaign, self.campaign)

        form = CampaignForm(self.user)
        obj = form.save(commit=False)
        obj.name = "new_campaign"
        obj.user = self.user
        obj.phonebook_id = 1
        obj.aleg_gateway_id = 1
        obj.content_type_id = self.content_type_id
        obj.object_id = 1
        obj.save()

        form = CampaignForm(self.user, instance=self.campaign)
        self.assertTrue(isinstance(form.instance, Campaign))

        form = CampaignForm(self.user, data={
            "name": "mylittle_campaign",
            "description": "xyz",
            "startingdate": "1301392136.0",
            "expirationdate": "1301332136.0",
            "frequency": "120",
            "callmaxduration": "50",
            "maxretry": "3",
            "intervalretry": "2000",
            "calltimeout": "60",
            "aleg_gateway": "1",
            "sms_gateway": "",
            "content_object": "type:32-id:1",
            "extra_data": "2000",
            "ds_user": self.user})
        self.assertEquals(form.is_valid(), False)

    def teardown(self):
        self.campaign.delete()
        self.subscriber.delete()
