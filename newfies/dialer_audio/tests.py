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
import nose.tools as nt


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
        response = self.client.get('/audio/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['module'], 'audio_list')
        self.assertTemplateUsed(response, 'frontend/audio/audio_list.html')

    def test_audiofile_view_add(self):
        response = self.client.get('/audio/add/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['action'], 'add')
        self.assertTemplateUsed(response, 'frontend/audio/audio_change.html')

        response = self.client.post('/audio/add/', {'name': '', 'audio_file': 'xyz.ttf'},
                                    **self.extra)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['name'].errors,
                         [u'This field is required.'])
        self.assertEqual(response.context['form']['audio_file'].errors,
                         [u'This field is required.'])


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

    def test_init(self):
        form = DialerAudioFileForm(instance=self.audiofile)

        self.assertTrue(isinstance(form.instance, AudioFile))
        self.assertEqual(form.instance.pk, self.audiofile.pk)

    def teardown(self):
        self.audiofile.delete()

