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

local luasql = require "luasql.postgres"
-- local oo = require "loop.base"
local oo = require "loop.simple"
local inspect = require 'inspect'
require "constant"

-- module("database.DataBase", oo.class)


Database = oo.class{
	-- default field values
	TABLE_SECTION   = 'survey_section_template',
	TABLE_BRANCHING = 'survey_branching_template',
	-- TABLE_SECTION   = 'survey_section',
	-- TABLE_BRANCHING = 'survey_branching',
	env = nil,
	con = nil,
	list_section = nil,
	list_branching = nil,
	list_audio = nil,
	campaign_info = nil,
	valid_data = true,
	app_type = 'survey', -- survey or voice_app
	start_node = false,
}

function Database:__init(debug_mode)
	-- self is the class
	return oo.rawnew(self, {
		debug_mode = debug_mode
	})
end

function Database:connect()
	self.env = assert(luasql.postgres())
	self.con = assert(self.env:connect('newfies2', 'newfiesuser', 'password', "127.0.0.1", 5432))
end

function Database:disconnect()
	--TODO - DB connection closed before end of the call
	self.con:close()
	self.env:close()
end

function Database:load_survey_section(survey_id)
	print("Load survey section")
	-- id	order	type	question	script	audiofile_id	retries	timeout
	-- key_0	key_1	key_2	key_3	key_4	key_5	key_6	key_7	key_8	key_9
	-- rating_laps	validate_number	number_digits	phonenumber	completed	created_date
	-- updated_date	survey_id	invalid_audiofile_id	min_number	max_number
	QUERY = "SELECT * FROM "..self.TABLE_SECTION.." WHERE survey_id="..survey_id.." ORDER BY "..self.TABLE_SECTION..".order"
	cur = self.con:execute(QUERY)

	-- LOOP THROUGH THE CURSOR
	if debug_mode then
		print(string.format("%15s  %-15s %-15s %-15s", "#", "QUESTION", "TYPE", "ORDER"))
	end
	list = {}
	row = cur:fetch ({}, "a")
	while row do
		if debug_mode then
			print(string.format("%15d  %-15s %-15s %-15s", row.id, row.question, row.type, row.order))
		end
		if not self.start_node then
			self.start_node = row.id
		end
		list[tonumber(row.id)] = row
		row = cur:fetch ({}, "a")
	end
	cur:close()
	self.list_section = list
end

function Database:load_survey_branching(survey_id)
	print("Load survey branching")
	-- id	keys section_id	goto_id
	QUERY = "SELECT "..self.TABLE_BRANCHING..".id, keys, section_id, goto_id "..
		"FROM "..self.TABLE_BRANCHING.." LEFT JOIN "..self.TABLE_SECTION..
		" ON "..self.TABLE_SECTION..".id="..self.TABLE_BRANCHING..".section_id "..
		"WHERE survey_id="..survey_id
	cur = self.con:execute(QUERY)

	-- LOOP THROUGH THE CURSOR
	if debug_mode then
		print(string.format("%15s  %-15s %-15s %-15s", "#", "KEYS", "SECTION_ID", "GOTO_ID"))
	end
	list = {}
	row = cur:fetch ({}, "a")
	while row do
		if debug_mode then
			print(string.format("%15d  %-15s %-15s %-15s", row.id, tostring(row.keys), tostring(row.section_id), tostring(row.goto_id)))
		end
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
	print("Load audiofile branching")
	-- id	name	audio_file	user_id
	QUERY = "SELECT * FROM audio_file"
	cur = self.con:execute(QUERY)

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

function Database:get_list(query)
	print("Load sql")
	cur = assert(self.con:execute(query))
	list = {}
	row = cur:fetch ({}, "a")
	while row do
		list[tonumber(row.id)] = row
		row = cur:fetch ({}, "a")
	end
	cur:close()
	return list
end

function Database:get_object(query)
	cur = assert(self.con:execute(query))
	row = cur:fetch ({}, "a")
	cur:close()
	return row
end

function Database:load_campaign_info(campaign_id)
	print("Load campaign info")
	QUERY = "SELECT * FROM dialer_campaign WHERE id="..campaign_id
	self.campaign_info = self:get_object(QUERY)
	-- check campaign info
end

function Database:load_contact(subscriber_id)
	print("Load contact data")
	QUERY = "SELECT * FROM dialer_subscriber "..
		"LEFT JOIN dialer_contact ON dialer_contact.id=contact_id "..
		"WHERE dialer_subscriber.id="..subscriber_id
	print(QUERY)
	self.contact = self:get_object(QUERY)
	-- check campaign info
end

function Database:update_subscriber(subscriber_id, status)
	print("Update Subscriber")
	QUERY = "UPDATE dialer_subscriber SET status='"..status.."' WHERE id="..subscriber_id
	res = self.con:execute(QUERY)
	print(res)
	self:update_campaign_completed()
end

function Database:update_campaign_completed()
	print("Update Campaign")
	QUERY = "UPDATE dialer_campaign SET completed = completed + 1 WHERE id="..campaign_info.id
	res = self.con:execute(QUERY)
end

function Database:update_callrequest_cpt(callrequest_id)
	print("Update CallRequest")
	QUERY = "UPDATE dialer_callrequest SET completed = 't' WHERE id="..callrequest_id
	res = self.con:execute(QUERY)
end

