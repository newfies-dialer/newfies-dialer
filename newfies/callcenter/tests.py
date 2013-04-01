#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
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


class ACallcenterCustomerView(BaseAuthenticatedClient):
    """Test Function to check UserProfile Customer pages"""

    fixtures = ['auth_user.json', 'notification.json']

    def test_queue_view_list(self):
        """Test Function to check queue list"""
        response = self.client.get('/queue/')
        self.assertEqual(response.context['module'], 'queue_list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/queues/list.html')

        request = self.factory.get('/queue/')
        request.user = self.user
        request.session = {}
        response = queue_list(request)
        self.assertEqual(response.status_code, 200)

    def test_queue_view_add(self):
        """Test Function to check add queue"""
        response = self.client.get('/queue/add/')
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/queue/add/', data={})
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/queue/add/')
        request.user = self.user
        request.session = {}
        response = queue_add(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/queue/add/', data={})
        self.assertEqual(response.status_code, 200)

    def test_queue_view_update(self):
        """Test Function to check update queue"""
        response = self.client.get('/queue/1/')
        self.assertEqual(response.context['action'], 'update')
        self.assertTemplateUsed(response, 'frontend/queue/change.html')

        request = self.factory.post('/queue/1/', {'contact': '1234'})
        request.user = self.user
        request.session = {}
        response = queue_change(request, 1)
        self.assertEqual(response.status_code, 200)

        # delete agent through queue_change
        request = self.factory.post('/queue/1/',
                                    data={'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        response = queue_change(request, 1)
        self.assertEqual(response['Location'], '/queue/')
        self.assertEqual(response.status_code, 302)

    def test_queue_view_delete(self):
        """Test Function to check delete queue"""
        request = self.factory.get('/queue/del/1/')
        request.user = self.user
        request.session = {}
        response = queue_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/queue/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = queue_del(request, 0)
        self.assertEqual(response['Location'], '/queue/')
        self.assertEqual(response.status_code, 302)

    def test_tier_view_list(self):
        """Test Function to check tier list"""
        response = self.client.get('/tier/')
        self.assertEqual(response.context['module'], 'tier_list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/tier/list.html')

        request = self.factory.get('/tier/')
        request.user = self.user
        request.session = {}
        response = tier_list(request)
        self.assertEqual(response.status_code, 200)

    def test_tier_view_add(self):
        """Test Function to check add tier"""
        response = self.client.get('/tier/add/')
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/tier/add/', data={})
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/tier/add/')
        request.user = self.user
        request.session = {}
        response = tier_add(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/tier/add/', data={})
        self.assertEqual(response.status_code, 200)

    def test_tier_view_update(self):
        """Test Function to check update tier"""
        response = self.client.get('/tier/1/')
        self.assertEqual(response.context['action'], 'update')
        self.assertTemplateUsed(response, 'frontend/tier/change.html')

        request = self.factory.post('/tier/1/', {'manager': '1'})
        request.user = self.user
        request.session = {}
        response = tier_change(request, 1)
        self.assertEqual(response.status_code, 200)

        # delete agent through tier_change
        request = self.factory.post('/tier/1/',
                                    data={'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        response = tier_change(request, 1)
        self.assertEqual(response['Location'], '/tier/')
        self.assertEqual(response.status_code, 302)

    def test_tier_view_delete(self):
        """Test Function to check delete tier"""
        request = self.factory.get('/tier/del/1/')
        request.user = self.user
        request.session = {}
        response = tier_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/tier/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = tier_del(request, 0)
        self.assertEqual(response['Location'], '/tier/')
        self.assertEqual(response.status_code, 302)