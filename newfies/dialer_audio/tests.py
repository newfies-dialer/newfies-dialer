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
from common.test_utils import BaseAuthenticatedClient
from audiofield.models import AudioFile
import nose.tools as nt


class AudioFileAdminView(BaseAuthenticatedClient):
    """Test cases for AudioFile Admin Interface."""

    def test_audiofile_admin(self):
        response = self.client.get("/admin/audiofield/audiofile/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/audiofield/audiofile/add/")
        self.assertEqual(response.status_code, 200)


class AudioFileCustomerView(BaseAuthenticatedClient):
    """Test cases for AudioFile Customer Interface."""

    def test_audiofile_customer(self):
        response = self.client.get('/audio/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/audio/audio_list.html')
        response = self.client.get('/audio/add/')
        self.assertEqual(response.status_code, 200)


class TestAudioFileModel(object):
    """Test AudioFile model"""

    def setup(self):
        self.user = User.objects.get(username='admin')

        self.audiofile = AudioFile(
            name='MyAudio',
            user=self.user,
            )
        self.audiofile.save()

    def test_name(self):
        nt.assert_equal(self.audiofile.name, "MyAudio")

    def teardown(self):
        self.audiofile.delete()
