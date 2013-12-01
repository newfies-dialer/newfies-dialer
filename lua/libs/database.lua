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

--TODO: It might worth to rename this to model.lua

require "constant"
local oo = require "loop.simple"
local dbhanlder = require "dbhandler"
-- local dbh_fs = require "dbh_fs"
-- local dbh_fs = require "dbh_light"



-- redis.commands.expire = redis.command('EXPIRE')
-- redis.commands.ttl = redis.command('TTL')

Database = oo.class{
    -- default field values
    DG_SURVEY_ID = false,
    TABLE_SECTION = 'survey_section',
    TABLE_BRANCHING = 'survey_branching',
    env = nil,
    con = nil,
    list_section = nil,
    list_branching = nil,
    list_audio = nil,
    campaign_info = nil,
    user_id = nil,
    valid_data = true,
    app_type = 'survey', -- survey or voice_app
    start_node = false,
    debugger = nil,
    results = {},
    caching = false,
    event_alarm = nil,
}

function Database:__init(debug_mode, debugger)
    -- self is the class
    return oo.rawnew(self, {
        debug_mode = debug_mode,
        -- debugger = nil,
        -- dbh = DBH(debug_mode, nil),
        debugger = debugger,
        dbh = DBH(debug_mode, debugger),
    })
end

function Database:connect()
    self.dbh:connect()
end

function Database:disconnect()
    self.dbh:disconnect()
end

function Database:db_debugger(level, msg)
    if self.debugger then
        self.debugger:msg(level, msg)
    end
end

function Database:db_debugger_inspect(level, msg)
    if self.debugger then
        self.debugger:msg_inspect(level, msg)
    end
end

function Database:load_survey_section(survey_id)
    -- id   order   type    question    script  audiofile_id    retries timeout
    -- key_0    key_1   key_2   key_3   key_4   key_5   key_6   key_7   key_8   key_9
    -- rating_laps  validate_number number_digits   phonenumber completed   created_date
    -- updated_date survey_id   invalid_audiofile_id    min_number  max_number
    local sqlquery = "SELECT * FROM "..self.TABLE_SECTION.." WHERE survey_id="..survey_id.." ORDER BY "..self.TABLE_SECTION..".order"
    self:db_debugger("DEBUG", "Load survey section : "..sqlquery)
    local qresult = self.dbh:get_cache_list(sqlquery, 300)

    local list = {}
    local low_order = -1
    for i,row in pairs(qresult) do
        self:db_debugger("DEBUG", string.format("id:%15d  question:%-15s type:%-15s order:%-15s", row.id, row.question, row.type, row.order))
        if tonumber(row.order) < low_order or low_order < 0 then
            low_order = tonumber(row.order)
            self.start_node = row.id
        end

        list[tonumber(row['id'])] = row
    end
    self:db_debugger("DEBUG", string.format("start_node:%15d", self.start_node))
    self:db_debugger_inspect("DEBUG", list)
    self.list_section = list
    if not self.start_node then
        self:db_debugger("ERROR", "Error Loading Survey Section")
    end
end

function Database:load_survey_branching(survey_id)
    -- id   keys section_id goto_id
    local sqlquery = "SELECT "..self.TABLE_BRANCHING..".id, keys, section_id, goto_id "..
        "FROM "..self.TABLE_BRANCHING.." LEFT JOIN "..self.TABLE_SECTION..
        " ON "..self.TABLE_SECTION..".id="..self.TABLE_BRANCHING..".section_id "..
        "WHERE survey_id="..survey_id
    self:db_debugger("DEBUG", "Load survey branching : "..sqlquery)
    local qresult = self.dbh:get_cache_list(sqlquery, 300)

    local list = {}
    for i,row in pairs(qresult) do
        if not list[tonumber(row['section_id'])] then
            list[tonumber(row['section_id'])] = {}
        end
        list[tonumber(row['section_id'])][tostring(row.keys)] = row
    end
    self:db_debugger_inspect("DEBUG", list)
    self.list_branching = list
end


