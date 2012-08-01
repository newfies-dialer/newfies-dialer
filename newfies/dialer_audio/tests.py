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
        audio_list = AudioFile.objects.filter(user=self.user)
        self.assertEqual(response.context['module'], 'audio_list')

        self.assertTemplateUsed(response, 'frontend/audio/audio_list.html')

    def test_audiofile_view_add(self):
        response = self.client.get('/audio/add/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/audio/audio_change.html')


class AudioFileModel(object):
    """Test AudioFile model"""

    fixtures = ['auth_user.json']

    def setup(self):
        self.user = User.objects.get(username='admin')

        self.audiofile = AudioFile(
            name='MyAudio',
            user=self.user,
            )
        self.audiofile.save()
        super(DialerAudioFileForm, self).setUp()

    def test_name(self):
        nt.assert_equal(self.audiofile.name, "MyAudio")

    def test_init(self):
        form = DialerAudioFileForm(instance=self.audiofile)

        self.assertRaises(KeyError, DialerAudioFileForm)
        self.assertRaises(KeyError, DialerAudioFileForm, {})

        self.assertTrue(isinstance(form.instance, AudioFile))
        self.assertEqual(form.instance.pk, self.audiofile.pk)
        self.assertEqual(form.instance.name, "Sample Audio")
        form.save()

    def teardown(self):
        self.audiofile.delete()
