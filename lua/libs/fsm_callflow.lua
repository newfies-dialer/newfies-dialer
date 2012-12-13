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



FSMCall = oo.class{
    -- default field values
    extension_list = nil,
    caller_id_name = nil,
    caller_id_number = nil,
    destination_number = nil,
    uuid = nil,
    survey_id = nil,
    call_duration = 0,
    logger = nil,
    hangup_trigger = false,
    current_section = false,
    db = nil,
}

function FSMCall:__init(session, debug_mode, logger)
    -- self is the class
    return oo.rawnew(self, {
        session = session,
        debug_mode = debug_mode,
        logger = logger,
        db = Database(debug_mode)
    })
end


function FSMCall:init()
    print("FSMCall:init")
    self.extension_list = self.session:getVariable("extension_list")
    self.caller_id_name = self.session:getVariable("caller_id_name")
    self.caller_id_number = self.session:getVariable("caller_id_number")
    self.destination_number = self.session:getVariable("destination_number")
    self.uuid = self.session:getVariable("uuid")
    self.campaign_id = self.session:getVariable("campaign_id")
    self.campaign_id = 23

    self.db:connect()
    if not self.db:load_all(self.campaign_id) then
        self.logger:error("Error loading data")
        print("Error loading data")
        self:hangupcall()
        return false
    end
    self.db:check_data()
    self.db:disconnect()
    print(self.db.start_node)
    print(inspect(self.db.list_section[tonumber(self.db.start_node)]))


    if not self.db.valid_data then
        self.logger:error("Error invalid data")
        self:hangupcall()
        return false
    end
    --print(inspect(self.db.list_audio))
end

function FSMCall:end_call()
    print("FSMCall:end_call")
    self.logger:info("FSMCall:end_call")
    -- NOTE: Don't use this call time for Billing
    -- Use FS CDRs
    self.call_duration = os.time() - self.call_start
    print("Estimated Call Duration : "..self.call_duration)
    self.logger:info("Estimated Call Duration : "..self.call_duration)
    self:hangupcall()
end

function FSMCall:hangupcall()
    -- This will interrupt lua script
    self.logger:info("FSMCall:hangupcall")
    self.hangup_trigger = true
    self.session:hangup()
end

function FSMCall:start_call()
    print("FSMCall:start_call")
    self.logger:info("FSMCall:start_call...")
    self.call_start = os.time()
    self:next_node()
end


function FSMCall:next_node()
    print("FSMCall:next_node")
    self.logger:info("FSMCall:next_node...")
    if not self.current_section then
        print "OK"
    end
end
