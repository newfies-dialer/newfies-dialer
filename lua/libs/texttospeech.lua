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

-- this file contain function to :
--
-- excecute_command
-- trim
-- tts : produce texttospeec
-- acapela
--

require "md5"
require "lfs"

function skip2(_,_, ...)
    --
    return unpack(arg)
end

function simple_command(command)
    --
    local file = assert(io.popen(command, 'r'))
    local output = file:read('*all')
    file:close()
    return output
end

-- Check file exists and readable
function file_exists(path)
    local attr = lfs.attributes(path)
    if (attr ~= nil) then
        return true
    else
        return false
    end
end


-- Excecute Command function
function excecute_command(cmd, quiet)
    --
    quiet = quiet or 0   -- nul mask
    local rc,sout,serr
    -- We need some output to get the return code:
    cmd = cmd.." ; echo RC=$?"

    local f= io.popen( cmd )
    local str= f:read'*a'
    f:close()

    -- By searching at the very end of the string, we avoid clashes
    -- with whatever the command itself spit out.
    --
    local s1,s2 = skip2( string.find( str, "(.*)RC=(%d+)%s*$" ) )
    rc = tonumber(s2)

    if quiet==0 then
        sout = s1
    else
        io.write(s1)  -- os.execute() would have shown the output
    end

    -- print( cmd, rc, sout, serr )
    return rc, sout, serr
end


function trim(s)
    --trim text
    if s == nil then
        return ''
    end
    return (string.gsub(s, "^%s*(.-)%s*$", "%1"))
end

--
-- Create TTS audio using a speech processing engine
--
function tts(text, dir)
    --produce tts audio file
    engine = 'flite'
    if engine == 'cepstral' then
        voice = "-n Allison-8kHz"
        frequency = 8000
        text = trim(text)
        if string.len(text) == 0 then
            return false
        end

        hash = md5.sumhexa(voice..text)
        filename = dir..'cepstral_'..hash
        wav_file = filename..'.wav'
        txt_file = filename..'.txt'

        if not file_exists(wav_file) then
            local out = assert(io.open(txt_file, "w"))
            out:write(text)
            assert(out:close())

            swift_command = "swift -p speech/rate=150,audio/channels=1,audio/sampling-rate="..frequency.." "..voice.." -o "..wav_file.." -f "..txt_file
            excecute_command(swift_command)
            return wav_file
        end

    elseif engine == 'flite' then
        voice = "slt"
        frequency = 8000
        text = trim(text)
        if string.len(text) == 0 then
            return false
        end

        hash = md5.sumhexa(voice..text)
        filename = dir..'flite_'..hash
        wav_file = filename..'.wav'
        txt_file = filename..'.txt'

        if not file_exists(wav_file) then
            local out = assert(io.open(txt_file, "w"))
            out:write(text)
            assert(out:close())

            -- Convert file
            flite_command = 'flite -voice '..voice..' -f '..txt_file..' -o '..wav_file
            --print(flite_command)
            excecute_command(flite_command)
            return wav_file
        end

    elseif engine == 'acapela' then
        -- TODO: code for acapela

    end

    return wav_file
end


--
-- Test Code
--
if false then
    local ROOT_DIR = '/usr/share/newfies-lua/'
    local TTS_DIR = ROOT_DIR..'tts/'
    text = "Let's see if this works for us. Give a try!"
    wav_file = tts(text, TTS_DIR)
    print("wav_file => "..wav_file)
end
