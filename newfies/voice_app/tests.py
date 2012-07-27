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
from voice_app.models import VoiceApp
from common.test_utils import BaseAuthenticatedClient
import nose.tools as nt


class VoiceAppAdminView(BaseAuthenticatedClient):
    """Test Function to check Voice App Admin pages"""

    def test_voiceapp(self):
        response = self.client.get("/admin/voice_app/voiceapp/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/voice_app/voiceapp/add/")
        self.assertEqual(response.status_code, 200)


class VoiceAppCustomerView(BaseAuthenticatedClient):
    """Test Function to check Voice App Customer pages"""
    fixtures = ['voiceapp']

    def test_voiceapp_view_list(self):
        response = self.client.get('/voiceapp/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/voiceapp/list.html')

    def test_voiceapp_view_add(self):
        response = self.client.get('/voiceapp/add/')
        self.assertTemplateUsed(response, 'frontend/voiceapp/change.html')
        response = self.client.get('/voiceapp/1/')
        self.assertEqual(response.status_code, 200)


class VoiceAppModel(object):
    """Test Voice app Model"""
    def setup(self):
        self.user = User.objects.get(username='admin')
        self.voiceapp = VoiceApp(
            name='test voiceapp',
            type=1,
            gateway_id=1,
            user=self.user,
            )
        self.voiceapp.set_name("MyVoiceapp")
        self.voiceapp.save()

    def test_name(self):
        nt.assert_equal(self.voiceapp.name, "MyVoiceapp")

    def teardown(self):
        self.voiceapp.delete()
