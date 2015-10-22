--
-- Newfies-Dialer License
-- http://www.newfies-dialer.org
--
-- This Source Code Form is subject to the terms of the Mozilla Public
-- License, v. 2.0. If a copy of the MPL was not distributed with this file,
-- You can obtain one at http://mozilla.org/MPL/2.0/.
--
-- Copyright (C) 2011-2015 Star2Billing S.L.
--
-- The primary maintainer of this project is
-- Arezqui Belaid <info@star2billing.com>
--

package.path = package.path .. ";/usr/share/newfies-lua/?.lua";
package.path = package.path .. ";/usr/share/newfies-lua/libs/?.lua";

local Database = require "database"
require "tag_replace"
require "texttospeech"
require "constant"


local FSMCall = {
    session = nil,
    debug_mode = nil,
    debugger = nil,
    db = nil,

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
    hangup_trigger = false,
    current_node_id = false,
    record_filename = false,
    actionresult = false,
    lastaction_start = false,
    last_node = nil,
    ended = false,
}

function FSMCall:new (o)
    o = o or {}   -- create object if user does not provide one
    setmetatable(o, self)
    self.__index = self
    return o
end

function FSMCall:init()
    -- Set db
    self.db = Database:new{
        debug_mode=self.debug_mode,
        debugger=self.debugger
    }
    self.db:init()
    -- Initialization
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
    self.alarm_request_id = self.session:getVariable("alarm_request_id")
    self.dialout_phone_number = self.session:getVariable("dialout_phone_number")

    --This is needed for Inbound test
    if not self.campaign_id or self.campaign_id == 0 or not self.contact_id then
        local nofs_type = 'alarm'
        if nofs_type == 'campaign' then
            -- Campaign Test
            self.campaign_id = 46
            self.subscriber_id = 39
            self.contact_id = 39
            self.callrequest_id = 215
            self.db.DG_SURVEY_ID = 41
            self.alarm_request_id = nil
        else
            -- Alarm Test
            self.campaign_id = 'None'
            self.subscriber_id = 'None'
            self.contact_id = 'None'
            self.callrequest_id = 15390
            self.db.DG_SURVEY_ID = 74
            self.alarm_request_id = 43
        end
    end

    call_id = self.uuid..'_'..self.callrequest_id
    self.debugger:set_call_id(call_id)

    -- This is the first connect
    if not self.db:connect() then
        self.debugger:msg("ERROR", "Error Connecting to database")
        self:hangupcall()
        return false
    end

    --Load All data
    self.survey_id = self.db:load_all(self.campaign_id, self.contact_id, self.alarm_request_id)
    if not self.survey_id then
        self.debugger:msg("ERROR", "Error Survey loading data")
        self:hangupcall()
        return false
    end
    self.db:check_data()
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
        local digits = ''
        local record_dur = audio_lenght(FS_RECORDING_PATH..self.record_filename)
        self.debugger:msg("INFO", "End_call -> Save missing recording")
        self.db:save_section_result(self.callrequest_id, self.last_node, digits, self.record_filename, record_dur)
    end

    --Check if we need to save the last action
    if self.actionresult and string.len(self.actionresult) > 0 then
        self.actionresult = self.actionresult
        self.db:save_section_result(self.callrequest_id, self.last_node, self.actionresult, '', 0)
        self.actionresult = false
    end

    --Save all the result to the Database
    self.db:commit_result_mem(self.survey_id)

    -- We need to keep this disconnect as it's End of Call
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
    if self.session then
        self.session:hangup()
    end
end

function FSMCall:start_call()
    self.debugger:msg("INFO", "FSMCall:start_call...")
    self:next_node()
end

function FSMCall:playnode(current_node)
    --play the audiofile or play the audio TTS
    local filetoplay = self:get_playnode_audiofile(current_node)
    if filetoplay and string.len(filetoplay) > 1 then
        self.debugger:msg("INFO", "StreamFile : "..filetoplay)
        self.session:streamFile(filetoplay)
    end
end

