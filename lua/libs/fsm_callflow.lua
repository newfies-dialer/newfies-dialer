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

package.path = package.path .. ";/usr/share/newfies-lua/?.lua";
package.path = package.path .. ";/usr/share/newfies-lua/libs/?.lua";

local oo = require "loop.simple"
local inspect = require 'inspect'
local database = require "database"
require "tag_replace"
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
    record_filename = false,
    actionresult = false,
    lastaction_start = false,
    last_node = nil,
    ended = false,
}

function FSMCall:__init(session, debug_mode, debugger)
    -- constructor
    return oo.rawnew(self, {
        session = session,
        debug_mode = debug_mode,
        debugger = debugger,
        db = Database(debug_mode, debugger),
    })
end

function FSMCall:init()
    self.debugger:msg("DEBUG", "FSMCall:init")
    self.call_start = os.time()
    self.caller_id_name = self.session:getVariable("caller_id_name")
    self.caller_id_number = self.session:getVariable("caller_id_number")
    self.destination_number = self.session:getVariable("destination_number")
    self.uuid = self.session:getVariable("uuid")
    self.campaign_id = self.session:getVariable("campaign_id")
    self.subscriber_id = self.session:getVariable("subscriber_id")
    self.contact_id = self.session:getVariable("contact_id")
    self.callrequest_id = self.session:getVariable("callrequest_id")
    self.used_gateway_id = self.session:getVariable("used_gateway_id")

    --This is needed for Inbound test
    if not self.campaign_id or self.campaign_id == 0 or not self.contact_id then
        self.campaign_id = 46
        self.subscriber_id = 39
        self.contact_id = 39
        self.callrequest_id = 215
        self.db.DG_SURVEY_ID = 41
        --self.db.TABLE_SECTION = 'survey_section_template'
        --self.db.TABLE_BRANCHING = 'survey_branching_template'
    end

    call_id = self.uuid..'_'..self.callrequest_id
    self.debugger:set_call_id(call_id)

    self.db:connect()
    --Load All data
    self.survey_id = self.db:load_all(self.campaign_id, self.contact_id)
    if not self.survey_id then
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
    self.debugger:msg("INFO", "Start_node : "..self.db.start_node)
    self.current_node_id = self.db.start_node
    return true
end

function FSMCall:end_call()
    if self.ended then
        return true
    end
    self.ended = true

    self.debugger:msg("INFO", "FSMCall:end_call")

    --Check if we need to save the last recording
    if self.record_filename and string.len(self.record_filename) > 0 then
        current_node = self.last_node
        digits = ''
        record_filepath = FS_RECORDING_PATH..self.record_filename
        record_dur = audio_lenght(record_filepath)
        self.debugger:msg("INFO", "End_call -> Save missing recording")
        self.db:save_section_result(self.callrequest_id, current_node, digits, self.record_filename, record_dur)
    end

    --Check if we need to save the last action
    if self.actionresult and string.len(self.actionresult) > 0 then
        current_node = self.last_node
        actionduration = os.time() - self.lastaction_start
        self.actionresult = self.actionresult
        self.db:save_section_result(self.callrequest_id, current_node, self.actionresult, '', 0)
        self.actionresult = false
    end

    --Save all the result to the Database
    --TODO: Reuse connection is faster, use the opened con
    self.db:connect()
    self.db:commit_result_mem(self.campaign_id, self.survey_id)
    self.db:disconnect()

    -- NOTE: Don't use this call time for Billing / Use CDRs
    if not self.call_ended then
        self.call_ended = true
        --Estimate the call Duration
        self.call_duration = os.time() - self.call_start
        self.debugger:msg("DEBUG", "Estimated Call Duration : "..self.call_duration)
        self:hangupcall()
    end
end

function FSMCall:hangupcall()
    -- This will interrupt lua script
    self.debugger:msg("INFO", "FSMCall:hangupcall")
    self.hangup_trigger = true
    self.session:hangup()
end

function FSMCall:start_call()
    self.debugger:msg("INFO", "FSMCall:start_call...")
    self:next_node()
end

