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

package.path = package.path .. ";/home/areski/public_html/django/MyProjects/newfies-dialer/lua/?.lua";
package.path = package.path .. ";/home/areski/public_html/django/MyProjects/newfies-dialer/lua/libs/?.lua";

local oo = require "loop.simple"
local inspect = require 'inspect'
local database = require "database"
require "texttospeech"
require "constant"


FSMCall = oo.class{
    -- default field values
    call_ended = false,
    extension_list = nil,
    caller_id_name = nil,
    caller_id_number = nil,
    destination_number = nil,
    uuid = nil,
    marked_completed = false,
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
    self.subscriber_id = self.session:getVariable("subscriber_id")
    self.callrequest_id = self.session:getVariable("callrequest_id")
    self.campaign_id = 23
    self.subscriber_id = 15
    self.callrequest_id = 30

    self.db:connect()
    if not self.db:load_all(self.campaign_id, self.subscriber_id) then
        self.debugger:msg("ERROR", "Error loading data")
        self:hangupcall()
        return false
    end
    self.db:check_data()
    self.db:disconnect()
    --print(inspect(self.db.list_section[tonumber(self.db.start_node)]))
    if not self.db.valid_data then
        self.debugger:msg("ERROR", "Error invalid data")
        self:hangupcall()
        return false
    end
    self.debugger:msg("INFO", "start_node--->"..self.db.start_node)
    self.current_node_id = self.db.start_node
end

function FSMCall:end_call()
    self.debugger:msg("ERROR", "FSMCall:end_call")
    -- NOTE: Don't use this call time for Billing
    -- Use FS CDRs
    if not self.call_ended then
        self.call_ended = true
        --Duration call
        self.call_duration = os.time() - self.call_start
        self.debugger:msg("DEBUG", "Estimated Call Duration : "..self.call_duration)
        self:hangupcall()
    end
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


function FSMCall:playnode(current_node)
    --play the audiofile or play the audio TTS
    if current_node.audiofile_id then
        --Get audio path
        current_audio = self.db.list_audio[tonumber(current_node.audiofile_id)]
        filetoplay = UPLOAD_DIR..current_audio.audio_file
        self.debugger:msg("INFO", "\n--->> streamFile : "..filetoplay)
        self.session:streamFile(filetoplay)
    else
        --Use TTS
        self.session:set_tts_parms("flite", "kal")
        self.debugger:msg("INFO", "\n--->> Speak : "..current_node.script)
        self.session:speak(current_node.script)
    end
end

--local digits = session:playAndGetDigits(1, 1, 2,4000, "#", "phrase:voicemail_record_file_check:1:2:3", invalid,"\\d{1}")

function FSMCall:build_dtmf_filter(current_node)
    -- Build the dtmf filter to capture digits
    dtmffilter = ''
    if current_node.key_0 and string.len(current_node.key_0) > 0 then
        dtmffilter = dtmffilter..'0'
    end
    if current_node.key_1 and string.len(current_node.key_1) > 0 then
        dtmffilter = dtmffilter..'1'
    end
    if current_node.key_2 and string.len(current_node.key_2) > 0 then
        dtmffilter = dtmffilter..'2'
    end
    if current_node.key_3 and string.len(current_node.key_3) > 0 then
        dtmffilter = dtmffilter..'3'
    end
    if current_node.key_4 and string.len(current_node.key_4) > 0 then
        dtmffilter = dtmffilter..'4'
    end
    if current_node.key_5 and string.len(current_node.key_5) > 0 then
        dtmffilter = dtmffilter..'5'
    end
    if current_node.key_6 and string.len(current_node.key_6) > 0 then
        dtmffilter = dtmffilter..'6'
    end
    if current_node.key_7 and string.len(current_node.key_7) > 0 then
        dtmffilter = dtmffilter..'7'
    end
    if current_node.key_8 and string.len(current_node.key_8) > 0 then
        dtmffilter = dtmffilter..'8'
    end
    if current_node.key_9 and string.len(current_node.key_9) > 0 then
        dtmffilter = dtmffilter..'9'
    end
    return dtmffilter
end

function FSMCall:getdigitnode(current_node)
    self.debugger:msg("INFO", "*** getdigitnode ***")
    number_digits = 1
    dtmf_filter = '0123456789'
    -- Get the node type and start playing it
    timeout = tonumber(current_node.timeout)
    if timeout <= 0 then
        timeout = 1 -- GetDigits 'timeout' must be a positive integer
    end
    -- Get number of retries
    retries = tonumber(current_node.retries)
    if not retries then
        retries = 1
    end

    --Invalid Audio
    if current_node.invalid_audiofile_id then
        invalid_audiofile = self.db.list_audio[tonumber(current_node.invalid_audiofile_id)]
    else
        invalid_audiofile = ''
    end

    if current_node.type == MULTI_CHOICE then
        dtmf_filter = self:build_dtmf_filter(current_node)
    end

    -- retrieve number_digits
    if current_node.type == RATING_SECTION then
        number_digits = string.len(tostring(current_node.rating_laps))
    elseif current_node.type == CAPTURE_DIGITS then
        number_digits = current_node.number_digits
    end

    -- digits = session:playAndGetDigits (
    --       min_digits, max_digits, max_attempts, timeout, terminators,
    --       prompt_audio_files, input_error_audio_files,
    --       digit_regex, variable_name, digit_timeout,
    --       transfer_on_failure)

    --play the audiofile or play the audio TTS
    if current_node.audiofile_id then
        --Get audio path
        current_audio = self.db.list_audio[tonumber(current_node.audiofile_id)]
        filetoplay = UPLOAD_DIR..current_audio.audio_file
        self.debugger:msg("INFO", "\nPlay the audiofile : "..filetoplay)

        digits = self.session:playAndGetDigits(1, number_digits, retries,
            timeout*1000, '#', filetoplay, invalid_audiofile, dtmf_filter)
    else
        --Use TTS
        --TODO: Build placeholder_replace
        script = self.db:placeholder_replace(current_node.script)

        tts_file = tts(current_node.script, TTS_DIR)
        self.debugger:msg("INFO", "\nPlay TTS : "..tts_file)
        digits = self.session:playAndGetDigits(1, number_digits, retries,
            timeout*1000, '#', tts_file, invalid_audiofile, dtmf_filter)
    end
    return digits
end

function FSMCall:next_node()
    digits = false
    recording_filename = false

    self.debugger:msg("INFO", "FSMCall:next_node (current_node="..tonumber(self.current_node_id)..")")
    local current_node = self.db.list_section[tonumber(self.current_node_id)]
    current_branching = self.db.list_branching[tonumber(self.current_node_id)]
    if not current_node then
        self.debugger:msg("ERROR", "Not current_node : "..type(current_node))
        self.debugger:msg("ERROR", inspect(self.db.list_section[tonumber(self.current_node_id)]))
        return false
    end

    if (current_node.completed == 't' and not self.marked_completed) then
        -- Mark the subscriber as completed and increment campaign completed field
        self.db:update_subscriber(self.subscriber_id, SUBSCRIBER_COMPLETED)
        --Flag Callrequest
        self.db:update_callrequest_cpt(self.callrequest_id)
    end

    --self.debugger:msg("INFO", "current_node.type >>>>> "..current_node.type)
    self.debugger:msg("INFO", "-------------------------------------------")
    self.debugger:msg("INFO", "TITLE :: ("..current_node.id..") "..current_node.question)
    self.debugger:msg("INFO", "NODE TYPE ==> "..SECTION_TYPE[current_node.type])

    --
    -- Run Action
    --
    if current_node.type == PLAY_MESSAGE then
        number_digits = 1
        timeout = 1
        self:playnode(current_node)

    elseif current_node.type == HANGUP_SECTION then
        self:playnode(current_node)
        self:end_call()

    elseif current_node.type == MULTI_CHOICE then
        digits = self:getdigitnode(current_node)
        self.debugger:msg("INFO", "result digit => " .. digits )

    elseif current_node.type == RATING_SECTION then
        digits = self:getdigitnode(current_node)
        self.debugger:msg("INFO", "result digit => " .. digits )

    elseif current_node.type == CAPTURE_DIGITS then
        digits = self:getdigitnode(current_node)
        self.debugger:msg("INFO", "result digit => " .. digits )

    elseif current_node.type == RECORD_MSG then
        --timeout : Seconds of silence before considering the recording complete
        -- syntax is session:recordFile(file_name, max_len_secs, silence_threshold, silence_secs)
        max_len_secs = 120
        silence_threshold = 30
        silence_secs = 5
        -- Python setting = FS_RECORDING_PATH
        id_recordfile = math.random(10000000, 99999999);
        record_file = "/tmp/recording-".."-"..id_recordfile..".wav"
        result_rec = self.session:recordFile(record_file, max_len_secs, silence_threshold, silence_secs)
    else
        self.debugger:msg("INFO", "EXCEPTION -> HANGUP")
        self:end_call()
    end

    --
    -- 3. Record result and Aggregate result
    --

    -- TODO: Finish Aggregate result
    if digits or record_file then
        self.db:connect()
        self.db:save_section_result(callrequest_id, current_node, DTMF, record_file)
        self.db:disconnect()
        --TODO: Improve by saving all the result at the end of the calls
        --TODO: Bulk insert
    end

    --
    -- Check Branching / Find the next node
    --
    self.debugger:msg("DEBUG", inspect(current_branching))

    if current_node.type == PLAY_MESSAGE
        or current_node.type == RECORD_MSG
        or current_node.type == CALL_TRANSFER then
        if not current_branching["0"].goto_id then
            -- go to hangup
            self.debugger:msg("INFO", "No more branching -> Goto Hangup")
            self:end_call()
        else
            self.current_node_id = tonumber(current_branching["0"].goto_id)
        end

    elseif current_node.type == MULTI_CHOICE
        or current_node.type == RATING_SECTION
        or current_node.type == CAPTURE_DIGITS then

        -- CAPTURE_DIGITS / Check Validity
        if current_node.type == CAPTURE_DIGITS
            and current_node.validate_number == 't'
            and digits and string.len(digits) >= 0 then
            -- we have DTMF now we check validity
            int_dtmf = tonumber(digits)

            int_min = tonumber(current_node.min_number)
            int_max = tonumber(current_node.max_number)
            if not int_min then
                int_min = 0
            end
            if not int_max then
                int_max = 999999999999999
            end

            if not int_dtmf or int_dtmf < int_min or int_dtmf > int_max then
                -- Invalid input
                if current_branching["invalid"] and current_branching["invalid"].goto_id then
                    --We got an "invalid branching" and as we got a DTMF we shall go there
                    self.debugger:msg("INFO", "Got 'invalid' Branching : "..current_branching["invalid"].goto_id)
                    self.current_node_id = tonumber(current_branching["invalid"].goto_id)
                    return true
                elseif current_branching["invalid"] then
                    -- There is no goto_id -> then we got to hangup
                    self.debugger:msg("INFO", "Got 'invalid' Branching but no goto_id -> then we got to hangup")
                    self:end_call()
                    return true
                end
            end
        end

        self.debugger:msg("INFO", "Got -------------------------> : "..digits)
        -- check if we got a branching for this capture
        if digits or string.len(digits) >= 0 then

            if current_branching[digits] and current_branching[digits].goto_id then
                --We got a branching for this DTMF and a goto_id
                self.current_node_id = tonumber(current_branching[digits].goto_id)
                return true

            elseif current_branching[digits] then
                --We got a branching for this DTMF but no goto_id
                self.debugger:msg("INFO", "We got a branching for this DTMF but no goto_id -> then we got to hangup")
                self:end_call()
                return true

            elseif current_branching["any"] and current_branching["any"].goto_id then
                --We got an "any branching" and as we got a DTMF we shall go there
                self.debugger:msg("INFO", "Got 'any' Branching : "..current_branching["any"].goto_id)
                self.current_node_id = tonumber(current_branching["any"].goto_id)
                return true
            elseif current_branching["any"] then
                -- There is no goto_id -> then we got to hangup
                self.debugger:msg("INFO", "Got 'any' Branching but no goto_id -> then we got to hangup")
                self:end_call()
                return true
            else
                --We got a capture but nothing accepted for this
                --let's stay on the same node then
                self.debugger:msg("INFO", "let's stay on the same node then")
                return true
            end
        end

        -- check if we got a branching for this capture
        if not digits or string.len(digits) == 0 then
            -- check if there is a timeout / you should
            if not current_branching["timeout"].goto_id then
                -- go to hangup
                self.debugger:msg("INFO", "No more branching -> Goto Hangup")
                self:end_call()
            else
                self.current_node_id = tonumber(current_branching["timeout"].goto_id)
            end
        end

    end

    return true
end
