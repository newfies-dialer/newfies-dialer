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

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from dnc.models import DNC, DNCContact
from dnc.views import dnc_add, dnc_change, dnc_list, dnc_del,\
    dnc_contact_list, dnc_contact_add, dnc_contact_change, \
    dnc_contact_del, get_dnc_contact_count, dnc_contact_import
from dnc.forms import DNCForm, DNCContactForm, DNCContactSearchForm,\
    DNCContact_fileImport
from common.utils import BaseAuthenticatedClient
#import os

#csv_file = open(
#    os.path.abspath('../../newfies-dialer/newfies/') + '/dnc/fixtures/import_dnc_contact_10.txt', 'r'
#)

csv_file = open(
    settings.APPLICATION_DIR + '/dnc/fixtures/import_dnc_contact_10.txt', 'r'
)
new_file = open(
    settings.APPLICATION_DIR + '/dialer_audio/fixtures/testcase_audio.mp3', 'r'
)


class DNCAdminView(BaseAuthenticatedClient):
    """
    Test cases for DNC list, DNC Contact Admin Interface.
    """

    def test_admin_dnc_view_list(self):
        """Test Function to check admin dnc list"""
        response = self.client.get("/admin/dnc/dnc/")
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_dnc_view_add(self):
        """Test Function to check admin dnc add"""
        response = self.client.get("/admin/dnc/dnc/add/")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/admin/dnc/dnc/add/',
            data={'name': 'test_dnc', 'user': '1'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_admin_dnc_contact_view_list(self):
        """Test Function to check admin dnc contact list"""
        response = self.client.get("/admin/dnc/dnccontact/")
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_dnc_contact_view_add(self):
        """Test Function to check admin dnc contact add"""
        response = self.client.get("/admin/dnc/dnccontact/add/")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/admin/dnc/dnccontact/add/',
            data={'dnc_id': '1', 'phone_number': '1234'})
        self.assertEqual(response.status_code, 200)