function FSMCall:playnode(current_node)
    --play the audiofile or play the audio TTS
    if current_node.audiofile_id then
        --Get audio path
        current_audio = self.db.list_audio[tonumber(current_node.audiofile_id)]
        filetoplay = UPLOAD_DIR..current_audio.audio_file
        self.debugger:msg("INFO", "StreamFile : "..filetoplay)
        self.session:streamFile(filetoplay)
    else
        --Use TTS
        mscript = tag_replace(current_node.script, self.db.contact)
        self.debugger:msg("INFO", "Speak : "..mscript)
        tts_file = tts(mscript, TTS_DIR)
        self.debugger:msg("DEBUG", "Speak TTS : "..tts_file)
        self.session:streamFile(tts_file)
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
    -- Get the node type and start playing it
    self.debugger:msg("DEBUG", "*** getdigitnode ***")
    local number_digits = 1
    local dtmf_filter = '0123456789'
    local invalid_audiofile = ''
    local timeout = tonumber(current_node.timeout)
    local retries = tonumber(current_node.retries)

    --Validate timeout
    if timeout <= 0 then
        timeout = 1 -- GetDigits 'timeout' must be a positive integer
    end
    --Validate retries
    if not retries then
        retries = 1
    elseif retries <= 0 then
        retries = 1
    else
        retries = retries + 1
    end
    --Get Invalid Audio
    if current_node.invalid_audiofile_id then
        invalid_audiofile = UPLOAD_DIR..
            self.db.list_audio[tonumber(current_node.invalid_audiofile_id)].audio_file
    end
    --Get DTMF Filter
    if current_node.type == MULTI_CHOICE then
        dtmf_filter = self:build_dtmf_filter(current_node)
    end
    --Retrieve number_digits
    if current_node.type == RATING_SECTION then
        number_digits = string.len(tostring(current_node.rating_laps))
    elseif current_node.type == CAPTURE_DIGITS then
        number_digits = current_node.number_digits
    end
    -- Function definition for playAndGetDigits
    -- digits = session:playAndGetDigits (
    --       min_digits, max_digits, max_attempts, timeout, terminators,
    --       prompt_audio_files, input_error_audio_files,
    --       digit_regex, variable_name, digit_timeout,
    --       transfer_on_failure)
    self.debugger:msg("DEBUG", "Play TTS (timeout="..tostring(timeout)..
        ",number_digits="..number_digits..", retries="..retries..
        ",invalid_audiofile="..tostring(invalid_audiofile)..
        ", dtmf_filter="..tostring(dtmf_filter)..")")

    i = 0
    while i < retries do
        i = i + 1
        self.debugger:msg("DEBUG", ">> Retries counter = "..i.." - Max Retries = "..retries)
        invalid = invalid_audiofile

        if current_node.type == RATING_SECTION or current_node.type == CAPTURE_DIGITS then
            -- for those 2 types we don't need invalid audio as we will handle this manually
            invalid = ''
        end

        --play the audiofile or play the audio TTS
        if current_node.audiofile_id then
            --Get audio path
            self.debugger:msg("DEBUG", "Play Audio to GetDigits")
            current_audio = self.db.list_audio[tonumber(current_node.audiofile_id)]
            filetoplay = UPLOAD_DIR..current_audio.audio_file
            self.debugger:msg("INFO", "Play the audiofile : "..filetoplay)

            digits = self.session:playAndGetDigits(1, number_digits, retries,
                timeout*1000, '#', filetoplay, invalid, '['..dtmf_filter..']|#')
        else
            --Use TTS
            self.debugger:msg("DEBUG", "Play TTS to GetDigits")
            mscript = tag_replace(current_node.script, self.db.contact)

            tts_file = tts(mscript, TTS_DIR)
            self.debugger:msg("INFO", "Play TTS : "..tts_file)

            digits = self.session:playAndGetDigits(1, number_digits, retries,
                timeout*1000, '#', tts_file, invalid, '['..dtmf_filter..']|#')
        end

        self.debugger:msg("INFO", "RESULT playAndGetDigits : "..digits)

        if current_node.type == RATING_SECTION then
            --break if digits is accepted
            if digits ~= '' and tonumber(digits) >= 1 and tonumber(digits) <= tonumber(current_node.rating_laps) then
                --Correct entrie, quit the loop
                break
            end
        elseif current_node.type == MULTI_CHOICE then
            --We already managed invalid on the playAndGetDigits
            break

        elseif current_node.type == CAPTURE_DIGITS and current_node.validate_number == 't'
            and digits and digits ~= '' then
            --CAPTURE_DIGITS / Check Validity
            int_dtmf = tonumber(digits)
            if int_dtmf and int_dtmf >= 0 then
                int_min = tonumber(current_node.min_number)
                int_max = tonumber(current_node.max_number)
                if not int_min then
                    int_min = 0
                end
                if not int_max then
                    int_max = 999999999999999
                end
                if int_dtmf >= int_min and int_dtmf <= int_max then
                    break
                end
            end
        end

        if invalid_audiofile ~= '' and i < retries then
            --Play invalid audiofile
            self.debugger:msg("INFO", "StreamFile Invalid : "..invalid_audiofile)
            self.session:streamFile(invalid_audiofile)
        end
    end

    return digits
