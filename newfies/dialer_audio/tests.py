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

#from django.contrib.auth.models import User
from django.conf import settings
from common.utils import BaseAuthenticatedClient
#from audiofield.models import AudioFile
from dialer_audio.views import audio_list  # audio_add, audio_change, audio_del
#import os

#audio_file = open(
#    os.path.abspath('../../newfies-dialer/newfies/') + '/dialer_audio/fixtures/testcase_audio.mp3', 'r'
#)

audio_file = open(
    settings.APPLICATION_DIR + '/dialer_audio/fixtures/testcase_audio.mp3', 'r'
)


class AudioFileAdminView(BaseAuthenticatedClient):
    """Test cases for AudioFile Admin Interface."""

    def test_admin_audiofile_view_list(self):
        """Test Function to check admin audiofile list"""
        response = self.client.get("/admin/audiofield/audiofile/")
        self.assertEqual(response.status_code, 200)

    def test_admin_audiofile_view_add(self):
        """Test Function to check admin audiofile add"""
        response = self.client.get("/admin/audiofield/audiofile/add/")
        self.assertEqual(response.status_code, 200)


class AudioFileCustomerView(BaseAuthenticatedClient):
    """Test cases for AudioFile Customer Interface."""

    fixtures = ['auth_user.json']

    def test_audiofile_view_list(self):
        """Test Function to check audio list"""
        response = self.client.get('/module/audio/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/audio/audio_list.html')

        request = self.factory.get('/module/audio/')
        request.user = self.user
        request.session = {}
        response = audio_list(request)
        self.assertEqual(response.status_code, 200)
    """
    def test_audiofile_view_add(self):
        request = self.factory.post('/module/audio/add/',
            {"name": "sample_audio_file",
             "audio_file": audio_file,
             "convert_type": 2,
             "channel_type": 1,
             "freq_type": 8000,
            }, follow=True)
        request.user = self.user
        request.session = {}
        response = audio_add(request)
        self.assertEqual(response.status_code, 200)
        def test_audiofile_view_change(self):
        request = self.factory.post('/module/audio/1/',
            {'name': 'sample_audio'},
            follow=True)
        request.user = self.user
        request.session = {}
        response = audio_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/module/audio/1/',
            {'delete': 'true'}, follow=True)
        request.user = self.user
        request.session = {}
        response = audio_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_audiofile_view_del(self):
        request = self.factory.post('/module/audio/del/1/', {},
            follow=True)
        request.user = self.user
        request.session = {}
        response = audio_del(request, 1)
        self.assertEqual(response.status_code, 302)
    """
