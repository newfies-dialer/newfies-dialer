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
from django.test import TestCase
from dialer_contact.models import Phonebook, Contact
from dialer_contact.forms import Contact_fileImport, \
                                 PhonebookForm, \
                                 ContactForm, \
                                 ContactSearchForm
from common.utils import BaseAuthenticatedClient
import nose.tools as nt


class DialerContactView(BaseAuthenticatedClient):
    """Test cases for Phonebook, Contact, Campaign, CampaignSubscriber
       Admin Interface.
    """

    def test_admin_phonebook_view_list(self):
        """Test Function to check admin phonebook list"""
        response = self.client.get("/admin/dialer_contact/phonebook/")
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_phonebook_view_add(self):
        """Test Function to check admin phonebook add"""
        response = self.client.get("/admin/dialer_contact/phonebook/add/")
        self.assertEqual(response.status_code, 200)

    def test_admin_contact_view_list(self):
        """Test Function to check admin contact list"""
        response = self.client.get("/admin/dialer_contact/contact/")
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_contact_view_add(self):
        """Test Function to check admin contact add"""
        response = self.client.get("/admin/dialer_contact/contact/add/")
        self.assertEqual(response.status_code, 200)

    def test_admin_contact_view_import(self):
        """Test Function to check admin import contact"""
        response =\
            self.client.get('/admin/dialer_contact/contact/import_contact/')
        self.failUnlessEqual(response.status_code, 200)


class DialerContactCustomerView(BaseAuthenticatedClient):
    """Test cases for Phonebook, Contact, Campaign, CampaignSubscriber
       Customer Interface.
    """

    fixtures = ['auth_user.json', 'phonebook.json', 'contact.json']

    def test_phonebook_view_list(self):
        """Test Function to check phonebook list"""
        response = self.client.get('/phonebook/')
        self.assertEqual(response.context['module'], 'phonebook_list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/phonebook/list.html')

    def test_phonebook_view_add(self):
        """Test Function to check add phonebook"""
        response = self.client.get('/phonebook/add/')
        self.assertEqual(response.context['action'], 'add')
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
        self.assertEqual(response.context['action'], 'update')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/phonebook/change.html')

    def test_contact_view_list(self):
        """Test Function to check Contact list"""
        response = self.client.get('/contact/')
        self.assertEqual(response.context['module'], 'contact_list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/contact/list.html')

    def test_contact_view_add(self):
        """Test Function to check add Contact"""
        response = self.client.get('/contact/add/')
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/contact/add/',
            data={'phonebook_id': '1', 'contact': '1234',
                  'last_name': 'xyz', 'first_name': 'abc',
                  'status': '1'})
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)

    def test_contact_view_update(self):
        """Test Function to check update Contact"""
        response = self.client.get('/contact/1/')
        self.assertEqual(response.context['action'], 'update')
        self.assertTemplateUsed(response, 'frontend/contact/change.html')

    def test_contact_view_import(self):
        """Test Function to check import Contact"""
        response = self.client.get('/contact/import/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                'frontend/contact/import_contact.html')


class DialerContactModel(TestCase):
    """Test Phonebook, Contact models"""

    fixtures = ['auth_user.json', 'phonebook.json', 'contact.json']

    def setUp(self):
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

    def test_phonebook_form(self):
        nt.assert_equal(self.phonebook.name, 'test_phonebook')
        nt.assert_equal(self.contact.phonebook, self.phonebook)

        form = PhonebookForm({'name': 'sample_phonebook'})
        obj = form.save(commit=False)
        obj.user = self.user
        obj.save()

        form = PhonebookForm(instance=self.phonebook)
        self.assertTrue(isinstance(form.instance, Phonebook))

    def test_contact_form(self):
        form = ContactForm(self.user)
        form.contact = '123456'
        obj = form.save(commit=False)
        obj.phonebook = self.phonebook
        obj.save()

        form = ContactForm(self.user, instance=self.contact)
        self.assertTrue(isinstance(form.instance, Contact))


    def teardown(self):
        self.phonebook.delete()
        self.contact.delete()
