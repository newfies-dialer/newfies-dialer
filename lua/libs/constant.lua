--
-- Newfies-Dialer License
-- http://www.newfies-dialer.org
--
-- This Source Code Form is subject to the terms of the Mozilla Public
-- License, v. 2.0. If a copy of the MPL was not distributed with this file,
-- You can obtain one at http://mozilla.org/MPL/2.0/.
--
-- Copyright (C) 2011-2013 Star2Billing S.L.
--
-- The Initial Developer of the Original Code is
-- Arezqui Belaid <info@star2billing.com>
--

-- Constant Value SECTION_TYPE
PLAY_MESSAGE = "1"
MULTI_CHOICE = "2"
RATING_SECTION = "3"
CAPTURE_DIGITS = "4"
RECORD_MSG = "5"
CALL_TRANSFER = "6"
HANGUP_SECTION = "7"
CONFERENCE = "8"
DNC = "9"

SECTION_TYPE = {}
SECTION_TYPE["1"] = "PLAY_MESSAGE"
SECTION_TYPE["2"] = "MULTI_CHOICE"
SECTION_TYPE["3"] = "RATING_SECTION"
SECTION_TYPE["4"] = "CAPTURE_DIGITS"
SECTION_TYPE["5"] = "RECORD_MSG"
SECTION_TYPE["6"] = "CALL_TRANSFER"
SECTION_TYPE["7"] = "HANGUP_SECTION"
SECTION_TYPE["8"] = "CONFERENCE"
SECTION_TYPE["9"] = "DNC"

-- Constant Value SUBSCRIBER_STATUS
SUBSCRIBER_PENDING = "1"
SUBSCRIBER_PAUSE = "2"
SUBSCRIBER_ABORT = "3"
SUBSCRIBER_FAIL = "4"
SUBSCRIBER_SENT = "5"
SUBSCRIBER_IN_PROCESS = "6"
SUBSCRIBER_NOT_AUTHORIZED = "7"
SUBSCRIBER_COMPLETED = "8"

ROOT_DIR = '/usr/share/newfies-lua/'
TTS_DIR = ROOT_DIR..'tts/'
UPLOAD_DIR = '/usr/share/newfies/usermedia/'
AUDIODIR = '/usr/share/newfies/usermedia/tts/'
AUDIO_WELCOME = AUDIODIR..'script_9805d01afeec350f36ff3fd908f0cbd5.wav'
AUDIO_ENTERAGE = AUDIODIR..'script_4ee73b76b5b4c5d596ed1cb3257861f0.wav'
AUDIO_PRESSDIGIT = AUDIODIR..'script_610e09c761c4b592aaa954259ce4ce1d.wav'
FS_RECORDING_PATH = '/usr/share/newfies/usermedia/recording/'

USE_CACHE = false
