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

#from django.test import TestCase
#from django.contrib.auth.models import User
#from django.conf import settings
from common.utils import BaseAuthenticatedClient


class ModMailerAdminView(BaseAuthenticatedClient):
    """
    Test cases for mail MailTemplate list Admin Interface.
    """

    def test_admin_mail_template_view_list(self):
        """Test Function to check admin MailTemplate list"""
        response = self.client.get("/admin/mod_mailer/mailtemplate/")
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_mail_template_view_add(self):
        """Test Function to check admin MailTemplate add"""
        response = self.client.get("/admin/mod_mailer/mailtemplate/add/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/admin/mod_mailer/mailtemplate/add/',
            data={'label': 'test', 'template_key': 'template_key_xyz',
                  'from_email': 'xyz@gmail.com', 'from_name': 'xyz',
                  'subject': 'sample_template', 'message_plaintext': 'test msg',
                  'message_html': '<b>test msg</b>'}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_admin_mailspooler_view_list(self):
        """Test Function to check admin mailspooler list"""
        response = self.client.get("/admin/mod_mailer/mailspooler/")
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_mailspooler_view_add(self):
        """Test Function to check admin mailspooler add"""
        response = self.client.get("/admin/mod_mailer/mailspooler/add/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/admin/mod_mailer/mailspooler/add/',
            data={'mailtemplate': '1', 'contact_email': 'areski@gmail.com',
                  'parameter': '', 'mailspooler_type': '1'},
            follow=True)
        self.assertEqual(response.status_code, 200)
