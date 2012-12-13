--
-- Newfies-Dialer License
-- http://www.newfies-dialer.org
--
-- This Source Code Form is subject to the terms of the Mozilla Public
-- License, v. 2.0. If a copy of the MPL was not distributed with this file,
-- You can obtain one at http://mozilla.org/MPL/2.0/.
--
-- Copyright (C) 2011-2012 Star2Billing S.L.
--
-- The Initial Developer of the Original Code is
-- Arezqui Belaid <info@star2billing.com>
--


package.path = package.path .. ";/home/areski/public_html/django/MyProjects/newfies-dialer/lua/?.lua";
package.path = package.path .. ";/home/areski/public_html/django/MyProjects/newfies-dialer/lua/libs/?.lua";

local oo = require "loop.simple"
local inspect = require 'inspect'
local database = require "database"


-- Constant Value
local PLAY_MESSAGE = 1
local MULTI_CHOICE = 2
local RATING_SECTION = 3
local CAPTURE_DIGITS = 4
local RECORD_MSG = 5
local CALL_TRANSFER = 6
local HANGUP_SECTION = 7

local AUDIODIR = '/home/areski/public_html/django/MyProjects/newfies-dialer/newfies/usermedia/tts/'
local AUDIO_WELCOME = AUDIODIR..'script_9805d01afeec350f36ff3fd908f0cbd5.wav'
local AUDIO_ENTERAGE = AUDIODIR..'script_4ee73b76b5b4c5d596ed1cb3257861f0.wav'
local AUDIO_PRESSDIGIT = AUDIODIR..'script_610e09c761c4b592aaa954259ce4ce1d.wav'


FSMCall = oo.class{
    -- default field values
    extension_list = nil,
    caller_id_name = nil,
    caller_id_number = nil,
    destination_number = nil,
    uuid = nil,
    survey_id = nil,
    call_duration = 0,
    debugger = nil,
    hangup_trigger = false,
    current_node_id = false,
    db = nil,
}

function FSMCall:__init(session, debug_mode, debugger)
    -- self is the class
    return oo.rawnew(self, {
        session = session,
        debug_mode = debug_mode,
        debugger = debugger,
        db = Database(debug_mode),
    })
end


function FSMCall:init()
    self.debugger:msg("INFO", "FSMCall:init")
    self.extension_list = self.session:getVariable("extension_list")
    self.caller_id_name = self.session:getVariable("caller_id_name")
    self.caller_id_number = self.session:getVariable("caller_id_number")
    self.destination_number = self.session:getVariable("destination_number")
    self.uuid = self.session:getVariable("uuid")
    self.campaign_id = self.session:getVariable("campaign_id")
    self.campaign_id = 23

    self.db:connect()
    if not self.db:load_all(self.campaign_id) then
        self.debugger:msg("ERROR", "Error loading data")
        self:hangupcall()
        return false
    end
    self.db:check_data()
    self.db:disconnect()

    self.debugger:msg("INFO", "start_node--->"..self.db.start_node)
    self.current_node_id = self.db.start_node
    --print(inspect(self.db.list_section[tonumber(self.db.start_node)]))
    if not self.db.valid_data then
        self.debugger:msg("ERROR", "Error invalid data")
        self:hangupcall()
        return false
    end
    --print(inspect(self.db.list_audio))
end

function FSMCall:end_call()
    self.debugger:msg("ERROR", "FSMCall:end_call")
    -- NOTE: Don't use this call time for Billing
    -- Use FS CDRs
    self.call_duration = os.time() - self.call_start
    self.debugger:msg("DEBUG", "Estimated Call Duration : "..self.call_duration)
    self:hangupcall()
end

function FSMCall:hangupcall()
    -- This will interrupt lua script
    self.debugger:msg("ERROR", "FSMCall:hangupcall")
    self.hangup_trigger = true
    self.session:hangup()
end

function FSMCall:start_call()
    self.debugger:msg("ERROR", "FSMCall:start_call...")
    self.call_start = os.time()
    self:next_node()
end


