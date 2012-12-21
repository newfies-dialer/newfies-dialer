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

local luasql = require "luasql.postgres"
local oo = require "loop.simple"
local inspect = require 'inspect'
require "constant"
require "db_config"


Database = oo.class{
	-- default field values
	-- TABLE_SECTION   = 'survey_section_template',
	-- TABLE_BRANCHING = 'survey_branching_template',
	TABLE_SECTION   = 'survey_section',
	TABLE_BRANCHING = 'survey_branching',
	env = nil,
	con = nil,
	list_section = nil,
	list_branching = nil,
	list_audio = nil,
	campaign_info = nil,
	valid_data = true,
	app_type = 'survey', -- survey or voice_app
	start_node = false,
	debugger = nil,
}

function Database:__init(debug_mode, debugger)
	-- self is the class
	return oo.rawnew(self, {
		debug_mode = debug_mode,
		debugger = debugger
	})
end

function Database:connect(debugger)
	self.env = assert(luasql.postgres())
	self.con = assert(self.env:connect(DBNAME, DBUSER, DBPASS, DBHOST, DBPORT))
end

function Database:disconnect()
	--TODO - DB connection closed before end of the call
	self.con:close()
	self.env:close()
end

function Database:load_survey_section(survey_id)
	-- id	order	type	question	script	audiofile_id	retries	timeout
	-- key_0	key_1	key_2	key_3	key_4	key_5	key_6	key_7	key_8	key_9
	-- rating_laps	validate_number	number_digits	phonenumber	completed	created_date
	-- updated_date	survey_id	invalid_audiofile_id	min_number	max_number
	sqlquery = "SELECT * FROM "..self.TABLE_SECTION.." WHERE survey_id="..survey_id.." ORDER BY "..self.TABLE_SECTION..".order"
	self.debugger:msg("INFO", "Load survey section : "..sqlquery)
	cur = self.con:execute(sqlquery)
	list = {}
	row = cur:fetch ({}, "a")
	while row do
		self.debugger:msg("DEBUG", string.format("%15d  %-15s %-15s %-15s", row.id, row.question, row.type, row.order))
		if not self.start_node then
			self.start_node = row.id
		end
		list[tonumber(row.id)] = row
		row = cur:fetch ({}, "a")
	end
	cur:close()
	self.list_section = list
	if not self.start_node then
		self.debugger:msg("INFO", "Error Loading Survey Section")
	end
end

function Database:load_survey_branching(survey_id)
	-- id	keys section_id	goto_id
	sqlquery = "SELECT "..self.TABLE_BRANCHING..".id, keys, section_id, goto_id "..
		"FROM "..self.TABLE_BRANCHING.." LEFT JOIN "..self.TABLE_SECTION..
		" ON "..self.TABLE_SECTION..".id="..self.TABLE_BRANCHING..".section_id "..
		"WHERE survey_id="..survey_id
	self.debugger:msg("INFO", "Load survey branching : "..sqlquery)
	cur = self.con:execute(sqlquery)

	-- LOOP THROUGH THE CURSOR
	self.debugger:msg("DEBUG", string.format("%15s  %-15s %-15s %-15s", "#", "KEYS", "SECTION_ID", "GOTO_ID"))
	list = {}
	row = cur:fetch ({}, "a")
	while row do
		self.debugger:msg("DEBUG", string.format("%15d  %-15s %-15s %-15s", row.id, tostring(row.keys), tostring(row.section_id), tostring(row.goto_id)))
		if not list[tonumber(row.section_id)] then
			list[tonumber(row.section_id)] = {}
		end
		list[tonumber(row.section_id)][tostring(row.keys)] = row
		row = cur:fetch ({}, "a")
	end
	cur:close()
	self.list_branching = list
	--print(inspect(self.list_branching))
end

function Database:load_audiofile()
	-- id	name	audio_file	user_id
	--TODO: Add user_id
	sqlquery = "SELECT * FROM audio_file"
	self.debugger:msg("INFO", "Load audiofile branching : "..sqlquery)
	cur = self.con:execute(sqlquery)

	-- LOOP THROUGH THE CURSOR
	list = {}
	row = cur:fetch ({}, "a")
	while row do
		list[tonumber(row.id)] = row
		row = cur:fetch ({}, "a")
	end
	cur:close()
	self.list_audio = list
	--print(inspect(self.list_audio))
end

function Database:get_list(sqlquery)
	self.debugger:msg("INFO", "Load SQL : "..sqlquery)
	cur = assert(self.con:execute(sqlquery))
	list = {}
	row = cur:fetch ({}, "a")
	while row do
		list[tonumber(row.id)] = row
		row = cur:fetch ({}, "a")
	end
	cur:close()
	return list
end

