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

local database = require "database"

--
-- Test Code
--
local inspect = require 'inspect'
local Debugger = require "fsdebugger"
local debugger = Debugger(false)
db = Database:new{
    debug_mode=debug_mode,
    debugger=debugger
}
db:connect()

-- campaign_id = 152
-- db:load_campaign_info(campaign_id)
-- print(inspect(db.campaign_info))
sms_text = 'hello there'
survey_id = 121
phonenumber = '845648998'

-- db:send_sms(sms_text, survey_id, phonenumber)

contact_id = 19143
db:load_contact(contact_id)
print(inspect(db.contact))
