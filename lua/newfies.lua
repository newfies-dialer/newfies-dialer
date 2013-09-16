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

require "fsm_callflow"
require "debugger"


--Init debug and fs_env
local debug_mode = false
local fs_env = true

local OptionParser = require "pythonic.optparse" . OptionParser
local opt = OptionParser{usage="%prog [options] [gzip-file...]",
    version="newfies-dialer-lua Version 1.0", add_help_option=false}
opt.add_option{
    "-h", "--help", action="store_true", dest="help",
    help="Newfies-Dialer voice application FSM"}
opt.add_option{
    "-n", "--nofs", action="store_true", dest="nofs",
    help="Select the environement to run the script, as command line, you might want to run this with --nofs"}

local options, args = opt.parse_args()

if options.help then opt.print_help(); os.exit(1) end

-- Set if the environment is FreeSWITCH
if options.nofs then
    fs_env = false
end

local debugger = Debugger(fs_env)
if not fs_env then
    require "session"
    session = Session()
end

local callflow = FSMCall(session, debug_mode, debugger)


-- This function simply tells us what function are available in Session
--   It just prints a list of all functions.  We may be able to find functions
--   that have not yet been documented but are useful.  I did :)
-- function printSessionFunctions( session )

--    metatbl = getmetatable(session)
--    if not metatbl then return nil end

--    local f=metatbl['.fn'] -- gets the functions table
--    if not f then return nil end

--    print("\n***Session Functions***\n")
--    for k,v in pairs(f) do print(k,v) end
--    print("\n\n")
-- end
-- new_session = freeswitch.Session() -- create a blank session
-- printSessionFunctions(new_session)


function myHangupHook(s, status, arg)
    --debug("NOTICE", "myHangupHook: status -> " .. status .. "\n")
    local obCause = session:hangupCause()
    -- debug("INFO", "session:hangupCause() = " .. obCause )
    if not callflow.hangup_trigger then
        -- End call
        callflow:end_call()
    end
    error()
end

if session:ready() then

    local res = callflow:init()
    if res then
        --Answer the call
        session:answer()
        session:setHangupHook("myHangupHook")

        -- session:streamFile("/usr/share/newfies_ramdisk/tts/flite_520f6ec9707bfe353662697257068b5e.wav")

        --Start the FSM
        callflow:start_call()

        local loop = 0
        --While the session is ready and call is not ended loop
        while session:ready() and not callflow.call_ended and loop < 1000 do
            loop = loop + 1
            -- Loop on the State Machine to find the next node to proceed
            callflow:next_node()
        end
    end
    -- End call
    callflow:end_call()
end

error(_die)