function Database:get_object(sqlquery)
	self.debugger:msg("INFO", "Load SQL : "..sqlquery)
	cur = assert(self.con:execute(sqlquery))
	row = cur:fetch ({}, "a")
	cur:close()
	return row
end

function Database:load_campaign_info(campaign_id)
	sqlquery = "SELECT * FROM dialer_campaign WHERE id="..campaign_id
	self.debugger:msg("INFO", "Load campaign info : "..sqlquery)
	self.campaign_info = self:get_object(sqlquery)
	-- check campaign info
end

function Database:load_contact(subscriber_id)
	sqlquery = "SELECT * FROM dialer_subscriber "..
		"LEFT JOIN dialer_contact ON dialer_contact.id=contact_id "..
		"WHERE dialer_subscriber.id="..subscriber_id
	self.debugger:msg("INFO", "Load contact data : "..sqlquery)
	self.contact = self:get_object(sqlquery)
	-- check campaign info
end

function Database:update_subscriber(subscriber_id, status)
	sqlquery = "UPDATE dialer_subscriber SET status='"..status.."' WHERE id="..subscriber_id
	self.debugger:msg("INFO", "Update Subscriber : "..sqlquery)
	res = self.con:execute(sqlquery)
	self:update_campaign_completed()
end

function Database:update_campaign_completed()
	sqlquery = "UPDATE dialer_campaign SET completed = completed + 1 WHERE id="..self.campaign_info.id
	self.debugger:msg("INFO", "Update Campaign : "..sqlquery)
	res = self.con:execute(sqlquery)
end

function Database:update_callrequest_cpt(callrequest_id)
	sqlquery = "UPDATE dialer_callrequest SET completed = 't' WHERE id="..callrequest_id
	self.debugger:msg("INFO", "Update CallRequest : "..sqlquery)
	res = self.con:execute(sqlquery)
end

function Database:load_all(campaign_id, subscriber_id)
	self:load_contact(subscriber_id)
	if not self.contact then
		self.debugger:msg("ERROR", "Error: No Contact")
		return false
	end
	--print(inspect(self.contact))

	self:load_campaign_info(campaign_id)
	if not self.campaign_info then
		self.debugger:msg("ERROR", "Error: No Campaign")
		return false
	end
	--print(inspect(self.campaign_info))

	--TODO: Fix content_type_id = 34 should be flexible
	if self.campaign_info.content_type_id == 34 then
		self.app_type = 'survey'
	else
		self.app_type = 'voice_app'
	end
	survey_id = self.campaign_info.object_id
	--TODO: Support Voice App
	self:load_survey_section(survey_id)
	self:load_survey_branching(survey_id)
	self:load_audiofile()
	return true
end

function Database:check_data()
	--Check if we retrieve Campaign Info
	if not self.campaign_info then
		self.valid_data = false
	end
	--Check if we retrieve List Section
	if not self.list_section then
		self.valid_data = false
	end
	--Check we got a start_node
	if not self.start_node then
		self.valid_data = false
	end
	return self.valid_data
end

-- TODO: Finish this later
function Database:placeholder_replace(text)
	--use contact self.contact

    -- Replace place holders by tag value.
    -- This function will replace all the following tags :
    --     {last_name}
    --     {first_name}
    --     {email}
    --     {country}
    --     {city}
    --     {phone_number}
    -- as well as, get additional_vars, and replace json tags

    --TODO Finish implementation of placeholder_replace
    --{PYTHON CODE}
    --text = str(text).lower()
    -- context = {
    --     'last_name': contact.last_name,
    --     'first_name': contact.first_name,
    --     'email': contact.email,
    --     'country': contact.country,
    --     'city': contact.city,
    --     'phone_number': contact.contact,
    -- }
    -- if contact.additional_vars:
    --     for index in contact.additional_vars:
    --         context[index] = contact.additional_vars[index]

    -- for ind in context:
    --     text = text.replace('{' + ind + '}', str(context[ind]))
    return text
end

function Database:save_result_recording(callrequest_id, section_id, record_file, recording_duration)
	sqlquery = "INSERT INTO survey_result (callrequest_id, section_id, record_file, recording_duration, response, created_date) "..
		"VALUES ("..callrequest_id..", "..section_id..", '"..record_file.."', '"..recording_duration.."', '', NOW())"
	self.debugger:msg("INFO", "Save Result Recording:"..sqlquery)
	res = self.con:execute(sqlquery)
	if not res then
		return false
	else
		return true
	end
end

function Database:update_result_recording(callrequest_id, section_id, record_file, recording_duration)
	sqlquery = "UPDATE survey_result SET record_file='"..record_file.."', recording_duration='"..recording_duration.."'"..
		" WHERE callrequest_id="..callrequest_id.." AND section_id="..section_id
	self.debugger:msg("INFO", "Update Result Recording:"..sqlquery)
	res = self.con:execute(sqlquery)
	if not res then
		return false
	else
		return true
	end
