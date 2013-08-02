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

--It might worth to rename this to model.lua

local inspect = require 'inspect'
require "constant"
local oo = require "loop.simple"
local dbhanlder = require "dbhandler"
--local dbh_fs = require "dbh_fs"


--redis.commands.expire = redis.command('EXPIRE')
--redis.commands.ttl = redis.command('TTL')

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
}

function Database:__init(debug_mode, debugger)
    -- self is the class
    return oo.rawnew(self, {
        debug_mode = debug_mode,
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

function Database:load_survey_section(survey_id)
    -- id   order   type    question    script  audiofile_id    retries timeout
    -- key_0    key_1   key_2   key_3   key_4   key_5   key_6   key_7   key_8   key_9
    -- rating_laps  validate_number number_digits   phonenumber completed   created_date
    -- updated_date survey_id   invalid_audiofile_id    min_number  max_number
    sqlquery = "SELECT * FROM "..self.TABLE_SECTION.." WHERE survey_id="..survey_id.." ORDER BY "..self.TABLE_SECTION..".order"
    self.debugger:msg("DEBUG", "Load survey section : "..sqlquery)
    qresult = self.dbh:get_cache_list(sqlquery, 300)

    list = {}
    low_order = -1
    for i,row in pairs(qresult) do
        self.debugger:msg("DEBUG", string.format("id:%15d  question:%-15s type:%-15s order:%-15s", row.id, row.question, row.type, row.order))
        if tonumber(row.order) < low_order or low_order < 0 then
            low_order = tonumber(row.order)
            self.start_node = row.id
        end

        list[tonumber(row['id'])] = row
    end
    self.debugger:msg("DEBUG", string.format("start_node:%15d", self.start_node))
    self.debugger:msg("DEBUG", inspect(list))
    self.list_section = list
    if not self.start_node then
        self.debugger:msg("ERROR", "Error Loading Survey Section")
    end
end

function Database:load_survey_branching(survey_id)
    -- id   keys section_id goto_id
    sqlquery = "SELECT "..self.TABLE_BRANCHING..".id, keys, section_id, goto_id "..
        "FROM "..self.TABLE_BRANCHING.." LEFT JOIN "..self.TABLE_SECTION..
        " ON "..self.TABLE_SECTION..".id="..self.TABLE_BRANCHING..".section_id "..
        "WHERE survey_id="..survey_id
    self.debugger:msg("DEBUG", "Load survey branching : "..sqlquery)
    qresult = self.dbh:get_cache_list(sqlquery, 300)

    list = {}
    for i,row in pairs(qresult) do
        if not list[tonumber(row['section_id'])] then
            list[tonumber(row['section_id'])] = {}
        end
        list[tonumber(row['section_id'])][tostring(row.keys)] = row
    end
    self.debugger:msg("DEBUG", inspect(list))
    self.list_branching = list
end


function Database:load_audiofile()
    -- id   name    audio_file  user_id
    sqlquery = "SELECT * FROM audio_file WHERE user_id="..self.user_id
    self.debugger:msg("DEBUG", "Load audiofile branching : "..sqlquery)
    self.list_audio = self.dbh:get_cache_list(sqlquery, 300)
    self.debugger:msg("DEBUG", inspect(self.list_audio))
end

function Database:load_campaign_info(campaign_id)
    sqlquery = "SELECT dialer_campaign.*, dialer_gateway.gateways FROM dialer_campaign LEFT JOIN dialer_gateway ON dialer_gateway.id=aleg_gateway_id WHERE dialer_campaign.id="..campaign_id
    self.debugger:msg("DEBUG", "Load campaign info : "..sqlquery)
    self.campaign_info = self.dbh:get_cache_object(sqlquery, 300)
    if not self.campaign_info then
        return false
    end
    self.user_id = self.campaign_info["user_id"]
end

function Database:load_contact(contact_id)
    sqlquery = "SELECT * FROM dialer_contact WHERE id="..contact_id
    self.debugger:msg("DEBUG", "Load contact data : "..sqlquery)
    self.contact = self.dbh:get_object(sqlquery)
end

function Database:load_content_type()
    sqlquery = "SELECt id FROM django_content_type WHERE model='survey'"
    self.debugger:msg("DEBUG", "Load content_type : "..sqlquery)
    result = self.dbh:get_cache_object(sqlquery, 300)
    return result["id"]
end

function Database:update_subscriber(subscriber_id, status)
    sqlquery = "UPDATE dialer_subscriber SET status='"..status.."' WHERE id="..subscriber_id
    self.debugger:msg("DEBUG", "Update Subscriber : "..sqlquery)
    res = self.dbh:execute(sqlquery)
    self:update_campaign_completed()
end

function Database:update_campaign_completed()
    sqlquery = "UPDATE dialer_campaign SET completed = completed + 1 WHERE id="..self.campaign_info.id
    self.debugger:msg("DEBUG", "Update Campaign : "..sqlquery)
    res = self.dbh:execute(sqlquery)
end

function Database:update_callrequest_cpt(callrequest_id)
    sqlquery = "UPDATE dialer_callrequest SET completed = 't' WHERE id="..callrequest_id
    self.debugger:msg("DEBUG", "Update CallRequest : "..sqlquery)
    res = self.dbh:execute(sqlquery)
end

function Database:load_all(campaign_id, contact_id)
    self:load_contact(contact_id)
    if not self.contact then
        self.debugger:msg("ERROR", "Error: No Contact")
        return false
    end

    self:load_campaign_info(campaign_id)
    if not self.campaign_info then
        self.debugger:msg("ERROR", "Error: No Campaign")
        return false
    end

    content_type_id = self:load_content_type()
    if tonumber(self.campaign_info.content_type_id) == tonumber(content_type_id) then
        self.app_type = 'survey'
    else
        self.app_type = 'voice_app'
        self.debugger:msg("ERROR", "Error: voice_app("..self.campaign_info.content_type_id..
            ") is not supported")
        return false
    end
    survey_id = self.campaign_info.object_id
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
    if not self.campaign_info then
        self.debugger:msg("ERROR", "campaign_info no valid")
        self.valid_data = false
    end
    --Check if we retrieve List Section
    if not self.list_section then
        self.debugger:msg("ERROR", "list_section no valid")
        self.valid_data = false
    end
    --Check we got a start_node
    if not self.start_node then
        self.debugger:msg("ERROR", "start_node no valid")
        self.valid_data = false
    end
    return self.valid_data
end

function Database:save_result_mem(callrequest_id, section_id, record_file, recording_duration, response)
    --We save the result in memory and we will commit later when the call stop
    self.results[tonumber(section_id)] = {callrequest_id, section_id, record_file, recording_duration, response, os.time()}
end

function Database:commit_result_mem(campaign_id, survey_id)
    --Commit all results with one bulk insert to the Database
    sql_result = ''
    count = 0
    for k, v in pairs(self.results) do
        count = count + 1
        if count > 1 then
            sql_result = sql_result..","
        end
        sql_result = sql_result.."("..v[1]..", "..v[2]..", '"..v[3].."', "..v[4]..", '"..v[5].."', CURRENT_TIMESTAMP("..v[6].."))"
        --Save Aggregate result
        --TODO: For performance replace this by a celery task which will read 1000 survey_result and aggregate them in block
        self:set_aggregate_result(campaign_id, survey_id, v[2], v[5], v[4])
    end
    sqlquery = "INSERT INTO survey_result "..
    "(callrequest_id, section_id, record_file, recording_duration, response, created_date) "..
    "VALUES "..sql_result
    if count > 0 then
        self.debugger:msg("DEBUG", "Insert Bulk Result : "..sqlquery)
        res = self.dbh:execute(sqlquery)
        if not res then
            self.debugger:msg("ERROR", "ERROR to Insert Bulk Result : "..sqlquery)
        end
    end
end

function Database:save_result_aggregate(campaign_id, survey_id, section_id, response)
    sqlquery = "INSERT INTO survey_resultaggregate (campaign_id, survey_id, section_id, response, count, created_date) "..
        "VALUES ("..campaign_id..", "..survey_id..", "..section_id..", '"..response.."', 1, NOW())"
    self.debugger:msg("DEBUG", "Save Result Aggregate:"..sqlquery)
    res = self.dbh:execute(sqlquery)
    if not res then
        return false
    else
        return true
    end
end

function Database:add_dnc(dnc_id, phonenumber)
    sqlquery = "INSERT INTO dnc_contact (dnc_id, phone_number, created_date, updated_date) "..
        "VALUES ("..dnc_id..", '"..phonenumber.."', NOW(), NOW())"
    self.debugger:msg("DEBUG", "Insert DNC:"..sqlquery)
    res = self.dbh:execute(sqlquery)
    if not res then
        return false
    else
        return true
    end
end

function Database:update_result_aggregate(campaign_id, survey_id, section_id, response)
    sqlquery = "UPDATE survey_resultaggregate SET count = count + 1"..
        " WHERE campaign_id="..campaign_id.." AND survey_id="..survey_id.." AND section_id="..section_id.." AND response='"..response.."'"
    self.debugger:msg("DEBUG", "Update Result Aggregate:"..sqlquery)
    res = self.dbh:execute(sqlquery)
    if not res then
        return false
    else
        return true
    end
end

function Database:set_aggregate_result(campaign_id, survey_id, section_id, response, recording_dur)
    -- save the aggregate result for the campaign / survey
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
    if self:save_result_aggregate(campaign_id, survey_id, section_id, response) then
        -- no errors in save_result_aggregate
        return true
    else
        -- log error
        if not self:update_result_aggregate(campaign_id, survey_id, section_id, response) then
            self.debugger:msg("ERROR", "Error update_result_aggregate")
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
        result = DTMF
        self:save_result_mem(callrequest_id, current_node.id, '', 0, result)
    end
end

--
-- Test Code
--
if false then
    campaign_id = 151
    survey_id = 72
    callrequest_id = 5000
    section_id = 315
    dnc_id = 1
    record_file = '/tmp/recording-file.wav'
    recording_duration = '30'
    dtmf = '5'
    local inspect = require 'inspect'
    require "debugger"
    local debugger = Debugger(false)
    db = Database(debug_mode, debugger)
    db:connect()

    db:load_campaign_info(campaign_id)
    print(inspect(db.campaign_info))

    db:add_dnc(dnc_id, '12388888880')

    print(db:load_content_type())

    db:save_result_mem(callrequest_id, section_id, record_file, recording_duration, dtmf)
    dtmf=io.read()
    section_id = section_id + 1
    db:save_result_mem(callrequest_id, section_id, record_file, recording_duration, dtmf)
    dtmf=io.read()
    section_id = section_id + 1
    db:save_result_mem(callrequest_id, section_id, record_file, recording_duration, dtmf)
    dtmf=io.read()
    --section_id = section_id + 1
    db:save_result_mem(callrequest_id, section_id, record_file, recording_duration, dtmf)

    db:commit_result_mem(campaign_id, survey_id)
end

if false then
    campaign_id = 42
    subscriber_id = 39
    survey_id = 5
    contact_id = 40
    callrequest_id = 30
    debug_mode = false
    section_id = 40
    record_file = '/tmp/recording-file.wav'
    recording_duration = '30'
    dtmf = '5'
    require "debugger"
    local inspect = require 'inspect'
    local debugger = Debugger(false)

    db = Database(debug_mode, debugger)
    db:connect()
    db:load_survey_section(survey_id)
    db:load_contact(subscriber_id)
    print(inspect(db.contact))
    error()
    db:load_all(campaign_id, contact_id)

    print(inspect(db.list_audio))
    print(inspect(db.list_branching))
    print(inspect(db.list_branching[11]["any"]))
    print(inspect(db.list_branching[11]["1"]))
    print(inspect(db.list_branching[11]["timeout"]))

    db:update_callrequest_cpt(callrequest_id)
    db:check_data()

    db:disconnect()
end


-- campaign_id = 42
-- contact_id = 40

-- require "debugger"
-- local debugger = Debugger(false)

-- db = Database(debug_mode, debugger)
-- db:connect()
-- db:load_all(campaign_id, contact_id)
-- --freeswitch.consoleLog('err', inspect(db.list_audio))
-- print(inspect(db.contact))
-- for k,v in pairs(db.contact) do
--     print(k)
--     print(v)
-- end

-- db:load_audiofile()
-- print(inspect(db.list_audio))
