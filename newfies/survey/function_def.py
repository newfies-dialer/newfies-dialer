#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#
from django.conf import settings


def getaudio_mstranslator(text, tts_language='en'):
    """
    Run Microsoft Speak Text2Speech and return audio url
    """
    import msspeak
    DIRECTORY = settings.MEDIA_ROOT + '/tts/'
    if not tts_language:
        tts_language = 'en'
    tts_msspeak = msspeak.MSSpeak(
        settings.CLIENT_ID,
        settings.CLIENT_SECRET,
        DIRECTORY)
    output_filename = tts_msspeak.speak(
        text, tts_language)
    audiofile = 'tts/' + output_filename
    return audiofile


def getaudio_acapela(text, tts_language='en'):
    """
    Run Acapela Text2Speech and return audio url
    """
    import acapela
    DIRECTORY = settings.MEDIA_ROOT + '/tts/'
    if not tts_language:
        tts_language = 'en'
    tts_acapela = acapela.Acapela(
        settings.ACCOUNT_LOGIN, settings.APPLICATION_LOGIN,
        settings.APPLICATION_PASSWORD, settings.SERVICE_URL,
        settings.QUALITY, DIRECTORY)
    tts_acapela.prepare(
        text, tts_language, settings.ACAPELA_GENDER,
        settings.ACAPELA_INTONATION)
    output_filename = tts_acapela.run()
    audiofile = 'tts/' + output_filename
    return audiofile