end

function Database:save_result_dtmf(callrequest_id, section_id, dtmf)
	sqlquery = "INSERT INTO survey_result (callrequest_id, section_id, response, record_file, created_date) "..
		"VALUES ("..callrequest_id..", "..section_id..", '"..dtmf.."', '', NOW())"
	self.debugger:msg("INFO", "Save Result DTMF:"..sqlquery)
	res = self.con:execute(sqlquery)
	if not res then
		return false
	else
		return true
	end
end

function Database:update_result_dtmf(callrequest_id, section_id, dtmf)
	sqlquery = "UPDATE survey_result SET response='"..dtmf.."'"..
		" WHERE callrequest_id="..callrequest_id.." AND section_id="..section_id
	self.debugger:msg("INFO", "Update Result DTMF:"..sqlquery)
	res = self.con:execute(sqlquery)
	if not res then
		return false
	else
		return true
	end
end

function Database:save_result_aggregate(campaign_id, survey_id, section_id, response)
	sqlquery = "INSERT INTO survey_resultaggregate (campaign_id, survey_id, section_id, response, count, created_date) "..
		"VALUES ("..campaign_id..", "..survey_id..", "..section_id..", '"..response.."', 1, NOW())"
	self.debugger:msg("INFO", "Save Result Aggregate:"..sqlquery)
	res = self.con:execute(sqlquery)
	if not res then
		return false
	else
		return true
	end
end

function Database:update_result_aggregate(campaign_id, survey_id, section_id, response)
	sqlquery = "UPDATE survey_resultaggregate SET count = count + 1"..
		" WHERE campaign_id="..campaign_id.." AND survey_id="..survey_id.." AND section_id="..section_id.." AND response='"..section_id.."'"
	self.debugger:msg("INFO", "Update Result Aggregate:"..sqlquery)
	res = self.con:execute(sqlquery)
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
    -- Insert ResultAggregate
    if self:save_result_aggregate(campaign_id, survey_id, section_id, response) then
		-- no errors in save_result_aggregate
		return true
	else
		-- threw an error
		res = pcall(self:update_result_aggregate(campaign_id, survey_id, section_id, response))
		if not res then
			self.debugger:msg("ERROR", "Error update_result_aggregate")
		end
		return true
	end
end

function Database:save_section_result(campaign_id, survey_id, callrequest_id, current_node, DTMF, record_file, recording_dur)
	-- DTMF can be false
	if not DTMF then
		DTMF = ''
	end
    -- save the result of a section
    if current_node.type == RECORD_MSG then
		--Save aggregated result
        self:set_aggregate_result(campaign_id, survey_id, current_node.id, DTMF, recording_dur)

		if self:save_result_recording(callrequest_id, current_node.id, record_file, recording_dur) then
			-- no errors in save_result
			return true
		else
			res = self:update_result_recording(callrequest_id, current_node.id, record_file, recording_dur)
			if not res then
				self.debugger:msg("ERROR", "Error update_result_recording")
			end
			return true
		end

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

		--Save aggregated result
        self:set_aggregate_result(campaign_id, survey_id, current_node.id, DTMF, recording_dur)

		if self:save_result_dtmf(callrequest_id, current_node.id, DTMF) then
			-- no errors in save_result

			return true
		else
			res = self:update_result_dtmf(callrequest_id, current_node.id, DTMF)
			self.debugger:msg("ERROR", tostring(res))
			if not res then
				self.debugger:msg("ERROR", "Error update_result_dtmf")
			end
			return true
		end
	end
end

--
-- Test Code
--
if false then
	campaign_id = 23
    subscriber_id = 15
    callrequest_id = 30
    debug_mode = false
    section_id = 40
    record_file = '/tmp/recording-file.wav'
    recording_dur = '30'
    dtmf = '5'

    db = Database(debug_mode)
    db:connect()
    db:load_all(campaign_id, subscriber_id)

	print(inspect(db.list_audio))
	print(inspect(db.list_branching))
	print(inspect(db.list_branching[11]["any"]))
	print(inspect(db.list_branching[11]["1"]))
	print(inspect(db.list_branching[11]["timeout"]))

    db:update_callrequest_cpt(callrequest_id)
    db:check_data()
    if db:save_result_recording(callrequest_id, section_id, record_file, recording_dur) then
    	print("OK save_result_recording")
    else
    	print("ERROR save_result_recording")
    	res = db:update_result_recording(callrequest_id, section_id, record_file, recording_dur)
    	print(res)
    end

    if db:save_result_dtmf(callrequest_id, section_id, dtmf) then
		print("OK save_result_dtmf")
    else
    	print("ERROR save_result_dtmf")
    	res = db:update_result_dtmf(callrequest_id, section_id, dtmf)
    	print(res)
    end
    db:disconnect()
end