class DNCCustomerView(BaseAuthenticatedClient):
    """Test cases for DNC list & DNC contact
       Customer Interface.
    """

    fixtures = ['auth_user.json', 'dnc_list.json', 'dnc_contact.json']

    def test_dnc_view_list(self):
        """Test Function to check dnc list"""
        response = self.client.get('/module/dnc_list/')
        self.assertTemplateUsed(response, 'frontend/dnc_list/list.html')

        request = self.factory.get('/module/dnc_list/')
        request.user = self.user
        request.session = {}
        response = dnc_list(request)
        self.assertEqual(response.status_code, 200)

    def test_dnc_view_add(self):
        """Test Function to check add dnc"""
        request = self.factory.post('/module/dnc_list/add/', data={
            'name': 'My DNC'}, follow=True)
        request.user = self.user
        request.session = {}
        response = dnc_add(request)
        self.assertEqual(response.status_code, 302)

        resp = self.client.post('/module/dnc_list/add/', data={'name': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['form']['name'].errors,
                         [u'This field is required.'])

    def test_dnc_view_update(self):
        """Test Function to check update dnc"""
        response = self.client.get('/module/dnc_list/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/dnc_list/change.html')

        request = self.factory.post('/module/dnc_list/1/',
            data={'name': 'Default_DNC'}, follow=True)
        request.user = self.user
        request.session = {}
        response = dnc_change(request, 1)
        self.assertEqual(response.status_code, 302)

        # delete dnc through dnc_change
        request = self.factory.post('/module/dnc_list/1/',
                                    data={'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        response = dnc_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_dnc_view_delete(self):
        """Test Function to check delete dnc"""
        request = self.factory.post('/module/dnc_list/del/1/')
        request.user = self.user
        request.session = {}
        response = dnc_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/module/dnc_list/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = dnc_del(request, 0)
        self.assertEqual(response.status_code, 302)

    def test_dnc_contact_view_list(self):
        """Test Function to check DNC Contact list"""
        response = self.client.get('/module/dnc_contact/')
        self.assertTrue(response.context['form'], DNCContactSearchForm(self.user))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/dnc_contact/list.html')

        request = self.factory.post('/module/dnc_contact/',
                                    data={'phone_number': '123'})
        request.user = self.user
        request.session = {}
        response = dnc_contact_list(request)
        self.assertEqual(response.status_code, 200)

    def test_dnc_contact_view_add(self):
        """Test Function to check add DNC Contact"""
        response = self.client.get('/module/dnc_contact/add/')
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/module/dnc_contact/add/',
                                    data={'dnc_id': '1', 'phone_number': '1234'})
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/module/dnc_contact/add/')
        request.user = self.user
        request.session = {}
        response = dnc_contact_add(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/module/dnc_contact/add/',
                                    data={'phone_number': '1234'})
        self.assertEqual(response.status_code, 200)

    def test_dnc_contact_view_update(self):
        """Test Function to check update DNC Contact"""
        response = self.client.get('/module/dnc_contact/1/')
        self.assertTrue(response.context['form'], DNCContactForm(self.user))
        self.assertEqual(response.context['action'], 'update')
        self.assertTemplateUsed(response, 'frontend/dnc_contact/change.html')

        request = self.factory.post('/module/dnc_contact/1/',
            {'dnc': '1', 'phone_number': '154'})
        request.user = self.user
        request.session = {}
        response = dnc_contact_change(request, 1)
        self.assertEqual(response.status_code, 302)

        # delete contact through dnc_contact_change
        request = self.factory.post('/module/dnc_contact/1/',
                                    data={'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        response = dnc_contact_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_dnc_contact_view_delete(self):
        """Test Function to check delete dnc contact"""
        request = self.factory.get('/module/dnc_contact/del/1/')
        request.user = self.user
        request.session = {}
        response = dnc_contact_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/module/dnc_contact/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = dnc_contact_del(request, 0)
        self.assertEqual(response['Location'], '/module/dnc_contact/')
        self.assertEqual(response.status_code, 302)

    def test_dnc_contact_view_import(self):
        """Test Function to check import dnc Contact"""
        response = self.client.get('/module/dnc_contact_import/')
        self.assertTrue(response.context['form'],
                        DNCContact_fileImport(self.user))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'frontend/dnc_contact/import_dnc_contact.html')

        response = self.client.post('/module/dnc_contact_import/',
                                    data={'dnc_list': '1',
                                          'csv_file': csv_file})
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/module/dnc_contact_import/',
                                    data={'dnc_list': '1',
                                          'csv_file': new_file})
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/module/dnc_contact_import/')
        request.user = self.user
        request.session = {}
        response = dnc_contact_import(request)
        self.assertEqual(response.status_code, 200)

    def test_get_dnc_contact_count(self):
        request = self.factory.get('/module/dnc_contact/', {'ids': '1'})
        request.user = self.user
        request.session = {}
        response = get_dnc_contact_count(request)
        self.assertEqual(response.status_code, 200)


class DNCModel(TestCase):
    """
    Test DNC model
    """

    fixtures = ['auth_user.json']

    def setUp(self):
        self.user = User.objects.get(username='admin')
        self.dnc = DNC(
            name='test_dnc',
            user=self.user
        )
        self.dnc.save()

        self.assertTrue(self.dnc.__unicode__())
        self.dnc_contact = DNCContact(
            dnc=self.dnc,
            phone_number='123456'
        )
        self.dnc_contact.save()

        self.assertTrue(self.dnc_contact.__unicode__())

    def test_dnc_form(self):
        self.assertEqual(self.dnc.name, 'test_dnc')
        form = DNCForm({'name': 'sample_dnc'})
        obj = form.save(commit=False)
        obj.user = self.user
        obj.save()

        form = DNCForm(instance=self.dnc)
        self.assertTrue(isinstance(form.instance, DNC))

    def test_dnc_contact_form(self):
        self.assertEqual(self.dnc_contact.dnc, self.dnc)
        form = DNCContactForm(self.user)
        form.phone_number = '123456'
        obj = form.save(commit=False)
        obj.dnc = self.dnc
        obj.save()

        form = DNCContactForm(self.user, instance=self.dnc_contact)
        self.assertTrue(isinstance(form.instance, DNCContact))

    def test_name(self):
        self.assertEqual(self.dnc.name, "test_dnc")
        self.assertEqual(self.dnc_contact.phone_number, "123456")

    def teardown(self):
        self.dnc.delete()
        self.dnc_contact.delete()