function Database:load_audiofile()
    -- id   name    audio_file  user_id
    local sqlquery = "SELECT * FROM audio_file WHERE user_id="..self.user_id
    self:db_debugger("DEBUG", "Load audiofile branching : "..sqlquery)
    self.list_audio = self.dbh:get_cache_list(sqlquery, 300)
    self:db_debugger_inspect("DEBUG", self.list_audio)
end

function Database:load_campaign_info(campaign_id)
    local sqlquery = "SELECT dialer_campaign.*, dialer_gateway.gateways FROM dialer_campaign LEFT JOIN dialer_gateway "..
        "ON dialer_gateway.id=aleg_gateway_id WHERE dialer_campaign.id="..campaign_id
    self:db_debugger("DEBUG", "Load campaign info : "..sqlquery)
    self.campaign_info = self.dbh:get_cache_object(sqlquery, 300)
    if not self.campaign_info then
        return false
    end
    self.user_id = self.campaign_info["user_id"]
end

function Database:test_get_campaign()
    local sqlquery = "SELECT * FROM dialer_campaign ORDER BY DESC id"
    self:db_debugger("DEBUG", "Get campaign list : "..sqlquery)
    self.contact = self.dbh:get_object(sqlquery)
end

function Database:load_contact(contact_id)
    local sqlquery = "SELECT * FROM dialer_contact WHERE id="..contact_id
    self:db_debugger("DEBUG", "Load contact data : "..sqlquery)
    self.contact = self.dbh:get_object(sqlquery)
end

function Database:load_content_type()
    local sqlquery = "SELECT id FROM django_content_type WHERE model='survey'"
    self:db_debugger("DEBUG", "Load content_type : "..sqlquery)
    local result = self.dbh:get_cache_object(sqlquery, 300)
    return result["id"]
end

function Database:update_subscriber(subscriber_id, status)
    if subscriber_id and subscriber_id ~= 'None' then
        local sqlquery = "UPDATE dialer_subscriber SET status='"..status.."' WHERE id="..subscriber_id
        self:db_debugger("DEBUG", "Update Subscriber : "..sqlquery)
        local res = self.dbh:execute(sqlquery)
        self:update_campaign_completed()
    end
end

function Database:update_campaign_completed()
    local sqlquery = "UPDATE dialer_campaign SET completed = completed + 1 WHERE id="..self.campaign_info.id
    self:db_debugger("DEBUG", "Update Campaign : "..sqlquery)
    local res = self.dbh:execute(sqlquery)
end

function Database:update_callrequest_cpt(callrequest_id)
    local sqlquery = "UPDATE dialer_callrequest SET completed = 't' WHERE id="..callrequest_id
    self:db_debugger("DEBUG", "Update CallRequest : "..sqlquery)
    local res = self.dbh:execute(sqlquery)
end

function Database:load_alarm_event(alarm_request_id)
    local sqlquery = "SELECT event_id, alarm_id, appointment_alarm.survey_id as survey_id, manager_id, data, "..
        "voicemail, amd_behavior, voicemail_audiofile_id FROM appointment_alarmrequest "..
        "LEFT JOIN appointment_alarm ON appointment_alarm.id=alarm_id "..
        "LEFT JOIN appointment_event ON appointment_event.id=appointment_alarm.event_id "..
        "LEFT JOIN calendar_user_profile ON calendar_user_profile.user_id=creator_id "..
        "LEFT JOIN calendar_setting ON calendar_setting.id=calendar_setting_id "..
        "WHERE appointment_alarmrequest.id="..alarm_request_id

    self:db_debugger("DEBUG", "Load Event Data : "..sqlquery)
    self.event_alarm = self.dbh:get_object(sqlquery)

    -- local inspect = require 'inspect'
    -- print(inspect(self.event_alarm))
    -- print(self.event_alarm.manager_id)
    -- print(self.event_alarm.alarm_id)
    self.user_id = self.event_alarm.manager_id
end

function Database:load_all_alarm_request(alarm_request_id)

    self:load_alarm_event(alarm_request_id)
    if not self.event_alarm then
        self:db_debugger("ERROR", "Error: No Event")
        return false
    end
end

