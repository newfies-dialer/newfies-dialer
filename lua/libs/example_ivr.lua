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

--
-- Test & demonstration file for "fsm.lua"
--

package.path = package.path .. ";/usr/share/newfies-lua/?.lua";
package.path = package.path .. ";/usr/share/newfies-lua/libs/?.lua";

fs_env = false

if not fs_env then
    require "session"
    session = Session()
end

FSM = require "fsm"
local state_data = {1, 2, 3}
local call_started = false
local hangup_call = false

local dumper = require "dumper"
-- local oo = require "loop.base"
local oo = require "loop.simple"


-- module("database.DataBase", oo.class)

function dump(...)
    -- print(DataDumper(...), "\n---")
end

function sleep(n)
  os.execute("sleep " .. tonumber(n))
end

function nodefunction()
    print("------------------")
end

function startcall()
    print("==> Start Call")
    print("==> Current FSM state: " .. fsm:get())
    dump(state_data)
end


function answercall()
    print("==> ANSWER CALL")
end

function playmessage()
    print("==> Play Message")
    dump(state_data)
end

function getdigits()
    print("==> GetDigits")
    -- use state_data to know the settings from : state_data
    press_digit = session:playAndGetDigits(1, 1, 3, 4000, '#', '/tmp/audio.wav', '', '\\d+|#')
    print("==> press digit = " .. press_digit )

    dump(state_data)
end

function recordmessage()
    print("==> GetDigits")
end

function hangup()
    print("==> HANGUP")
    hangup_call = true
end

function unknow()
    print("Performing unknow event")
    print("Current FSM state: " .. fsm:get())
end

-- Define your state transitions here
local myStateTransitionTable = {
    {"start", "*", "answercall", answercall},
    {"answercall", "*", "section0", playmessage},
    {"section0", "*", "section1", getdigits},
    {"section1", "DTMF1", "section2", getdigits},
    {"section1", "DTMF2", "section2", getdigits},
    {"section1", "DTMF3", "section2", getdigits},
    {"section1", "DTMF0", "section1", getdigits},
    {"section1", "TIMEOUT", "section3", recordmessage},
    {"section2", "DTMF1", "section3", recordmessage},
    {"section2", "DTMF2", "section4", hangup},
    {"section3", "*", "section4", hangup},
    {"section4", "*", "section4", hangup},
--    {"*",      "event3", "state3", recordmessage},  -- for any state
    {"*",      "*",      "unknow", unknow}   -- exception handler
}

-- Create your finite state machine
fsm = FSM.new(myStateTransitionTable)


if not call_started then
    fsm:set("start")
    call_started = true
    fsm:fire("next")
end

-- Add session ready
while hangup_call == false do
    -- Use your finite state machine
    -- which starts by default with the first defined state
    -- Or you can set another state
    state_data = {1, 2, 3, 4}

    current_state = fsm:get()
    print("Current FSM state: " .. current_state)

    io.write("WAIT DTMF:")
    io.flush()
    digits=io.read()
    print("fire DTMF"..digits)
    fsm:fire("DTMF"..digits)

    -- Resond on "event" and last set "state"

    -- fsm:fire("event3")
    -- print("Current FSM state: " .. fsm:get())

    -- state_data = {1, 2}

end