function FSMCall:get_playnode_audiofile(current_node)
    --get the audiofile or play the audio TTS
    if current_node.audiofile_id then
        --Get audio path
        local current_audio = self.db.list_audio[tonumber(current_node.audiofile_id)]
        local filetoplay = UPLOAD_DIR..current_audio.audio_file
        self.debugger:msg("DEBUG", "Prepare StreamFile : "..filetoplay)
        return filetoplay
    else
        --Use TTS
        local mscript = tag_replace(current_node.script, self.db.contact)
        self.debugger:msg("INFO", "Speak TTS : "..mscript)
        if mscript and mscript ~= '' then
            local tts_file = tts(mscript, TTS_DIR)
            self.debugger:msg("DEBUG", "Prepare Speak TTS : "..tostring(tts_file))
            return tts_file
        end
    end
    return false
end

function FSMCall:get_confirm_ttsfile(current_node)
    -- This function is going to be used by transfer
    local mscript = tag_replace(current_node.confirm_script, self.db.contact)
    self.debugger:msg("INFO", "Prepare Speak : "..mscript)
    if mscript and mscript ~= '' then
        local tts_file = tts(mscript, TTS_DIR)
        self.debugger:msg("DEBUG", "Prepare File for TTS : "..tostring(tts_file))
        -- if tts_file then
        --     self.session:streamFile(tts_file)
        -- end
        return tts_file
    end
    return false
end

--local digits = session:playAndGetDigits(1, 1, 2,4000, "#", "phrase:voicemail_record_file_check:1:2:3", invalid,"\\d{1}")

function FSMCall:build_dtmf_mask(current_node)
    -- Build the dtmf filter to capture digits
    local mask = ''
    if current_node.key_0 and string.len(current_node.key_0) > 0 then
        mask = mask..'0'
    end
    if current_node.key_1 and string.len(current_node.key_1) > 0 then
        mask = mask..'1'
    end
    if current_node.key_2 and string.len(current_node.key_2) > 0 then
        mask = mask..'2'
    end
    if current_node.key_3 and string.len(current_node.key_3) > 0 then
        mask = mask..'3'
    end
    if current_node.key_4 and string.len(current_node.key_4) > 0 then
        mask = mask..'4'
    end
    if current_node.key_5 and string.len(current_node.key_5) > 0 then
        mask = mask..'5'
    end
    if current_node.key_6 and string.len(current_node.key_6) > 0 then
        mask = mask..'6'
    end
    if current_node.key_7 and string.len(current_node.key_7) > 0 then
        mask = mask..'7'
    end
    if current_node.key_8 and string.len(current_node.key_8) > 0 then
        mask = mask..'8'
    end
    if current_node.key_9 and string.len(current_node.key_9) > 0 then
        mask = mask..'9'
    end
    return mask
end