function Database:load_all(campaign_id, contact_id, alarm_request_id)

    if contact_id=='None' or campaign_id=='None' then
        -- ALARM
        self:load_all_alarm_request(alarm_request_id)
        self:load_survey_section(self.event_alarm.survey_id)
        self:load_survey_branching(self.event_alarm.survey_id)
        self:load_audiofile()
        return self.event_alarm.survey_id
    end

    -- CAMPAIGN
    self:load_contact(contact_id)
    if not self.contact then
        self:db_debugger("ERROR", "Error: No Contact")
        return false
    end

    self:load_campaign_info(campaign_id)
    if not self.campaign_info then
        self:db_debugger("ERROR", "Error: No Campaign")
        return false
    end

    local content_type_id = self:load_content_type()
    if tonumber(self.campaign_info.content_type_id) == tonumber(content_type_id) then
        self.app_type = 'survey'
    else
        self.app_type = 'voice_app'
        self:db_debugger("ERROR", "Error: voice_app("..self.campaign_info.content_type_id..
            ") is not supported")
        return false
    end
    local survey_id = self.campaign_info.object_id
    if self.DG_SURVEY_ID and self.DG_SURVEY_ID > 0 then
        survey_id = self.DG_SURVEY_ID
    end
    self:load_survey_section(survey_id)
    self:load_survey_branching(survey_id)
    self:load_audiofile()
    return survey_id
end

function Database:check_data()
    --Check if we retrieve Campaign Info
    if not self.campaign_info and not self.event_alarm then
        self:db_debugger("ERROR", "campaign_info or event_alarm no valid")
        self.valid_data = false
    end
    --Check if we retrieve List Section
    if not self.list_section then
        self:db_debugger("ERROR", "list_section no valid")
        self.valid_data = false
    end
    --Check we got a start_node
    if not self.start_node then
        self:db_debugger("ERROR", "start_node no valid")
        self.valid_data = false
    end
    return self.valid_data
end

function Database:save_result_mem(callrequest_id, section_id, record_file, recording_duration, response)
    --We save the result in memory and we will commit later when the call stop
    self.results[tonumber(section_id)] = {callrequest_id, section_id, record_file, recording_duration, response, os.time()}
end

function Database:commit_result_mem(survey_id)
    --Commit all results with one bulk insert to the Database
    local sql_result = ''
    local count = 0
    for k, v in pairs(self.results) do
        count = count + 1
        if count > 1 then
            sql_result = sql_result..","
        end
        sql_result = sql_result.."("..v[1]..", "..v[2]..", '"..v[3].."', "..v[4]..", '"..v[5].."', CURRENT_TIMESTAMP("..v[6].."))"
        --Save Aggregate result
        --TODO: For performance replace this by a celery task which will read 1000 survey_result and aggregate them in block
        self:set_aggregate_result(survey_id, v[2], v[5], v[4])
    end
    local sqlquery = "INSERT INTO survey_result "..
        "(callrequest_id, section_id, record_file, recording_duration, response, created_date) VALUES "..sql_result
    if count > 0 then
        self:db_debugger("DEBUG", "Insert Bulk Result : "..sqlquery)
        local res = self.dbh:execute(sqlquery)
        if not res then
            self:db_debugger("ERROR", "ERROR to Insert Bulk Result : "..sqlquery)
        end
    end
end

function Database:save_result_aggregate(survey_id, section_id, response)
    local sqlquery = "INSERT INTO survey_resultaggregate (survey_id, section_id, response, count, created_date) "..
        "VALUES ("..survey_id..", "..section_id..", '"..response.."', 1, NOW())"
    self:db_debugger("DEBUG", "Save Result Aggregate:"..sqlquery)
    local res = self.dbh:execute(sqlquery)
    if not res then
        return false
    else
        return true
    end
end

function Database:add_dnc(dnc_id, phonenumber)
    local sqlquery = "INSERT INTO dnc_contact (dnc_id, phone_number, created_date, updated_date) "..
        "VALUES ("..dnc_id..", '"..phonenumber.."', NOW(), NOW())"
    self:db_debugger("DEBUG", "Insert DNC:"..sqlquery)
    local res = self.dbh:execute(sqlquery)
    if not res then
        return false
    else
        return true
    end
end