end

--Used for AMD / Version of next_node only for PLAY_MESSAGE
--Review if this code is really needed, maybe can replace by next_node
function FSMCall:next_node_light()
    self.debugger:msg("INFO", "FSMCall:next_node_light (current_node="..tonumber(self.current_node_id)..")")
    local current_node = self.db.list_section[tonumber(self.current_node_id)]
    self.last_node = current_node
    self.debugger:msg("DEBUG", inspect(current_node))

    current_branching = self.db.list_branching[tonumber(self.current_node_id)]

    self:marked_node_completed(current_node)

    self.debugger:msg("DEBUG", "-------------------------------------------")
    self.debugger:msg("DEBUG", "TITLE :: ("..current_node.id..") "..current_node.question)
    self.debugger:msg("DEBUG", "NODE TYPE ==> "..SECTION_TYPE[current_node.type])

    --
    --Run Action
    --
    if current_node.type == PLAY_MESSAGE then
        self:playnode(current_node)
    else
        self.debugger:msg("ERROR", "next_node_light need to be a PLAY_MESSAGE : "..current_node.type)
        self:end_call()
        return false
    end

    --
    --Check Branching / Find the next node
    --
    self.debugger:msg("DEBUG", inspect(current_branching))

    if current_node.type == PLAY_MESSAGE then
        --Check for timeout
        if (not current_branching["0"] or not current_branching["0"].goto_id) and
           (not current_branching["timeout"] or not current_branching["timeout"].goto_id) then
            --Go to hangup
            self.debugger:msg("DEBUG", "No more branching -> Goto Hangup")
            self:end_call()
        else
            if current_branching["0"] and current_branching["0"].goto_id then
                self.current_node_id = tonumber(current_branching["0"].goto_id)
            elseif current_branching["timeout"] and current_branching["timeout"].goto_id then
                self.current_node_id = tonumber(current_branching["timeout"].goto_id)
            end
        end
    end
    return true
end

function FSMCall:marked_node_completed(current_node)
    if (current_node.completed == 't' and not self.marked_completed) then
        self.db:connect()
        --Mark the subscriber as completed and increment campaign completed field
        self.db:update_subscriber(self.subscriber_id, SUBSCRIBER_COMPLETED)
        --Flag Callrequest
        self.db:update_callrequest_cpt(self.callrequest_id)
        self.db:disconnect()
    end
end

