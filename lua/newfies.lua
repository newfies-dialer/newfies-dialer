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

require "luasql.postgres"
require "logging.file"
require "fsm_callflow"
require "debugger"

local debugger = Debugger('INFO', nil)

local OptionParser = require "pythonic.optparse" . OptionParser
--TODO: parse version from __init__.py
local opt = OptionParser{usage="%prog [options] [gzip-file...]",
                           version="Newfies-Dialer Version 1.0", add_help_option=false}
opt.add_option{"-h", "--help", action="store_true", dest="help",
                 help="Newfies-Dialer Voice Application FSM"}
opt.add_option{
    "-n", "--nofs", action="store_true", dest="nofs",
    help="select the environement to run the script, as command line, you might want to run this with --nofs"}

local options, args = opt.parse_args()

if options.help then opt.print_help(); os.exit(1) end
--for _, name in ipairs(args) do print(name) end

-- Set if the environment is FreeSWITCH
if options.nofs then
    fs_env = false
else
    fs_env = true
end

debug_mode = false

if not fs_env then
    require "session"
    session = Session()
end


local callflow = FSMCall(session, debug_mode, debugger)

--error(_die)


-- This function simply tells us what function are available in Session
--   It just prints a list of all functions.  We may be able to find functions
--   that have not yet been documented but are useful.  I did :)
function printSessionFunctions( session )

   metatbl = getmetatable(session)
   if not metatbl then return nil end

   local f=metatbl['.fn'] -- gets the functions table
   if not f then return nil end

   print("\n***Session Functions***\n")
   for k,v in pairs(f) do print(k,v) end
   print("\n\n")

end
-- new_session = freeswitch.Session() -- create a blank session
-- printSessionFunctions(new_session)


function myHangupHook(s, status, arg)
    debug("NOTICE", "myHangupHook: status -> " .. status .. "\n")
    local obCause = session:hangupCause()
    debug("INFO", "session:hangupCause() = " .. obCause )
    -- local xmlcdr = session:getXMLCDR()
    -- debug("info", "session:getXMLCDR() = " .. xmlcdr )
    if not callflow.hangup_trigger then
        -- End call
        callflow:end_call()
    end
    error()
end


function sleep(seconds)
    time = os.clock()
    while os.clock()-time < seconds do end
end


if session:ready() then

    session:answer()
    session:setHangupHook("myHangupHook")

    callflow:init()
    callflow:start_call()

    loop = 0
    while session:ready() and not callflow.call_ended and loop < 1000 do
        loop = loop + 1

        -- Loop on the State Machine to find the next node to proceed
        callflow:next_node()
        sleep(1)
    end

    -- Play Message
    -- session:streamFile(AUDIO_WELCOME);

    -- digits = session:playAndGetDigits (
    --       min_digits, max_digits, max_attempts, timeout, terminators,
    --       prompt_audio_files, input_error_audio_files,
    --       digit_regex, variable_name, digit_timeout,
    --       transfer_on_failure)

    -- Multi Choice
    -- press_digit = session:playAndGetDigits(1, 1, 3, 4000, '#', AUDIO_PRESSDIGIT, '', '\\d+|#')
    -- debug("info", "press digit = " .. press_digit )

    -- -- Capture Digits
    -- entered_age = session:playAndGetDigits(1, 6, 3, 4000, '#', AUDIO_ENTERAGE, '', '\\d+|#')
    -- debug("info", "entered_age = " .. entered_age )

    -- -- Recording
    -- recording_dir = '/tmp/'
    -- filename = 'myfile.wav'
    -- recording_filename = string.format('%s%s', recording_dir, filename)

    -- -- syntax is session:recordFile(file_name, max_len_secs, silence_threshold, silence_secs)
    -- max_len_secs = 30
    -- silence_threshold = 30
    -- silence_secs = 5
    -- test = session:recordFile(recording_filename, max_len_secs, silence_threshold, silence_secs)


    -- max_attempts = 1
    -- audiofile = '/usr/local/freeswitch/sounds/en/us/callie/voicemail/8000/vm-enter_new_pin.wav'

    -- while max_attempts > 0 do
    --     -- expect 1-6 digits, max_tries=3, timeout=4s, terminator=#
    --     agent_id = session:playAndGetDigits(1, 6, 3, 4000, '#', audiofile, '', '\\d+|#')

    --     -- did we actually get an agent_id?
    --     if agent_id == "" then
    --         session:sayPhrase("voicemail_goodbye")
    --         session:hangup()
    --     end

    --     max_attempts = max_attempts - 1
    -- end

    -- session:sayPhrase("welcome")

    -- End call
    callflow:end_call()

else
    -- This means the call was not answered ... Check for the reason
    local obCause = session:hangupCause()
    debug("info", "obSession:hangupCause() = " .. obCause )

    if ( obCause == "USER_BUSY" ) then              -- SIP 486
       -- For BUSY you may reschedule the call for later
    elseif ( obCause == "NO_ANSWER" ) then
       -- Call them back in an hour
    elseif ( obCause == "ORIGINATOR_CANCEL" ) then   -- SIP 487
       -- May need to check for network congestion or problems
    else
       -- Log these issues
    end
end


error(_die);