function FSMCall:next_node()
    self.debugger:msg("INFO", "FSMCall:next_node (current_node="..tonumber(self.current_node_id)..")")
    current_node = self.db.list_section[tonumber(self.current_node_id)]
    if not self.current_node then
        return false
    end

    print(inspect(current_node))
    -- Get the node type and start playing it
    timeout = current_node.timeout
    if timeout <= 0 then
        timeout = 1 -- GetDigits 'timeout' must be a positive integer
    end
    -- Get number of retries
    retries = current_node.retries
    if not retries then
        retries = 1
    end

    --Invalid Audio URL
    invalid_input = ''
    -- {PYTHON CODE}
    -- if (list_section[current_state].invalid_audiofile
    --    and list_section[current_state].invalid_audiofile.audio_file.url):
    --     #Audio file
    --     invalid_audiourl = url_basename + list_section[current_state].invalid_audiofile.audio_file.url
    --     invalid_input = ' invalidDigitsSound="%s"' % invalid_audiourl
    -- else:
    --     invalid_input = ''

    --Check if it's a completed section
    -- {PYTHON CODE}
    -- if (list_section[current_state].completed and (not current_completion or current_completion == 0)):
    --     #Flag subscriber
    --     subscriber = Subscriber.objects.get(pk=obj_callrequest.subscriber.id)
    --     subscriber.status = SUBSCRIBER_STATUS.COMPLETED
    --     subscriber.save()
    --     #Flag Callrequest
    --     obj_callrequest.completed = True
    --     obj_callrequest.save()
    --     #Increment Campaign completed call
    --     campaign = Campaign.objects.get(pk=obj_callrequest.campaign.id)
    --     if not campaign.completed:
    --         campaign.completed = 1
    --     else:
    --         campaign.completed = campaign.completed + 1
    --     campaign.save()

    debug_output = ''
    self.debugger:msg("INFO", "current_node.type >>>>> "..current_node.type)

    if current_node.type == PLAY_MESSAGE then
        number_digits = 1
        timeout = 1
        debug_output = debug_output.."PLAY_MESSAGE"
        session:streamFile(AUDIO_WELCOME)

    elseif current_node.type == HANGUP_SECTION then
        debug_output = debug_output.."HANGUP_SECTION<br/>------------------<br/>"
        html = '<Response> %s <Hangup/> </Response>' % html_play

    elseif current_node.type == MULTI_CHOICE then
        number_digits = 1
        --dtmf_filter = list_section[current_state].build_dtmf_filter()
        dtmf_filter = '123456789*'
        debug_output = debug_output.."MULTI_CHOICE<br/>------------------<br/>"
        -- digits = session:playAndGetDigits (
        --       min_digits, max_digits, max_attempts, timeout, terminators,
        --       prompt_audio_files, input_error_audio_files,
        --       digit_regex, variable_name, digit_timeout,
        --       transfer_on_failure)

        -- Multi Choice
        press_digit = session:playAndGetDigits(1, 1, 3, 4000, '#', AUDIO_PRESSDIGIT, invalid_input, '\\d+|#')
        debug("info", "result digit => " .. press_digit )

    elseif current_node.type == RATING_SECTION then
        if current_node.rating_laps and string.len(current_node.rating_laps) > 0 then
            number_digits = string.len(current_node.rating_laps)
        else
            number_digits = 1
        end
        debug_output = debug_output.."RATING_SECTION<br/>------------------<br/>"
        -- Multi Choice
        press_digit = session:playAndGetDigits(1, 1, 3, 4000, '#', AUDIO_PRESSDIGIT, invalid_input, '\\d+|#')
        debug("info", "result digit => " .. press_digit )

    elseif current_node.type == CAPTURE_DIGITS then
        number_digits = current_node.number_digits
        if not number_digits then
            number_digits = 1
        end
        debug_output = debug_output.."CAPTURE_DIGITS<br/>------------------<br/>"
        press_digit = session:playAndGetDigits(1, 1, 3, 4000, '#', AUDIO_PRESSDIGIT, invalid_input, '\\d+|#')
        debug("info", "result digit => " .. press_digit )

    elseif current_node.type == RECORD_MSG then
        debug_output = debug_output.."RECORD_MSG<br/>------------------<br/>"
        --timeout : Seconds of silence before considering the recording complete
        -- syntax is session:recordFile(file_name, max_len_secs, silence_threshold, silence_secs)
        max_len_secs = 120
        silence_threshold = 30
        silence_secs = 5
        -- Python setting = FS_RECORDING_PATH
        id_recordfile = math.random(10000000, 99999999);
        recording_filename = "/tmp/recording-".."-"..id_recordfile..".wav"
        result_rec = session:recordFile(recording_filename, max_len_secs, silence_threshold, silence_secs)

    else
        debug_output = debug_output.."EXCEPTIONH -> HANGUP"
        self:end_call()
    end

end
