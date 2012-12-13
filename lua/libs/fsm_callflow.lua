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
local PLAY_MESSAGE = "1"
local MULTI_CHOICE = "2"
local RATING_SECTION = "3"
local CAPTURE_DIGITS = "4"
local RECORD_MSG = "5"
local CALL_TRANSFER = "6"
local HANGUP_SECTION = "7"

local SECTION_TYPE = {}
SECTION_TYPE["1"] = "PLAY_MESSAGE"
SECTION_TYPE["2"] = "MULTI_CHOICE"
SECTION_TYPE["3"] = "RATING_SECTION"
SECTION_TYPE["4"] = "CAPTURE_DIGITS"
SECTION_TYPE["5"] = "RECORD_MSG"
SECTION_TYPE["6"] = "CALL_TRANSFER"
SECTION_TYPE["7"] = "HANGUP_SECTION"

local AUDIODIR = '/home/areski/public_html/django/MyProjects/newfies-dialer/newfies/usermedia/tts/'
local AUDIO_WELCOME = AUDIODIR..'script_9805d01afeec350f36ff3fd908f0cbd5.wav'
local AUDIO_ENTERAGE = AUDIODIR..'script_4ee73b76b5b4c5d596ed1cb3257861f0.wav'
local AUDIO_PRESSDIGIT = AUDIODIR..'script_610e09c761c4b592aaa954259ce4ce1d.wav'


FSMCall = oo.class{
    -- default field values
    call_ended = false,
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


function FSMCall:next_node()
    self.debugger:msg("INFO", "FSMCall:next_node (current_node="..tonumber(self.current_node_id)..")")
    local current_node = self.db.list_section[tonumber(self.current_node_id)]
    current_branching = self.db.list_branching[tonumber(self.current_node_id)]
    if not current_node then
        print(type(current_node))
        print ("Not current_node")
        print(inspect(self.db.list_section[tonumber(self.current_node_id)]))
        return false
    end

    print(inspect(current_node))
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
    self.debugger:msg("INFO", "TITLE :: ("..current_node.id..") "..current_node.question)
    self.debugger:msg("INFO", "-------------------------------------------")


    --
    -- Run Action
    --

    if current_node.type == PLAY_MESSAGE then
        number_digits = 1
        timeout = 1
        debug_output = debug_output.."PLAY_MESSAGE"
        session:streamFile(AUDIO_WELCOME)

    elseif current_node.type == HANGUP_SECTION then
        debug_output = debug_output.."EXCEPTION -> HANGUP"
        self:end_call()

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
        cap_dtmf = session:playAndGetDigits(1, 1, 3, 4000, '#', AUDIO_PRESSDIGIT, invalid_input, '\\d+|#')
        self.debugger:msg("info", "result digit => " .. cap_dtmf )

    elseif current_node.type == RATING_SECTION then
        if current_node.rating_laps and string.len(current_node.rating_laps) > 0 then
            number_digits = string.len(current_node.rating_laps)
        else
            number_digits = 1
        end
        debug_output = debug_output.."RATING_SECTION<br/>------------------<br/>"
        -- Multi Choice
        cap_dtmf = session:playAndGetDigits(1, 1, 3, 4000, '#', AUDIO_PRESSDIGIT, invalid_input, '\\d+|#')
        self.debugger:msg("INFO", "result digit => " .. cap_dtmf )

    elseif current_node.type == CAPTURE_DIGITS then
        number_digits = current_node.number_digits
        if not number_digits then
            number_digits = 1
        end
        debug_output = debug_output.."CAPTURE_DIGITS<br/>------------------<br/>"
        cap_dtmf = session:playAndGetDigits(1, 1, 3, 4000, '#', AUDIO_PRESSDIGIT, invalid_input, '\\d+|#')
        self.debugger:msg("INFO", "result digit => " .. cap_dtmf )

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
        debug_output = debug_output.."EXCEPTION -> HANGUP"
        self:end_call()
    end


    --
    -- 3. Record result / Aggregate result
    --

    -- TODO: Record result / Aggregate result

    --
    -- Check Branching / Find the next node
    --

    print("---------------------")
    print(current_node.type)
    print("NODE TYPE ==> "..SECTION_TYPE[current_node.type])
    print(inspect(current_branching))

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

        --CAPTURE_DIGITS / Check Validity
        --{PYTHON CODE}
        -- if (obj_p_section.type == SECTION_TYPE.CAPTURE_DIGITS
        --    and obj_p_section.validate_number):
        --     #check if number is valid
        --     try:
        --         int_dtmf = int(DTMF)
        --     except:
        --         #No correct input from user
        --         int_dtmf = False

        --     try:
        --         int_min = int(obj_p_section.min_number)
        --         int_max = int(obj_p_section.max_number)
        --     except:
        --         int_min = 0
        --         int_max = 999999999999999

        --     if (int_dtmf and (int_dtmf < int_min
        --        or int_dtmf > int_max)):
        --         #Invalid input
        --         try:
        --             #DTMF doesn't have any branching so let's check for any
        --             branching = Branching.objects.get(
        --                 keys='invalid',
        --                 section=obj_p_section)
        --             exit_action = 'INVALID'
        --         except Branching.DoesNotExist:
        --             branching = False


        self.debugger:msg("INFO", "Got -------------------------> : "..cap_dtmf)
        -- check if we got a branching for this capture
        if cap_dtmf or string.len(cap_dtmf) >= 0 then

            if current_branching[cap_dtmf] then
                if current_branching[cap_dtmf].goto_id then
                    print("2OK")
                end
                print("1OK")
            end
            if current_branching[cap_dtmf] and current_branching[cap_dtmf].goto_id then
                self.current_node_id = tonumber(current_branching[cap_dtmf].goto_id)
                return true
            elseif current_branching["any"] and current_branching["any"].goto_id then
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
        if not cap_dtmf or string.len(cap_dtmf) == 0 then
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
