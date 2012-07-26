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
from django.test import TestCase, Client
from user_profile.models import Staff, Customer
import nose.tools as nt
import base64

from django.contrib import admin
admin.site.register(User)

class BaseAuthenticatedClient(TestCase):
    """Common Authentication to setup test"""

    def setUp(self):
        """To create admin user"""
        self.client = Client()
        self.user = \
            User.objects.create_user('admin', 'admin@world.com', 'admin')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.is_active = True
        self.user.save()
        auth = '%s:%s' % ('admin', 'admin')
        auth = 'Basic %s' % base64.encodestring(auth)
        auth = auth.strip()
        self.extra = {
            'HTTP_AUTHORIZATION': auth,
        }
        login = self.client.login(username='admin', password='admin')
        self.assertTrue(login)


class UserProfileAdminView(BaseAuthenticatedClient):
    """
    TODO: Add documentation
    """
    def test_user_profile(self):
        response = self.client.get("/admin/auth/staff/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/auth/staff/add/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/auth/customer/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/auth/customer/add/")
        self.assertEqual(response.status_code, 200)


class UserProfileCustomerView(BaseAuthenticatedClient):

    def test_user_settings(self):
        """Test Function to check User settings"""
        response = self.client.get('/user_detail_change/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
            'frontend/registration/user_detail_change.html')


class UserProfileModel(object):
    """
    TODO: Add documentation
    """
    def setup(self):
        self.user =\
            User.objects.get(username='admin')
        self.user_profile = Staff(
            user=self.user,
            userprofile_gateway_id=1,
            dialersetting_id=1,
            phone_no='123456',
            )
        self.user_profile.save()

    def test_name(self):
        nt.assert_equal(self.user_profile.user, self.user)

    def teardown(self):
        self.user_profile.delete()