function FSMCall:getdigitnode(current_node)
    -- Get the node type and start playing it
    self.debugger:msg("DEBUG", "*** getdigitnode ***")
    local number_digits = 1
    local dtmf_mask = '0123456789'
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
        dtmf_mask = self:build_dtmf_mask(current_node)
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
        ", dtmf_mask="..tostring(dtmf_mask)..")")

    local i = 0
    while i < retries do
        i = i + 1
        self.debugger:msg("DEBUG", ">> Retries counter = "..i.." - Max Retries = "..retries)
        invalid = invalid_audiofile
        digits = ''

        if current_node.type == RATING_SECTION or current_node.type == CAPTURE_DIGITS then
            -- for those 2 types we don't need invalid audio as we will handle this manually
            invalid = ''
        end

        --play the audiofile or play the audio TTS
        if current_node.audiofile_id then
            --Get audio path
            self.debugger:msg("DEBUG", "Play Audio GetDigits")
            current_audio = self.db.list_audio[tonumber(current_node.audiofile_id)]
            filetoplay = UPLOAD_DIR..current_audio.audio_file
            self.debugger:msg("INFO", "Play Audiofile : "..filetoplay)

            digits = self.session:playAndGetDigits(1, number_digits, retries,
                timeout*1000, '#', filetoplay, invalid, '['..dtmf_mask..']|#')
        else
            --Use TTS
            self.debugger:msg("DEBUG", "Play TTS GetDigits")
            mscript = tag_replace(current_node.script, self.db.contact)

            tts_file = tts(mscript, TTS_DIR)
            self.debugger:msg("INFO", "Play TTS : "..tostring(tts_file))
            if tts_file then
                digits = self.session:playAndGetDigits(1, number_digits, retries,
                    timeout*1000, '#', tts_file, invalid, '['..dtmf_mask..']|#')
            end
        end

        self.debugger:msg("INFO", "RESULT playAndGetDigits : "..digits)

        if current_node.type == RATING_SECTION then
            --break if digits is accepted
            if digits ~= '' and tonumber(digits) >= 0 and tonumber(digits) <= tonumber(current_node.rating_laps) then
                --Correct entrie, quit the loop
                break
            end
        elseif current_node.type == MULTI_CHOICE then
            --We already managed invalid on the playAndGetDigits
            break

        elseif current_node.type == CAPTURE_DIGITS
            and (current_node.validate_number == '1' or current_node.validate_number == 't')
            and digits ~= '' then
            --CAPTURE_DIGITS / Check Validity
            local int_dtmf = tonumber(digits)
            local int_max = 0  -- init
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
        elseif current_node.type == CAPTURE_DIGITS
            and not (current_node.validate_number == '1' or current_node.validate_number == 't')
            and digits ~= '' then
            self.debugger:msg("INFO", "CAPTURE_DIGITS / No Check Validity")
            break
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
    self.debugger:msg_inspect("DEBUG", current_node)

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
    self.debugger:msg_inspect("DEBUG", current_branching)

    if current_node.type == PLAY_MESSAGE then
        --Check for timeout
        if (not current_branching["0"] or not current_branching["0"].goto_id) and
           (not current_branching["timeout"] or not current_branching["timeout"].goto_id) then
            --Go to hangup
            self.debugger:msg("DEBUG", "PLAY_MESSAGE : No more branching -> Goto Hangup")
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
        --Mark the subscriber as completed and increment campaign completed field
        self.db:update_subscriber(self.subscriber_id, SUBSCRIBER_COMPLETED)
        --Flag Callrequest
        self.db:update_callrequest_cpt(self.callrequest_id)
    end
end