function Database:load_all(campaign_id, subscriber_id)
	self:load_contact(subscriber_id)
	if not self.contact then
		return false
	end
	print(inspect(self.contact))

	self:load_campaign_info(campaign_id)
	if not self.campaign_info then
		return false
	end
	--print(inspect(self.campaign_info))

	--TODO: 34 should be flexible
	if self.campaign_info.content_type_id == 34 then
		self.app_type = 'survey'
	else
		self.app_type = 'voice_app'
	end
	survey_id = self.campaign_info.object_id
	print(">> survey_id = "..survey_id)
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
end

-- TODO: Finish this later
function Database:placeholder_replace(text)
	--use contact
	print(self.contact)

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
	print("Save Result")
	QUERY = "INSERT INTO survey_result (callrequest_id, section_id, record_file, recording_duration, response, created_date) "..
		"VALUES ("..callrequest_id..", "..section_id..", '"..record_file.."', '"..recording_duration.."', '', NOW())"
	print(QUERY)
	res = self.con:execute(QUERY)
	if not res then
		return false
	else
		return true
	end
end

function Database:update_result_recording(callrequest_id, section_id, record_file, recording_duration)
	print("Save Result")
	QUERY = "UPDATE survey_result SET record_file='"..record_file.."', recording_duration='"..recording_duration.."'"..
		" WHERE callrequest_id="..callrequest_id.." AND section_id="..section_id
	res = self.con:execute(QUERY)
	if not res then
		return false
	else
		return true
	end
end

function Database:save_result_dtmf(callrequest_id, section_id, dtmf)
	QUERY = "INSERT INTO survey_result (callrequest_id, section_id, response) "..
		"VALUES ("..callrequest_id..", "..section_id..", "..dtmf..")"
	print("Save Result : "..QUERY)
	res = self.con:execute(QUERY)
	if not res then
		return false
	else
		return true
	end
end

function Database:update_result_dtmf(callrequest_id, section_id, dtmf)
	print("Save Result")
	QUERY = "UPDATE survey_result SET response="..dtmf..
		" WHERE callrequest_id="..callrequest_id.." AND section_id="..section_id
	res = self.con:execute(QUERY)
	if not res then
		return false
	else
		return true
	end
end

function Database:save_section_result(callrequest_id, current_node, DTMF, record_file)
    -- save the result of a section

    if current_node.type == RECORD_MSG then
        --RECORD_MSG
        --TODO: Use sox to get file duration
        recording_duration = 0

		--TODO: Save aggregated result
        --set_aggregate_result(callrequest_id, current_node, DTMF, recording_duration)

		if self:save_result_recording(callrequest_id, current_node.id, record_file, recording_duration) then
			-- no errors in save_result
			return true
		else
			-- threw an error
			res = pcall(self:update_result_recording(callrequest_id, current_node.id, record_file, recording_duration))
			if not res then
				print "Error update_result_recording"
			end
			return true
		end

    elseif DTMF and string.len(DTMF) > 0 and
    	(current_node.type == MULTI_CHOICE or
    	 current_node.type == RATING_SECTION or
         current_node.type == CAPTURE_DIGITS) then

        if current_node.type == MULTI_CHOICE then
            -- Get value for the DTMF from current_node.key_X
            if DTMF == '0' and current_node.key_0 then
                DTMF = current_node.key_0
            elseif DTMF == '1' and current_node.key_1 then
                DTMF = current_node.key_1
            elseif DTMF == '2' and current_node.key_2 then
                DTMF = current_node.key_2
            elseif DTMF == '3' and current_node.key_3 then
                DTMF = current_node.key_3
            elseif DTMF == '4' and current_node.key_4 then
                DTMF = current_node.key_4
            elseif DTMF == '5' and current_node.key_5 then
                DTMF = current_node.key_5
            elseif DTMF == '6' and current_node.key_6 then
                DTMF = current_node.key_6
            elseif DTMF == '7' and current_node.key_7 then
                DTMF = current_node.key_7
            elseif DTMF == '8' and current_node.key_8 then
                DTMF = current_node.key_8
            elseif DTMF == '9' and current_node.key_8 then
                DTMF = current_node.key_9
            end
        end

		--Save aggregated result
        --set_aggregate_result(callrequest_id, current_node, DTMF, False)
		if pcall(self:save_result_dtmf(callrequest_id, current_node.id, DTMF)) then
			-- no errors in save_result
			return true
		else
			-- threw an error
			res = pcall(self:update_result_dtmf(callrequest_id, current_node.id, DTMF))
			if not res then
				print "Error update_result_dtmf"
			end
			return true
		end
	end
end


-- TEST
-- Define a shortcut function for testing

-- print(inspect(Database.list_audio))
-- print(inspect(Database.list_branching))
-- print(inspect(Database.list_branching[11]["any"]))
-- print(inspect(Database.list_branching[11]["1"]))
-- print(inspect(Database.list_branching[11]["timeout"]))

--
-- Test Code
--
if true then
	campaign_id = 23
    subscriber_id = 15
    callrequest_id = 30
    debug_mode = false
    section_id = 40
    record_file = '/tmp/recording-file.wav'
    recording_duration = '30'
    dtmf = '5'

    db = Database(debug_mode)
    db:connect()
    db:load_all(campaign_id, subscriber_id)
    db:update_callrequest_cpt(callrequest_id)
    db:check_data()
    if db:save_result_recording(callrequest_id, section_id, record_file, recording_duration) then
    	print("OK save_result_recording")
    else
    	print("ERROR save_result_recording")
    end
    db:update_result_recording(callrequest_id, section_id, record_file, recording_duration)
    db:save_result_dtmf(callrequest_id, section_id, dtmf)
    db:update_result_dtmf(callrequest_id, section_id, dtmf)
    db:disconnect()
end