# -*- coding: utf-8 -*-
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
from rest_framework import serializers
from audiofield.models import AudioFile


class AudioFileSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/audio-files/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/audio-files/%audio-files-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/audio-files/1/",
                        "name": "Sample audio",
                        "audio_file": "upload/audiofiles/audio-file-SODXT-1669906647.wav",
                        "user": "http://127.0.0.1:8000/rest-api/users/1/",
                        "created_date": "2013-06-14T18:56:58.550",
                        "updated_date": "2013-06-14T18:56:58.969"
                    }
                ]
            }
    """
    audio_file = serializers.FileField(required=True)
    user = serializers.Field(source='user')

    class Meta:
        model = AudioFile