function FSMCall:next_node()
    local digits = false
    local recording_filename = false
    local actionduration = 0

    self.debugger:msg("DEBUG", "FSMCall:next_node (current_node="..tonumber(self.current_node_id)..")")
    local current_node = self.db.list_section[tonumber(self.current_node_id)]
    self.last_node = current_node

    local current_branching = self.db.list_branching[tonumber(self.current_node_id)]
    if not current_node then
        self.debugger:msg("ERROR", "Not current_node : "..type(current_node))
        self.debugger:msg_inspect("ERROR", self.db.list_section[tonumber(self.current_node_id)])
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
        self:playnode(current_node)

    elseif current_node.type == HANGUP_SECTION then
        self:playnode(current_node)
        self:end_call()

    elseif current_node.type == CALL_TRANSFER then
        -- Removed and replaced by Smooth-Transfer
        -- self:playnode(current_node)

        self.debugger:msg("INFO", "STARTING CALL_TRANSFER : "..current_node.phonenumber)
        if current_node.phonenumber == '' then
            self:end_call()
        else
            -- Flush the insert for the survey results when node is a Transfer
            self.db:commit_result_mem()

            self.lastaction_start = os.time()
            -- Allow to hang up transfer call detecting DMTF ( *0 ) in LEG A
            session:execute("bind_meta_app","0 a o hangup::normal_clearing")

            session:setAutoHangup(false)
            -- callerid = self.db.campaign_info.callerid
            -- CallerID display at transfer will be the contact's phonenumber
            callerid = self.dialout_phone_number
            caller_id_name = self.dialout_phone_number
            -- originate_timeout = self.db.campaign_info.calltimeout
            -- leg_timeout = self.db.campaign_info.calltimeout
            originate_timeout = 300
            leg_timeout = 300

            mcontact = mtable_jsoncontact(self.db.contact)

            local dialstr = ''
            local confirm_string = ''
            local smooth_transfer = ''

            -- check if we got a json phonenumber for transfer
            if mcontact.transfer_phonenumber then
                transfer_phonenumber = mcontact.transfer_phonenumber
            else
                transfer_phonenumber = current_node.phonenumber
            end

            new_dialout_phone_number = transfer_phonenumber

            --dialstr = 'sofia/default/'..current_node.phonenumber..'@'..self.outbound_gateway;
            if string.find(transfer_phonenumber, "/") then
                --SIP URI call
                dialstr = transfer_phonenumber
            else
                --Use Gateway call
                dialstr = self.db.campaign_info.gateways..transfer_phonenumber
            end

            -- Set SIP HEADER P-CallRequest-ID & P-Contact-ID
            -- http://wiki.freeswitch.org/wiki/Sofia-SIP#Adding_Request_Headers
            session:execute("set", "sip_h_P-CallRequest-ID="..self.callrequest_id)
            session:execute("set", "sip_h_P-Contact-ID="..self.contact_id)
            -- Set SIP HEADER P-Contact-Transfer-Ref provisioned by Contact.additional_vars.transfer_ref Json setting
            if mcontact.transfer_ref then
                session:execute("set", "sip_h_P-Contact-Transfer-Ref="..mcontact.transfer_ref)
            end

            -- Smooth-Transfer - Play audio to user while bridging the call
            transfer_audio = self:get_playnode_audiofile(current_node)
            if transfer_audio then
                -- Test audio
                -- transfer_audio = "/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-congratulations_you_pressed_star.wav"

                -- idea: try api_on_originate or api_on_pre_originate? https://wiki.freeswitch.org/wiki/Channel_Variables

                -- uuid_broadcast don't work cause the audio keep playing when the agent accept the call
                -- api = freeswitch.API()
                -- cmd = "bgapi uuid_broadcast "..self.uuid.." "..transfer_audio.." aleg"
                -- result = api:executeString(cmd)

                -- api_on_answer don't work as expect
                -- smooth_transfer = ",api_on_answer=uuid_break"..self.uuid..","

                -- Custom music on hold - Doesn't seem to work
                -- session:execute("set", "hold_music=/usr/local/freeswitch/sounds/music/8000/suite-espanola-op-47-leyenda.wav")

                -- smooth_transfer = ',api_on_pre_originate=playback'

                -- session:execute("set", "hold_music="..transfer_audio)
                -- bridge_pre_execute_aleg_app Seems broken
                -- smooth_transfer = ',bridge_pre_execute_bleg_app=playback,bridge_pre_execute_bleg_data='..transfer_audio
                -- session:execute("set", "campon=true")
                -- session:execute("set", "campon_hold_music="..transfer_audio)
                -- session:execute("set", "campon_retries=1")
                -- session:execute("set", "campon_sleep=30")
                -- session:execute("set", "campon_timeout=20")

                -- Use ringback
                -- <action application="set" data="ringback=file_string://${xxsounds}hi-long.wav!${sayname}!tone_stream://${us-ring};loops=-1"/>
                session:execute("set", "ringback=file_string://"..transfer_audio.."!tone_stream://${us-ring};loops=-1")
                session:execute("set", "transfer_ringback=file_string://"..transfer_audio.."!tone_stream://${us-ring};loops=-1")
            end

            -- Sending Ringback
            -- session:execute("set", "ringback=${us-ring}")
            -- session:execute("set", "transfer_ringback=${us-ring}")

            -- Confirm Key
            if string.len(current_node.confirm_key) == 1 and string.len(current_node.confirm_script) > 1 then
                -- Great TTS file
                confirm_file = self:get_confirm_ttsfile(current_node)
                if confirm_file and string.len(confirm_file) > 1 then
                    -- <action application="bridge" data="{group_confirm_file=playback /path/to/prompt.wav,group_confirm_key=exec,call_timeout=60} iax/guest@somebox/1234,sofia/test-int/1000@somehost"/>
                    -- confirm_file = "/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-congratulations_you_pressed_star.wav"
                    confirm_string = ',group_confirm_file='..confirm_file..',group_confirm_key='..current_node.confirm_key..',group_confirm_cancel_timeout=1'
                    -- group_confirm_read_timeout: Time in milliseconds to wait for the confirmation input (default: 5000 ms)
                end
            elseif string.len(current_node.confirm_script) > 1 then
                -- No confirm key so we want to just playback an audio to the callee before bridging the call

                -- Great TTS file
                confirm_file = self:get_confirm_ttsfile(current_node)
                if confirm_file and string.len(confirm_file) > 1 then
                    -- confirm_file = "/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-congratulations_you_pressed_star.wav"
                    -- <action application="bridge" data="{group_confirm_file=playback /path/to/prompt.wav,group_confirm_key=exec,call_timeout=60} iax/guest@somebox/1234,sofia/test-int/1000@somehost"/>
                    confirm_string = ',group_confirm_file=playback '..confirm_file..',group_confirm_key=exec,group_confirm_cancel_timeout=1'
                end
            end

            self.actionresult = 'phonenumber: '..current_node.phonenumber
            dialstr = "{ignore_early_media=true,instant_ringback=true,hangup_after_bridge=false,origination_caller_id_number="..callerid..
                ",origination_caller_id_name="..caller_id_name..",originate_timeout="..originate_timeout..
                ",leg_timeout="..leg_timeout..",legtype=bleg,callrequest_id="..self.callrequest_id..
                ",dialout_phone_number="..new_dialout_phone_number..
                ",used_gateway_id="..self.used_gateway_id..confirm_string..smooth_transfer.."}"..dialstr

            -- originate the call
            self.debugger:msg("INFO", "dialstr:"..dialstr)
            session:execute("bridge", dialstr)
            actionduration = os.time() - self.lastaction_start

            -- get disposition status
            originate_disposition = session:getVariable("originate_disposition") or ''
            if originate_disposition ~= 'SUCCESS' then
                actionduration = 0
            end
            self.debugger:msg("INFO", "END CALL_TRANSFER callduration:"..actionduration.." - originate_disposition:"..originate_disposition)

            self.actionresult = 'phonenumber: '..current_node.phonenumber
            --.." duration: "..actionduration
            self.db:save_section_result(self.callrequest_id, current_node, self.actionresult, '', 0)
            self.actionresult = false
        end

    elseif current_node.type == DNC then
        -- Add this phonenumber to the DNC campaign list
        if self.db.campaign_info.dnc_id then
            self.db:add_dnc(self.db.campaign_info.dnc_id, self.destination_number)
        end
        -- Save result
        self.actionresult = 'DNC: '..self.destination_number
        self.db:save_section_result(self.callrequest_id, current_node, self.actionresult, '', 0)
        self.actionresult = false
        -- Play Node
        self:playnode(current_node)
        self:end_call()

    elseif current_node.type == CONFERENCE then
        self:playnode(current_node)
        conference = current_node.conference
        self.debugger:msg("INFO", "STARTING CONFERENCE : "..conference)
        if conference == '' then
            conference = self.campaign_id
        end
        self.lastaction_start = os.time()
        self.session:execute("conference", conference..'@default')
        actionduration = os.time() - self.lastaction_start
        self.debugger:msg("INFO", "END CONFERENCE : duration "..actionduration)
        -- Save result
        self.actionresult = 'conf: '..conference
        self.db:save_section_result(self.callrequest_id, current_node, self.actionresult, '', 0)
        self.actionresult = false

    elseif current_node.type == SMS then
        --Send an SMS
        if current_node.sms_text and current_node.sms_text ~= '' then
            mcontact = mtable_jsoncontact(self.db.contact)
            if mcontact.sms_phonenumber then
                destination_number = mcontact.sms_phonenumber
            else
                destination_number = self.destination_number
            end

            -- Use Event to decide to whom send the SMS
            if self.db.event_data then
                dec_eventdata = decodejson(self.db.event_data)
                if dec_eventdata.sms_phonenumber then
                    destination_number = dec_eventdata.sms_phonenumber
                end
            end

            local sms_text = tag_replace(current_node.sms_text, self.db.contact)
            self.debugger:msg("INFO", "Prepare Send SMS : "..sms_text)
            self.db:send_sms(sms_text, self.survey_id, destination_number)

            -- Save result
            self.actionresult = 'SMS: '..destination_number
            self.db:save_section_result(self.callrequest_id, current_node, self.actionresult, '', 0)
            self.actionresult = false
        end
        --Play Node
        self:playnode(current_node)

    elseif current_node.type == MULTI_CHOICE then
        digits = self:getdigitnode(current_node)
        self.debugger:msg("INFO", "result digit => "..digits)

    elseif current_node.type == CAPTURE_DIGITS then
        digits = self:getdigitnode(current_node)
        self.debugger:msg("INFO", "result digit => "..digits)

    elseif current_node.type == RATING_SECTION then
        digits = self:getdigitnode(current_node)
        self.debugger:msg("INFO", "result digit => "..digits)

        -- Save the result to Alarm model
        if self.db.event_alarm and self.db.event_alarm.alarm_id then
            self.db:save_alarm_result(self.db.event_alarm.alarm_id, digits)
        end

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
        -- <action application="set" data="playback_terminators=#"/>
        --session:setVariable("playback_terminators", "#")
        session:execute("set", "playback_terminators=#")
        session:setVariable("playback_terminators", "#");
        session:setInputCallback("on_dtmf", "");
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
    self.debugger:msg_inspect("DEBUG", current_branching)

    if current_node.type == PLAY_MESSAGE
        or current_node.type == RECORD_MSG
        or current_node.type == CALL_TRANSFER
        or current_node.type == CONFERENCE
        or current_node.type == SMS then
        --Check when no branching has been created
        if (not current_branching) then
            self.debugger:msg("ERROR", "No existing branching -> Goto Hangup - nodetype:"..current_node.type)
            self:end_call()
        --Check for timeout
        elseif (not current_branching["0"] or not current_branching["0"].goto_id) and
           (not current_branching["timeout"] or not current_branching["timeout"].goto_id) then
            --Go to hangup
            self.debugger:msg("DEBUG", "Check Branching : No more branching -> Goto Hangup")
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
        local invalid_input = false
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
                self.debugger:msg("DEBUG", "MULTI_CHOICE invalid_input or maybe timeout")
                invalid_input = true

                -- in case of MULTI_CHOICE if digits is empty we might want to branch to the timeout first
                if current_branching["timeout"] and current_branching["timeout"].goto_id then
                    --We got an "timeout branching"
                    self.debugger:msg("DEBUG", "Got 'timeout' Branching : "..current_branching["timeout"].goto_id)
                    self.current_node_id = tonumber(current_branching["timeout"].goto_id)
                    return true
                elseif current_branching["timeout"] then
                    --There is no goto_id -> then we got to hangup
                    self.debugger:msg("DEBUG", "Got 'timeout' Branching but no goto_id -> then we got to hangup")
                    self:end_call()
                    return true
                end
            end
        elseif current_node.type == CAPTURE_DIGITS
            and (current_node.validate_number == '1' or current_node.validate_number == 't')
            and digits ~= '' then

            self.debugger:msg("DEBUG", "We have DTMF now we check validity")

            local int_dtmf = tonumber(digits)
            local int_min = tonumber(current_node.min_number)
            local int_max = tonumber(current_node.max_number)
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
                self.debugger:msg("DEBUG", "Check capture : No more branching -> Goto Hangup")
                self:end_call()
            else
                self.current_node_id = tonumber(current_branching["timeout"].goto_id)
            end
        end
    end

    return true
end

--define on_dtmf call back function
function on_dtmf(s, type, obj, arg)
    if (type == "dtmf") then
        freeswitch.console_log("info", "[recording] dtmf digit: " .. obj['digit'] .. ", duration: " .. obj['duration'] .. "\n");
        if (obj['digit'] == "#") then
            return 0;
        end
    end
    return 0;
end


return FSMCall
