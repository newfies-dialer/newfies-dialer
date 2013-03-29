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
from django.contrib.auth.forms import PasswordChangeForm
from agent.models import AgentProfile
from agent.forms import UserChangeDetailForm, \
    AgentChangeDetailExtendForm
from agent.views import agent_detail_change, agent_list, agent_add, agent_change, agent_del
from dialer_settings.models import DialerSetting
from common.utils import BaseAuthenticatedClient


class AgentProfileAdminView(BaseAuthenticatedClient):
    """Test Function to check UserProfile Admin pages"""

    def test_admin_agent_view_list(self):
        """Test Function to check admin customer list"""
        response = self.client.get("/admin/auth/agent/")
        self.assertEqual(response.status_code, 200)

    def test_admin_agent_view_add(self):
        """Test Function to check admin agent add"""
        response = self.client.get("/admin/auth/agent/add/")
        self.assertEqual(response.status_code, 200)


class AgentProfileCustomerView(BaseAuthenticatedClient):
    """Test Function to check UserProfile Customer pages"""

    fixtures = ['auth_user.json', 'notification.json']

    def test_agent_settings(self):
        """Test Function to check agent settings"""
        response = self.client.post('/agent_detail_change/?action=tabs-1',
                                    {'form-type': 'change-detail',
                                     'first_name': 'admin'})
        self.assertTrue(response.context['user_detail_form'],
                        UserChangeDetailForm(self.user))
        self.assertTrue(response.context['user_detail_extened_form'],
                        AgentChangeDetailExtendForm(self.user))

        response = self.client.post('/agent_detail_change/?action=tabs-2',
                                    {'form-type': ''})
        self.assertTrue(response.context['user_password_form'],
                        PasswordChangeForm(self.user))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
            'frontend/registration/user_detail_change.html')

        request = self.factory.get('/agent_detail_change/')
        request.user = self.user
        request.session = {}
        response = agent_detail_change(request)
        self.assertEqual(response.status_code, 200)

    def test_agent_view_list(self):
        """Test Function to check Agent list"""
        response = self.client.get('/agent/')
        self.assertEqual(response.context['module'], 'agent_list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/agent/list.html')

        request = self.factory.get('/agent/')
        request.user = self.user
        request.session = {}
        response = agent_list(request)
        self.assertEqual(response.status_code, 200)

    def test_agent_view_add(self):
        """Test Function to check add agent"""
        response = self.client.get('/agent/add/')
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/agent/add/',
                                    data={'username': 'xyz',
                                          'password1': '1234',
                                          'password2': '1234'})
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/agent/add/')
        request.user = self.user
        request.session = {}
        response = agent_add(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/agent/add/',
                                    data={'username': 'xyz'})
        self.assertEqual(response.status_code, 200)

    def test_agent_view_update(self):
        """Test Function to check update agent"""
        response = self.client.get('/agent/1/')
        self.assertEqual(response.context['action'], 'update')
        self.assertTemplateUsed(response, 'frontend/agent/change.html')

        request = self.factory.post('/contact/1/', {'contact': '1234'})
        request.user = self.user
        request.session = {}
        response = agent_change(request, 1)
        self.assertEqual(response.status_code, 200)

        # delete agent through agent_change
        request = self.factory.post('/agent/1/',
                                    data={'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        response = agent_change(request, 1)
        self.assertEqual(response['Location'], '/agent/')
        self.assertEqual(response.status_code, 302)

    def test_agent_view_delete(self):
        """Test Function to check delete contact"""
        request = self.factory.get('/agent/del/1/')
        request.user = self.user
        request.session = {}
        response = agent_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/agent/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = agent_del(request, 0)
        self.assertEqual(response['Location'], '/agent/')
        self.assertEqual(response.status_code, 302)
