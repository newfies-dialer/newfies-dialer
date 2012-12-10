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

local dumper = require "dumper"
local luasql = require "luasql.postgres"
-- local oo = require "loop.base"
local oo = require "loop.simple"


-- module("database.DataBase", oo.class)

function dump(...)
 	print(DataDumper(...), "\n---")
end

Database = oo.class{
	-- default field values
	TABLE_SECTION   = 'survey_section_template',
	TABLE_BRANCHING = 'survey_branching_template',
	-- TABLE_SECTION   = 'survey_section',
	-- TABLE_BRANCHING = 'survey_branching',
	env = nil,
	con = nil,
	list_section = nil,
	list_branch = nil,
	list_audio = nil
}

function Database:__init(debug_mode)
	-- self is the class
	return oo.rawnew(self, {
		debug_mode = debug_mode
	})
end

function Database:connect()
	self.env = assert (luasql.postgres())
	self.con = assert (self.env:connect('newfies2', 'newfiesuser', 'password', "127.0.0.1", 5432))
end

function Database:disconnect()
	self.con:close()
	self.env:close()
end

function Database:load_survey_section(survey_id)
	print("Load survey section")
	-- id	order	type	question	script	audiofile_id	retries	timeout
	-- key_0	key_1	key_2	key_3	key_4	key_5	key_6	key_7	key_8	key_9
	-- rating_laps	validate_number	number_digits	phonenumber	completed	created_date
	-- updated_date	survey_id	invalid_audiofile_id	min_number	max_number
	QUERY = "SELECT * FROM "..self.TABLE_SECTION.." WHERE survey_id="..survey_id.." ORDER BY id"
	cur = assert (self.con:execute(QUERY))

	-- LOOP THROUGH THE CURSOR
	if debug_mode then
		print()
		print(string.format("%15s  %-15s %-15s %-15s", "#", "QUESTION", "TYPE", "ORDER"))
		print(string.format("%15s  %-15s %-15s %-15s", "-", "--------", "----", "-----"))
	end
	list = {}
	row = cur:fetch ({}, "a")
	while row do
		if debug_mode then
			print(string.format("%15d  %-15s %-15s %-15s", row.id, row.question, row.type, row.order))
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
	cur = assert (self.con:execute(QUERY))

	-- LOOP THROUGH THE CURSOR
	if debug_mode then
		print()
		print(string.format("%15s  %-15s %-15s %-15s", "#", "KEYS", "SECTION_ID", "GOTO_ID"))
		print(string.format("%15s  %-15s %-15s %-15s", "-", "----", "----------", "-------"))
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
	self.list_branch = list
end


function Database:load_audiofile()
	print("Load audiofile branching")
	-- id	name	audio_file	user_id
	QUERY = "SELECT * FROM audio_file"
	cur = assert (self.con:execute(QUERY))

	-- LOOP THROUGH THE CURSOR
	list = {}
	row = cur:fetch ({}, "a")
	while row do
		list[tonumber(row.id)] = row
		row = cur:fetch ({}, "a")
	end
	cur:close()
	self.list_audio = list
end

function Database:load_all(survey_id)
	self:load_survey_section(survey_id)
	self:load_survey_branching(survey_id)
	self:load_audiofile()
end

-- -- RECREATE PEOPLE TABLE
-- res = assert (con:execute[[
-- 	CREATE TABLE people(
-- 		id integer,
-- 		fname text,
-- 		lname text,
-- 		job text
-- 	)
-- ]])



-- TEST
-- Define a shortcut function for testing
-- function dump(...)
--   print(DataDumper(...), "\n---")
-- end

-- dump(Database.list_audio)
-- dump(Database.list_branch)
-- dump(Database.list_branch[11]["any"])
-- dump(Database.list_branch[11]["1"])
-- dump(Database.list_branch[11]["timeout"])
