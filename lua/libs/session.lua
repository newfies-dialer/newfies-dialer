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


Session = {
    -- default field values
    myvar = nil,
}

function Session:new (o)
    o = o or {}   -- create object if user does not provide one
    setmetatable(o, self)
    self.__index = self
    return o
end

-- we will simulate the freeswitch Session instances

function Session:ready()
    print("Session:ready")
    return true
end

function Session:answer()
    print("Session:answer")
    return true
end

function Session:preAnswer()
    print("Session:preAnswer")
    return true
end

function Session:hangup()
    print("Session:hangup")
    return true
end

function Session:setHangupHook(data)
    print("Session:setHangupHook -> "..data)
    return true
end

function Session:setInputCallback(data)
    print("Session:setInputCallback -> "..data)
    return true
end

function Session:execute(data)
    print("Session:execute -> "..data)
    return true
end

function Session:hangupCause()
    print("Session:hangupCause")
    return "ANSWER"
end

function Session:getVariable(varname)
    var_value = math.random(100000, 999999)
    if varname == 'campaign_id' then
        var_value = 0
    elseif varname == 'amd_status' then
        var_value = 'person'
        --var_value = 'machine'
    elseif varname == 'uuid' then
        var_value = math.random(1000, 9999)..'-'..math.random(1000, 9999)..'-'..
            math.random(1000, 9999)..'-'..math.random(1000, 9999)
    end
    print("Session:getVariable -> "..varname.." = "..var_value)
    return var_value
end

function Session:streamFile(data)
    print("Session:streamFile -> "..data)
    return true
end

function Session:set_tts_parms(engine, voice)
    print("Session:set_tts_parms -> "..engine.."-"..voice)
    return true
end

function Session:speak(data)
    print("Session:speak -> "..data)
    return true
end

function Session:playAndGetDigits(min_digits, max_digits, max_attempts, timeout, terminators, prompt_audio_files, input_error_audio_files, digit_regex, variable_name, digit_timeout, transfer_on_failure)
    print("Session:playAndGetDigits -> "..prompt_audio_files)
    local digits
    repeat
        io.write("Enter some digits and press Enter ==> ")
        io.flush()
        digits=io.read()
        print(string.len(digits))
    until string.len(digits) > 0
    return digits
end

function Session:recordFile(recording_filename, max_len_secs, silence_threshold, silence_secs)
    print("Session:recordFile -> "..recording_filename)
    return true
end

function Session:sayPhrase(data)
    print("Session:sayPhrase -> "..data)
    return true
end

return Session
