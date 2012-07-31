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


class DialerContactView(BaseAuthenticatedClient):
    """Test cases for Phonebook, Contact, Campaign, CampaignSubscriber
       Admin Interface.
    """

    def test_admin_phonebook_view_list(self):
        """Test Function to check admin phonebook list"""
        response = self.client.get("/admin/dialer_campaign/phonebook/")
        self.failUnlessEqual(response.status_code, 200)
    def test_admin_phonebook_view_list(self):
        """Test Function to check admin phonebook add"""
        response = self.client.get("/admin/dialer_campaign/phonebook/add/")
        self.assertEqual(response.status_code, 200)

    def test_admin_contact_view_list(self):
        """Test Function to check admin contact list"""
        response = self.client.get("/admin/dialer_campaign/contact/")
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_contact_view_add(self):
        """Test Function to check admin contact add"""
        response = self.client.get("/admin/dialer_campaign/contact/add/")
        self.assertEqual(response.status_code, 200)

    def test_admin_contact_view_import(self):
        """Test Function to check admin import contact"""
        response =\
            self.client.get('/admin/dialer_campaign/contact/import_contact/')
        self.failUnlessEqual(response.status_code, 200)


class DialerContactCustomerView(BaseAuthenticatedClient):
    """Test cases for Phonebook, Contact, Campaign, CampaignSubscriber
       Customer Interface.
    """

    fixtures = ['auth_user.json', 'phonebook.json', 'contact.json']

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


