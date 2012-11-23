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
from common.utils import BaseAuthenticatedClient
from common_notification.views import user_notification,\
    notification_del_read,\
    update_notification


class NotificationCustomerView(BaseAuthenticatedClient):
    """Test Function to check Notification pages"""

    fixtures = ['auth_user.json', 'notification.json']

    def test_user_settings(self):
        """Test Function to check User settings"""
        response = self.client.get(
            '/user_notification/?notification=mark_read_all', {})
        self.assertEqual(response.status_code, 200)

    def test_notification_del_read(self):
        """Test Function to check delete notification"""
        request = self.factory.post('/user_notification/del/1/',
            {'mark_read': 'false'})
        request.user = self.user
        request.session = {}
        response = notification_del_read(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/user_notification/del/2/',
            {'select': '1'})
        request.user = self.user
        request.session = {}
        response = notification_del_read(request, 2)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/user_notification/del/',
            {'select': '1',
             'mark_read': 'true'})
        request.user = self.user
        request.session = {}
        response = notification_del_read(request, 0)
        self.assertEqual(response.status_code, 302)

    def test_update_notice_status_cust(self):
        """Test Function to check update notice status"""
        request = self.factory.post('/user_notification/1/',
            {'select': '1'})
        request.user = self.user
        request.session = {}
        response = update_notification(request, 1)
        self.assertEqual(response.status_code, 302)

