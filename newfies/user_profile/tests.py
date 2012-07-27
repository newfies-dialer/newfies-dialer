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
from user_profile.models import Staff, Customer
from common.utils import BaseAuthenticatedClient
import nose.tools as nt

from django.contrib import admin
admin.site.register(User)


class UserProfileAdminView(BaseAuthenticatedClient):
    """Test Function to check UserProfile Admin pages"""

    def test_admin_staff_view_list(self):
        """Test Function to check admin staff list"""
        response = self.client.get("/admin/auth/staff/")
        self.assertEqual(response.status_code, 200)

    def test_admin_staff_view_add(self):
        """Test Function to check admin staff add"""
        response = self.client.get("/admin/auth/staff/add/")
        self.assertEqual(response.status_code, 200)

    def test_admin_customer_view_list(self):
        """Test Function to check admin customer list"""
        response = self.client.get("/admin/auth/customer/")
        self.assertEqual(response.status_code, 200)

    def test_admin_customer_view_add(self):
        """Test Function to check admin customer add"""
        response = self.client.get("/admin/auth/customer/add/")
        self.assertEqual(response.status_code, 200)


class UserProfileCustomerView(BaseAuthenticatedClient):
    """Test Function to check UserProfile Customer pages"""

    def test_user_settings(self):
        """Test Function to check User settings"""
        response = self.client.get('/user_detail_change/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
            'frontend/registration/user_detail_change.html')


class UserProfileModel(object):
    """Test UserProfile Model"""

    fixtures = ['auth_user.json', 'gateway.json', 'dialer_setting']

    def setup(self):
        self.user = User.objects.get(username='admin')
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
