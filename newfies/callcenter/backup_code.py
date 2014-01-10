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
from django.test import TestCase
from callcenter.models import Queue, Tier
from callcenter.forms import QueueForm, QueueFrontEndForm,\
    TierForm, TierFrontEndForm
from callcenter.views import queue_list, queue_add, queue_change, queue_del,\
    tier_list, tier_add, tier_change, tier_del
from common.utils import BaseAuthenticatedClient


class CallcenterAdminView(BaseAuthenticatedClient):
    """Test Function to check UserProfile Admin pages"""

    def test_admin_queue_view_list(self):
        """Test Function to check admin queue list"""
        response = self.client.get("/admin/callcenter/queue/")
        self.assertEqual(response.status_code, 200)

    def test_admin_queue_view_add(self):
        """Test Function to check admin queue add"""
        response = self.client.get("/admin/callcenter/queue/add/")
        self.assertEqual(response.status_code, 200)

    def test_admin_tier_view_list(self):
        """Test Function to check admin tier list"""
        response = self.client.get("/admin/callcenter/tier/")
        self.assertEqual(response.status_code, 200)

    def test_admin_tier_view_add(self):
        """Test Function to check admin tier add"""
        response = self.client.get("/admin/callcenter/tier/add/")
        self.assertEqual(response.status_code, 200)


class CallcenterCustomerView(BaseAuthenticatedClient):
    """Test Function to check UserProfile Customer pages"""

    fixtures = ['dialer_setting.json', 'gateway.json',
                'auth_user.json', 'user_profile.json', 'notification.json',
                'agent.json', 'agent_profile.json',
                'queue.json', 'tier.json']

    def test_queue_view_list(self):
        """Test Function to check queue list"""
        manager = User.objects.get(pk=2)
        response = self.client.get('/module/queue/')
        self.assertEqual(response.context['module'], 'queue_list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/queue/list.html')

        request = self.factory.get('/module/queue/')
        request.user = manager
        request.session = {}
        response = queue_list(request)
        self.assertEqual(response.status_code, 302)

    def test_queue_view_add(self):
        """Test Function to check add queue"""
        manager = User.objects.get(pk=2)
        response = self.client.get('/module/queue/add/')
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)
        #response = self.client.post('/queue/add/', data={})
        #self.assertEqual(response.context['action'], 'add')
        #self.assertEqual(response.status_code, 200)

        request = self.factory.get('/module/queue/add/')
        request.user = manager
        request.session = {}
        response = queue_add(request)
        self.assertEqual(response.status_code, 302)

        response = self.client.post('/module/queue/add/',
            data={'manager': '1', 'strategy': 'xyz'})
        self.assertEqual(response.status_code, 302)

    def test_queue_view_update(self):
        """Test Function to check update queue"""
        manager = User.objects.get(pk=2)
        request = self.factory.post('/module/queue/1/', {'contact': '1234'})
        request.user = manager
        request.session = {}
        response = queue_change(request, 1)
        self.assertEqual(response.status_code, 302)

        # delete agent through queue_change
        request = self.factory.post('/module/queue/1/',
                                    data={'delete': True}, follow=True)
        request.user = manager
        request.session = {}
        response = queue_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_queue_view_delete(self):
        """Test Function to check delete queue"""
        manager = User.objects.get(pk=2)
        request = self.factory.get('/module/queue/del/1/')
        request.user = manager
        request.session = {}
        response = queue_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/module/queue/del/', {'select': '1'})
        request.user = manager
        request.session = {}
        response = queue_del(request, 0)
        self.assertEqual(response.status_code, 302)

    def test_tier_view_list(self):
        """Test Function to check tier list"""
        manager = User.objects.get(pk=2)
        response = self.client.get('/module/tier/')
        self.assertEqual(response.context['module'], 'tier_list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/tier/list.html')

        request = self.factory.get('/module/tier/')
        request.user = manager
        request.session = {}
        response = tier_list(request)
        self.assertEqual(response.status_code, 302)

    def test_tier_view_add(self):
        """Test Function to check add tier"""
        manager = User.objects.get(pk=2)
        response = self.client.get('/module/tier/add/')
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/module/tier/add/', data={})
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/module/tier/add/')
        request.user = manager
        request.session = {}
        response = tier_add(request)
        self.assertEqual(response.status_code, 302)

        response = self.client.post('/module/tier/add/', data={})
        self.assertEqual(response.status_code, 200)

    def test_tier_view_update(self):
        """Test Function to check update tier"""
        manager = User.objects.get(pk=2)

        request = self.factory.post('/module/tier/1/', {'manager': '1'})
        request.user = manager
        request.session = {}
        response = tier_change(request, 1)
        self.assertEqual(response.status_code, 302)

        # delete agent through tier_change
        request = self.factory.post('/module/tier/1/',
                                    data={'delete': True}, follow=True)
        request.user = manager
        request.session = {}
        response = tier_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_tier_view_delete(self):
        """Test Function to check delete tier"""
        manager = User.objects.get(pk=2)
        request = self.factory.get('/module/tier/del/1/')
        request.user = manager
        request.session = {}
        response = tier_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/module/tier/del/', {'select': '1'})
        request.user = manager
        request.session = {}
        response = tier_del(request, 0)
        self.assertEqual(response.status_code, 302)
