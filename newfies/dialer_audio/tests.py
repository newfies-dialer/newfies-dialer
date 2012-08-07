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
from audiofield.models import AudioFile
from dialer_audio.forms import DialerAudioFileForm
from dialer_audio.views import audio_list, audio_add


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

    def test_audiofile_view_list(self):
        """Test Function to check aidio list"""
        response = self.client.get('/audio/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['module'], 'audio_list')
        self.assertTemplateUsed(response, 'frontend/audio/audio_list.html')

        request = self.factory.get('/audio/')
        request.user = self.user
        request.session = {}
        response = audio_list(request)
        self.assertEqual(response.status_code, 200)

    def test_audiofile_view_add(self):
        """Test Function to check view to add audio"""
        response = self.client.get('/audio/add/')
        self.assertTrue(response.context['form'], DialerAudioFileForm())
        self.assertEqual(response.context['action'], 'add')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'frontend/audio/audio_change.html')

        response = self.client.post('/audio/add/', {'name': '',
                                                    'audio_file': ''},
                                    **self.extra)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['name'].errors,
                         [u'This field is required.'])
        self.assertEqual(response.context['form']['audio_file'].errors,
                         [u'This field is required.'])

        request = self.factory.post('/audio/add/', {'name': '',
                                                    'audio_file': ''})
        request.user = self.user
        request.session = {}
        response = audio_add(request)
        self.assertEqual(response.status_code, 200)


class AudioFileModel(TestCase):
    """Test AudioFile model"""

    fixtures = ['auth_user.json']

    def setUp(self):
        self.user = User.objects.get(username='admin')
        self.audiofile = AudioFile(
            name='MyAudio',
            user=self.user,
        )
        self.audiofile.save()

    def test_name(self):
        self.assertEqual(self.audiofile.name, "MyAudio")

    def test_audio_form(self):
        form = DialerAudioFileForm(instance=self.audiofile)

        self.assertTrue(isinstance(form.instance, AudioFile))
        self.assertEqual(form.instance.pk, self.audiofile.pk)

    def teardown(self):
        self.audiofile.delete()