function FSMCall:next_node()
    digits = false
    recording_filename = false

    self.debugger:msg("DEBUG", "FSMCall:next_node (current_node="..tonumber(self.current_node_id)..")")
    local current_node = self.db.list_section[tonumber(self.current_node_id)]
    self.last_node = current_node

    current_branching = self.db.list_branching[tonumber(self.current_node_id)]
    if not current_node then
        self.debugger:msg("ERROR", "Not current_node : "..type(current_node))
        self.debugger:msg("ERROR", inspect(self.db.list_section[tonumber(self.current_node_id)]))
        return false
    end

    self:marked_node_completed(current_node)

    self.debugger:msg("DEBUG", "-------------------------------------------")
    self.debugger:msg("DEBUG", "TITLE :: ("..current_node.id..") "..current_node.question)
    self.debugger:msg("DEBUG", "NODE TYPE ==> "..SECTION_TYPE[current_node.type])

    --
    --Run Action
    --
    if current_node.type == PLAY_MESSAGE then
        number_digits = 1
        timeout = 1
        self:playnode(current_node)

    elseif current_node.type == HANGUP_SECTION then
        self:playnode(current_node)
        self:end_call()

    elseif current_node.type == CALL_TRANSFER then
        self:playnode(current_node)
        phonenumber = current_node.phonenumber
        self.debugger:msg("INFO", "STARTING CALL_TRANSFER : "..phonenumber)
        if phonenumber == '' then
            self:end_call()
        else
            self.lastaction_start = os.time()

            -- Allow to hang up transfer call detecting DMTF ( *0 ) in LEG A
            session:execute("bind_meta_app","0 a o hangup::normal_clearing")

            session:setAutoHangup(false)
            callerid = self.db.campaign_info.callerid
            originate_timeout = self.db.campaign_info.calltimeout
            leg_timeout = self.db.campaign_info.calltimeout

            --dialstr = 'sofia/default/'..phonenumber..'@'..self.outbound_gateway;
            if string.find(phonenumber, "/") then
                --SIP URI call
                dialstr = phonenumber
            else
                --Use Gateway call
                dialstr = self.db.campaign_info.gateways..phonenumber
            end

            self.actionresult = 'phonenumber: '..phonenumber
            dialstr = "{hangup_after_bridge=false,origination_caller_id_number="..callerid..
                ",origination_caller_id_name="..callerid..",originate_timeout="..originate_timeout..
                ",leg_timeout="..leg_timeout..",legtype=bleg,callrequest_id="..self.callrequest_id..
                ",used_gateway_id="..self.used_gateway_id.."}"..dialstr

            -- originate the call
            session:execute("bridge", dialstr)
            actionduration = os.time() - self.lastaction_start

            -- get disposition status
            originate_disposition = session:getVariable("originate_disposition") or ''
            if originate_disposition ~= 'SUCCESS' then
                actionduration = 0
            end
            freeswitch.consoleLog("info", "END CALL_TRANSFER callduration:"..actionduration.." - originate_disposition:"..originate_disposition)

            self.actionresult = 'phonenumber: '..phonenumber
            --.." duration: "..actionduration
            self.db:save_section_result(self.callrequest_id, current_node, self.actionresult, '', 0)
            self.actionresult = false
        end

    elseif current_node.type == CONFERENCE then
        self:playnode(current_node)
        conference = current_node.conference
        self.debugger:msg("INFO", "STARTING CONFERENCE : "..conference)
        if conference == '' then
            conference = self.campaign_id
        end
        self.lastaction_start = os.time()
        self.actionresult = 'conf: '..conference
        self.session:execute("conference", conference..'@default')
        actionduration = os.time() - self.lastaction_start
        self.debugger:msg("INFO", "END CONFERENCE : duration "..actionduration)

        self.actionresult = 'conf: '..conference
        --.." duration:"..actionduration
        self.db:save_section_result(self.callrequest_id, current_node, self.actionresult, '', 0)
        self.actionresult = false

    elseif current_node.type == DNC then
        --Add this phonenumber to the DNC campaign list
        self.db:connect()
        self.db:add_dnc(self.db.campaign_info.dnc_id, self.destination_number)
        self.db:disconnect()
        --Play Node
        self:playnode(current_node)
        self:end_call()

    elseif current_node.type == MULTI_CHOICE then
        digits = self:getdigitnode(current_node)
        self.debugger:msg("INFO", "result digit => "..digits)

    elseif current_node.type == RATING_SECTION then
        digits = self:getdigitnode(current_node)
        self.debugger:msg("INFO", "result digit => "..digits)

    elseif current_node.type == CAPTURE_DIGITS then
        digits = self:getdigitnode(current_node)
        self.debugger:msg("INFO", "result digit => "..digits)

    elseif current_node.type == RECORD_MSG then
        self:playnode(current_node)
        --timeout : Seconds of silence before considering the recording complete
        --syntax is session:recordFile(file_name, max_len_secs, silence_threshold, silence_secs)
        max_len_secs = 120
        silence_threshold = 30
        silence_secs = 5
        id_recordfile = math.random(10000000, 99999999)
        self.record_filename = "recording-"..current_node.id.."-"..id_recordfile..".wav"
        record_filepath = FS_RECORDING_PATH..self.record_filename
        self.debugger:msg("INFO", "STARTING RECORDING : "..record_filepath)
        result_rec = self.session:recordFile(record_filepath, max_len_secs, silence_threshold, silence_secs)
        record_dur = audio_lenght(record_filepath)
        self.debugger:msg("DEBUG", "RECORDING DONE DURATION: "..record_dur)
    else
        self.debugger:msg("DEBUG", "EXCEPTION -> HANGUP")
        self:end_call()
    end

    --
    --3. Record result and Aggregate result
    --
    if digits or self.record_filename then
        self.db:save_section_result(self.callrequest_id, current_node, digits, self.record_filename, record_dur)
        --reinit record_filename
        self.record_filename = false
        record_dur = false
    end

    --
    --Check Branching / Find the next node
    --
    self.debugger:msg("DEBUG", inspect(current_branching))

    if current_node.type == PLAY_MESSAGE
        or current_node.type == RECORD_MSG
        or current_node.type == CALL_TRANSFER
        or current_node.type == CONFERENCE then
        --Check when no branching has been created
        if (not current_branching) then
            self.debugger:msg("ERROR", "No existing branching -> Goto Hangup - nodetype:"..current_node.type)
            self:end_call()
        --Check for timeout
        elseif (not current_branching["0"] or not current_branching["0"].goto_id) and
           (not current_branching["timeout"] or not current_branching["timeout"].goto_id) then
            --Go to hangup
            self.debugger:msg("DEBUG", "No more branching -> Goto Hangup")
            self:end_call()
        else
            if current_branching["0"] and current_branching["0"].goto_id then
                self.current_node_id = tonumber(current_branching["0"].goto_id)
            elseif current_branching["timeout"] and current_branching["timeout"].goto_id then
                self.current_node_id = tonumber(current_branching["timeout"].goto_id)
            end
        end

    elseif current_node.type == MULTI_CHOICE
        or current_node.type == RATING_SECTION
        or current_node.type == CAPTURE_DIGITS then

        --Flag for invalid input
        invalid_input = false
        self.debugger:msg("DEBUG", "Check Validity")

        --Check Validity
        if current_node.type == RATING_SECTION then
            --Break if digits is accepted
            if digits == '' or tonumber(digits) < 1 or tonumber(digits) > tonumber(current_node.rating_laps) then
                self.debugger:msg("DEBUG", "RATING_SECTION invalid_input")
                invalid_input = true
            end
        elseif current_node.type == MULTI_CHOICE then
            --Break if digits is accepted
            if digits == '' then
                self.debugger:msg("DEBUG", "MULTI_CHOICE invalid_input")
                invalid_input = true
            end
        elseif current_node.type == CAPTURE_DIGITS
            and current_node.validate_number == 't'
            and digits ~= '' then
            --We have DTMF now we check validity
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
                self.debugger:msg("DEBUG", "CAPTURE_DIGITS invalid_input")
                invalid_input = true
            end
        end

        if invalid_input then
            --Invalid input
            if current_branching["invalid"] and current_branching["invalid"].goto_id then
                --We got an "invalid branching" and as we got a DTMF we shall go there
                self.debugger:msg("DEBUG", "Got 'invalid' Branching : "..current_branching["invalid"].goto_id)
                self.current_node_id = tonumber(current_branching["invalid"].goto_id)
                return true
            elseif current_branching["invalid"] then
                --There is no goto_id -> then we got to hangup
                self.debugger:msg("DEBUG", "Got 'invalid' Branching but no goto_id -> then we got to hangup")
                self:end_call()
                return true
            end
        end

        self.debugger:msg("INFO", "Got valid digit(s) : "..digits)
        --Check if we got a branching for this capture
        if digits and string.len(digits) > 0 then

            if current_branching[digits] and current_branching[digits].goto_id then
                --We got a branching for this DTMF and a goto_id
                self.current_node_id = tonumber(current_branching[digits].goto_id)
                return true

            elseif current_branching[digits] then
                --We got a branching for this DTMF but no goto_id
                self.debugger:msg("DEBUG", "We got a branching for this DTMF but no goto_id -> then we got to hangup")
                self:end_call()
                return true

            elseif current_branching["any"] and current_branching["any"].goto_id then
                --We got an "any branching" and as we got a DTMF we shall go there
                self.debugger:msg("DEBUG", "Got 'any' Branching : "..current_branching["any"].goto_id)
                self.current_node_id = tonumber(current_branching["any"].goto_id)
                return true
            elseif current_branching["any"] then
                --There is no goto_id -> then we got to hangup
                self.debugger:msg("DEBUG", "Got 'any' Branching but no goto_id -> then we got to hangup")
                self:end_call()
                return true
            else
                --Got digits but nothing accepted for this, let's stay on the same node
                self.debugger:msg("DEBUG", "Got digits but nothing accepted for this, let's stay on the same node")
                --If Rating and it's value
                if current_node.type == RATING_SECTION and not invalid_input then
                    self.debugger:msg("DEBUG", "It's a valid input but there is no branching for it, so we hangup")
                    self:end_call()
                end
                return true
            end
        end

        --Check if we got a branching for this capture
        if not digits or string.len(digits) == 0 then
            --Check if there is a timeout / you should
            if not current_branching["timeout"] or not current_branching["timeout"].goto_id then
                --Go to hangup
                self.debugger:msg("DEBUG", "No more branching -> Goto Hangup")
                self:end_call()
            else
                self.current_node_id = tonumber(current_branching["timeout"].goto_id)
            end
        end
    end

    return true
end
