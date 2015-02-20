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
    local Debugger = require "fsdebugger"
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

    db:commit_result_mem(survey_id)
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
    local Debugger = require "fsdebugger"
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


-- local Debugger = require "fsdebugger"
-- local debugger = Debugger(false)

-- db = Database(debug_mode, debugger)
-- db:connect()
-- list_campaign = db:test_get_campaign()
-- print(inspect(list_campaign))


-- campaign_id = 42
-- contact_id = 40

-- local Debugger = require "fsdebugger"
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
