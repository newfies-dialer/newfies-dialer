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
from django.core.management import call_command
from django.test import TestCase
from sms_module.models import SMSCampaign, SMSMessage, SMSCampaignSubscriber
from sms_module.views import sms_campaign_list, sms_campaign_add,\
    sms_campaign_change, sms_campaign_del, update_sms_campaign_status_admin,\
    update_sms_campaign_status_cust, sms_dashboard, sms_report, export_sms_report,\
    get_url_sms_campaign_status, common_sms_campaign_status
from sms_module.tasks import init_smsrequest, check_sms_campaign_pendingcall, spool_sms_nocampaign,\
    sms_campaign_running, SMSImportPhonebook, sms_campaign_spool_contact, sms_collect_subscriber,\
    sms_campaign_expire_check, resend_sms_update_smscampaignsubscriber
from sms_module.constants import SMS_CAMPAIGN_STATUS
from user_profile.models import UserProfile
from sms_module.forms import SMSDashboardForm
from frontend.constants import SEARCH_TYPE
from common.utils import BaseAuthenticatedClient
from datetime import datetime
from django.utils.timezone import utc
from uuid import uuid1


class SMSAdminView(BaseAuthenticatedClient):
    """Test cases for SMSCampaign, SMSSubscriber Admin Interface."""

    def test_admin_sms_campaign_view_list(self):
        """Test Function to check admin campaign list"""
        response = self.client.get('/admin/sms_module/smscampaign/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_sms_campaign_view_add(self):
        """Test Function to check admin campaign add"""
        response = self.client.get('/admin/sms_module/smscampaign/add/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_sms_subscriber_view_list(self):
        """Test Function to check admin subscriber list"""
        response = self.client.get('/admin/sms_module/smscampaignsubscriber/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_sms_subscriber_view_add(self):
        """Test Function to check admin subscriber add"""
        response = self.client.get('/admin/sms_module/smscampaignsubscriber/add/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_sms_template_view_list(self):
        """Test Function to check admin subscriber list"""
        response = self.client.get('/admin/sms_module/smstemplate/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_sms_template_view_add(self):
        """Test Function to check admin subscriber add"""
        response = self.client.get('/admin/sms_module/smstemplate/add/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_smsmessage_view_list(self):
        """Test Function to check admin subscriber list"""
        response = self.client.get('/admin/sms_module/smsmessage/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_smsmessage_report(self):
        """Test Function to check admin subscriber add"""
        response = self.client.get('/admin/sms_module/smsmessage/sms_daily_report/')
        self.failUnlessEqual(response.status_code, 200)


class SMSModuleCustomerView(BaseAuthenticatedClient):
    """Test cases for SMSCampaign Customer Interface."""

    fixtures = ['example_gateways.json', 'auth_user.json', 'gateway.json',
                'phonebook.json', 'contact.json', 'dialer_setting.json',
                'sms_campaign.json', 'user_profile.json', 'message.json',
                'sms_message.json']

    def test_sms_campaign_list(self):
        """Test Function to check sms campaign list"""
        response = self.client.get('/sms_campaign/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/sms_campaign/list.html')

        request = self.factory.get('/sms_campaign/')
        request.user = self.user
        request.session = {}
        response = sms_campaign_list(request)
        self.assertEqual(response.status_code, 200)

    def test_sms_campaign_view_add(self):
        """Test Function to check add campaign"""
        request = self.factory.get('/sms_campaign/add/')
        request.user = self.user
        request.session = {}
        response = sms_campaign_add(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/sms_campaign/add/', data={
            "name": "my sms campaign",
            "description": "xyz",
            "sms_gateway": "1",
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/sms_campaign/add/', {
            "name": "my sms campaign 2",
            "description": "xyz",
            "sms_gateway": "1",
        }, follow=True)
        request.user = self.user
        request.session = {}
        response = sms_campaign_add(request)
        self.assertEqual(response.status_code, 200)

    def test_sms_campaign_view_update(self):
        """Test Function to check update sms campaign"""
        request = self.factory.post('/sms_campaign/1/', {
            "name": "Sample sms campaign",
        }, follow=True)
        request.user = self.user
        request.session = {}
        response = sms_campaign_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/sms_campaign/1/',
            {'delete': 'true'}, follow=True)
        request.user = self.user
        request.session = {}
        response = sms_campaign_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_sms_campaign_view_delete(self):
        """Test Function to check delete sms campaign"""
        # delete campaign through campaign_change
        request = self.factory.post('/sms_campaign/del/1/', follow=True)
        request.user = self.user
        request.session = {}
        response = sms_campaign_del(request, 1)
        self.assertEqual(response['Location'], '/sms_campaign/')
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/sms_campaign/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = sms_campaign_del(request, 0)
        self.assertEqual(response['Location'], '/sms_campaign/')
        self.assertEqual(response.status_code, 302)

    def test_update_sms_campaign_status_admin(self):
        request = self.factory.post('update_sms_campaign_status_admin/1/1/',
            follow=True)
        request.user = self.user
        request.session = {}
        response = update_sms_campaign_status_admin(request, 1, 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],
            '/admin/sms_module/smscampaign/')

    def test_update_sms_campaign_status_cust(self):
        request = self.factory.post(
            'update_sms_campaign_status_cust/1/1/', follow=True)
        request.user = self.user
        request.session = {}
        response = update_sms_campaign_status_cust(request, 1, 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/sms_campaign/')

        request = self.factory.post(
            'update_sms_campaign_status_cust/1/2/', follow=True)
        request.user = self.user
        request.session = {}
        response = update_sms_campaign_status_cust(request, 1, 2)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post(
            'update_sms_campaign_status_cust/1/3/', follow=True)
        request.user = self.user
        request.session = {}
        response = update_sms_campaign_status_cust(request, 1, 3)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post(
            'update_sms_campaign_status_cust/1/4/', follow=True)
        request.user = self.user
        request.session = {}
        response = update_sms_campaign_status_cust(request, 1, 4)
        self.assertEqual(response.status_code, 302)

    def test_sms_dashboard(self):
        """Test Function to check customer sms_dashboard"""
        response = self.client.get('/sms_dashboard/')
        self.assertTrue(response.context['form'], SMSDashboardForm(self.user))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/sms_campaign/sms_dashboard.html')

        request = self.factory.post('/sms_dashboard/',
            {'smscampaign': '1',
             'search_type': SEARCH_TYPE.A_Last_30_days})

        request.user = self.user
        request.session = {}
        response = sms_dashboard(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/sms_dashboard/',
            {'smscampaign': '1',
             'search_type': SEARCH_TYPE.B_Last_7_days})

        request.user = self.user
        request.session = {}
        response = sms_dashboard(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/sms_dashboard/',
            {'smscampaign': '1',
             'search_type': SEARCH_TYPE.C_Yesterday})

        request.user = self.user
        request.session = {}
        response = sms_dashboard(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/sms_dashboard/',
            {'smscampaign': '1',
             'search_type': SEARCH_TYPE.D_Last_24_hours})

        request.user = self.user
        request.session = {}
        response = sms_dashboard(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/sms_dashboard/',
            {'smscampaign': '1',
             'search_type': SEARCH_TYPE.E_Last_12_hours})

        request.user = self.user
        request.session = {}
        response = sms_dashboard(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/sms_dashboard/',
            {'smscampaign': '1',
             'search_type': SEARCH_TYPE.F_Last_6_hours})

        request.user = self.user
        request.session = {}
        response = sms_dashboard(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/sms_dashboard/',
            {'smscampaign': '1',
             'search_type': SEARCH_TYPE.G_Last_hour})

        request.user = self.user
        request.session = {}
        response = sms_dashboard(request)
        self.assertEqual(response.status_code, 200)
        response = sms_dashboard(request, on_index='yes')

    def test_sms_report(self):
        """Test Function to check sms report"""
        response = self.client.get('/sms_report/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'frontend/sms_campaign/sms_report.html')

        response = self.client.post(
            '/sms_report/', data={'from_date': datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d"),
                                  'to_date': datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d")})
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/sms_report/')
        request.user = self.user
        request.session = {}
        response = sms_report(request)
        self.assertEqual(response.status_code, 200)

    def test_export_sms_report(self):
        """Test Function to check message export report"""
        request = self.factory.get('/export_sms_report/?format=csv')
        request.user = self.user
        request.session = {}
        request.session['sms_record_qs'] = {}
        response = export_sms_report(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/export_sms_report/?format=json')
        request.user = self.user
        request.session = {}
        request.session['sms_record_qs'] = {}
        response = export_sms_report(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/export_sms_report/?format=xls')
        request.user = self.user
        request.session = {}
        request.session['sms_record_qs'] = {}
        response = export_sms_report(request)
        self.assertEqual(response.status_code, 200)


class SMSCeleryTaskTestCase(TestCase):
    """Test cases for celery task"""

    fixtures = ['example_gateways.json', 'auth_user.json', 'gateway.json',
                'phonebook.json', 'contact.json', 'dialer_setting.json',
                'user_profile.json', 'sms_campaign.json', 'message.json',
                'sms_message.json', 'sms_campaign_subscriber.json']

    def test_init_smsrequest(self):
        """Test that the ``init_smsrequest``
        task runs with no errors, and returns the correct result."""
        sms_campaign_obj = SMSCampaign.objects.get(pk=1)
        sms_campaign_subscriber_obj = SMSCampaignSubscriber.objects.get(pk=1)
        result = init_smsrequest.delay(sms_campaign_subscriber_obj, sms_campaign_obj)
        self.assertEqual(result.successful(), True)

    def test_check_sms_campaign_pendingcall(self):
        """Test that the ``check_sms_campaign_pendingcall``
        periodic task runs with no errors, and returns the correct result."""
        result = check_sms_campaign_pendingcall.delay(1)
        self.assertEqual(result.successful(), True)

    def test_sms_campaign_running(self):
        """Test that the ``sms_campaign_running``
        task runs with no errors, and returns the correct result."""
        result = sms_campaign_running.delay()
        self.assertEqual(result.successful(), True)

    def test_sms_campaign_spool_contact(self):
        """Test that the ``sms_campaign_spool_contact``
        periodic task runs with no errors, and returns the correct result."""
        result = sms_campaign_spool_contact.delay()
        self.assertEqual(result.successful(), True)

    def test_import_phonebook(self):
        """Test that the ``import_phonebook``
        periodic task runs with no errors, and returns the correct result."""
        result = SMSImportPhonebook.delay(1, 1)
        self.assertEqual(result.successful(), True)

    def test_sms_campaign_expire_check(self):
        """Test that the ``sms_campaign_expire_check``
        task runs with no errors, and returns the correct result."""
        result = sms_campaign_expire_check.delay()
        self.assertEqual(result.successful(), True)

    def test_resend_sms_update_smscampaignsubscriber(self):
        """Test that the ``resend_sms_update_smscampaignsubscriber``
        periodic task runs with no errors, and returns the correct result."""
        result = resend_sms_update_smscampaignsubscriber.delay()
        self.assertEqual(result.successful(), True)


class SMSCampaignModel(TestCase):
    """Test SMSCampaign, SMSSubscriber models"""

    fixtures = ['example_gateways.json', 'auth_user.json', 'gateway.json',
                'phonebook.json', 'contact.json', 'dialer_setting.json',
                'sms_campaign.json', 'user_profile.json', 'message.json',
                'sms_message.json']

    def setUp(self):
        self.user = User.objects.get(username='admin')

        self.sms_dialer_setting = UserProfile.objects.get(user=self.user).dialersetting
        self.sms_dialer_setting.save()

        self.smscampaign = SMSCampaign(
            name="SMS Campaign",
            user=self.user,
            sms_gateway_id=1,
            status=2
        )
        self.smscampaign.save()
        self.assertEqual(self.smscampaign.__unicode__(), u'SMS Campaign')

        self.sms = SMSMessage(
            message_id=1,
            sms_campaign_id=1,
            sms_gateway_id=1,
            sender=self.user,
            content_type_id=1,
            object_id=1,
            uuid=str(uuid1()),
        )
        self.sms.save()

        # Subscriber model
        self.smssubscriber = SMSCampaignSubscriber(
            message_id=1,
            sms_campaign=self.smscampaign,
            contact_id=1,
            count_attempt=0,
            duplicate_contact=1,
            status=1
        )
        self.smssubscriber.save()
        self.assertTrue(self.smssubscriber.__unicode__())

        # Test mgt command
        call_command("create_sms", "1|10")

    def test_campaign_form(self):
        self.assertEqual(self.smscampaign.name, "SMS Campaign")
        SMSCampaign.objects.get_running_sms_campaign()
        SMSCampaign.objects.get_expired_sms_campaign()

        self.smscampaign.status = SMS_CAMPAIGN_STATUS.PAUSE
        self.smscampaign.save()
        self.smscampaign.update_sms_campaign_status()
        get_url_sms_campaign_status(self.smscampaign.pk, self.smscampaign.status)

        self.smscampaign.status = SMS_CAMPAIGN_STATUS.ABORT
        self.smscampaign.save()
        self.smscampaign.update_sms_campaign_status()
        get_url_sms_campaign_status(self.smscampaign.pk, self.smscampaign.status)

        self.smscampaign.status = SMS_CAMPAIGN_STATUS.END
        self.smscampaign.save()
        self.smscampaign.update_sms_campaign_status()
        get_url_sms_campaign_status(self.smscampaign.pk, self.smscampaign.status)

        self.smscampaign.is_authorized_contact('123456789')

        self.smscampaign.get_active_max_frequency()
        self.smscampaign.get_active_contact()
        self.smscampaign.progress_bar()
        self.smscampaign.sms_campaignsubscriber_detail()
        self.smscampaign.get_pending_subscriber()
        self.smscampaign.get_pending_subscriber_update()

        common_sms_campaign_status(self.smscampaign.id, SMS_CAMPAIGN_STATUS.START)
        common_sms_campaign_status(self.smscampaign.id, SMS_CAMPAIGN_STATUS.PAUSE)
        common_sms_campaign_status(self.smscampaign.id, SMS_CAMPAIGN_STATUS.ABORT)
        common_sms_campaign_status(self.smscampaign.id, SMS_CAMPAIGN_STATUS.END)

        self.assertEqual(self.smssubscriber.sms_campaign, self.smscampaign)

    def teardown(self):
        self.smscampaign.delete()
        self.smssubscriber.delete()