function Database:update_result_aggregate(survey_id, section_id, response)
    local sqlquery = "UPDATE survey_resultaggregate SET count = count + 1"..
        " WHERE survey_id="..survey_id.." AND section_id="..section_id.." AND response='"..response.."'"
    self:db_debugger("DEBUG", "Update Result Aggregate:"..sqlquery)
    local res = self.dbh:execute(sqlquery)
    if not res then
        return false
    else
        return true
    end
end

function Database:set_aggregate_result(survey_id, section_id, response, recording_dur)
    -- save the aggregate result for the survey
    if recording_dur and tonumber(recording_dur) > 0 then
        recording_dur = tonumber(recording_dur)
        response = 'error to detect recording duration'
        -- recording duration 0 - 20 seconds ; 20 - 40 seconds ; 40 - 60 seconds
        if recording_dur > 0 and recording_dur <= 20 then
            response = '0 - 20 seconds'
        elseif recording_dur > 20 and recording_dur <= 40 then
            response = '21 - 40 seconds'
        elseif recording_dur > 40 and recording_dur <= 60 then
            response = '41 - 60 seconds'
        elseif recording_dur > 60 and recording_dur <= 90 then
            response = '61 - 90 seconds'
        elseif recording_dur > 90 then
            response = '> 90 seconds'
        end
    end

    --TODO: Replace Insert ResultAggregate by a stored procedure PL/SQL

    -- Insert ResultAggregate
    if self:save_result_aggregate(survey_id, section_id, response) then
        -- no errors in save_result_aggregate
        return true
    else
        -- log error
        if not self:update_result_aggregate(survey_id, section_id, response) then
            self:db_debugger("ERROR", "Error update_result_aggregate")
        end
        return true
    end
end

function Database:save_section_result(callrequest_id, current_node, DTMF, record_file, recording_dur)
    -- DTMF can be false
    if not DTMF then
        DTMF = ''
    end
    -- save the result of a section
    if current_node.type == RECORD_MSG then
        --Save result to memory
        self:save_result_mem(callrequest_id, current_node.id, record_file, recording_dur, DTMF)

    elseif DTMF and string.len(DTMF) > 0 and
        (current_node.type == MULTI_CHOICE or
         current_node.type == RATING_SECTION or
         current_node.type == CAPTURE_DIGITS) then

        if current_node.type == MULTI_CHOICE then
            -- Get value for the DTMF from current_node.key_X
            if DTMF == '0' and string.len(current_node.key_0) then
                DTMF = current_node.key_0
            elseif DTMF == '1' and string.len(current_node.key_1) then
                DTMF = current_node.key_1
            elseif DTMF == '2' and string.len(current_node.key_2) then
                DTMF = current_node.key_2
            elseif DTMF == '3' and string.len(current_node.key_3) then
                DTMF = current_node.key_3
            elseif DTMF == '4' and string.len(current_node.key_4) then
                DTMF = current_node.key_4
            elseif DTMF == '5' and string.len(current_node.key_5) then
                DTMF = current_node.key_5
            elseif DTMF == '6' and string.len(current_node.key_6) then
                DTMF = current_node.key_6
            elseif DTMF == '7' and string.len(current_node.key_7) then
                DTMF = current_node.key_7
            elseif DTMF == '8' and string.len(current_node.key_8) then
                DTMF = current_node.key_8
            elseif DTMF == '9' and string.len(current_node.key_9) then
                DTMF = current_node.key_9
            end
        end
        --Save result to memory
        self:save_result_mem(callrequest_id, current_node.id, '', 0, DTMF)
    else
        --Save result to memory
        self:save_result_mem(callrequest_id, current_node.id, '', 0, DTMF)
    end
end

function Database:save_alarm_result(alarm_id, digits)
    local int_digits = tonumber(digits)
    if alarm_id and int_digits and int_digits >=0 then
        local sqlquery = "UPDATE appointment_alarm SET result="..int_digits.." WHERE id="..alarm_id
        self:db_debugger("DEBUG", "Update Alarm Result:"..sqlquery)
        local res = self.dbh:execute(sqlquery)
        if not res then
            return false
        else
            return true
        end
    end
end
