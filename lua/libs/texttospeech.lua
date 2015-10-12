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

-- this file contain function to :
--
-- excecute_command
-- trim
-- tts : produce texttospeec
-- acapela
--

require "constant"


-- loadding acapela_config depend of file_exists which then load lfs
-- TODO: Find a better way to load conf

-- Check file exists and readable
function file_exists(path)
    local lfs = require "lfs"
    local attr = lfs.attributes(path)
    if (attr ~= nil) then
        return true
    else
        return false
    end
end

--load local config first
if file_exists(ROOT_DIR..'libs/acapela_config.lua') then
    require "acapela_config"
end
if ACCOUNT_LOGIN == nil then
    --if local config failed, import settings
    require "settings"
end

--Set a default TTS engine
if TTS_ENGINE == nil then
    TTS_ENGINE = 'flite'
end


-- function skip2(_,_, ...)
--     return unpack(arg)
-- end

function simple_command(command)
    local file = assert(io.popen(command, 'r'))
    local output = file:read('*all')
    file:close()
    return output
end

-- Excecute Command function
function excecute_command(cmd, quiet)
    local rc, sout, serr
    -- We need some output to get the return code:
    cmd = cmd.." ; echo RC=$?"

    local f= io.popen( cmd )
    local str= f:read'*a'
    f:close()

    -- By searching at the very end of the string, we avoid clashes
    -- with whatever the command itself spit out.
    --
    -- local s1,s2 = skip2( string.find( str, "(.*)RC=(%d+)%s*$" ) )
    -- rc = tonumber(s2)

    -- if quiet==0 then
    --     sout = s1
    -- else
    --     print("io.write")
    --     io.write(s1)  -- os.execute() would have shown the output
    -- end

    -- print( cmd, rc, sout, serr )
    return rc, sout, serr
end

--
-- Trim text
--
function trim(text)
    if text == nil then
        return ''
    end
    return (string.gsub(text, "^%s*(.-)%s*$", "%1"))
end


--
-- Return the audio lenght in float
--
function audio_lenght(audio_file)
    if not file_exists(audio_file) then
        return '0'
    else
        len_command = "soxi -D "..audio_file
        res = simple_command(len_command)
        if res then
            return trim(res)
        else
            return '0'
        end
    end
end

--
-- Create TTS audio using a speech processing engine
--
-- TODO: name tts to synthesize
--
function tts(text, tts_dir)

    local md5 = require "md5"

    if TTS_ENGINE == 'cepstral' then
        --Cepstral
        voice = "-n Allison-8kHz"
        frequency = 8000
        text = trim(text)
        if string.len(text) == 0 then
            return false
        end

        hash = md5.sumhexa(voice..text)
        filename = tts_dir..'cepstral_'..hash
        output_file = filename..'.wav'
        txt_file = filename..'.txt'

        if not file_exists(output_file) then
            local out = assert(io.open(txt_file, "w"))
            out:write(text)
            assert(out:close())

            swift_command = "swift -p speech/rate=150,audio/channels=1,audio/sampling-rate="..frequency.." "..voice.." -o "..output_file.." -f "..txt_file
            excecute_command(swift_command)
            return output_file
        end

    elseif TTS_ENGINE == 'flite' then
        --Flite
        voice = "awb"
        frequency = 8000
        text = trim(text)
        if string.len(text) == 0 then
            return false
        end

        hash = md5.sumhexa(voice..text)
        filename = tts_dir..'flite_'..hash
        output_file = filename..'.wav'
        txt_file = filename..'.txt'

        if not file_exists(output_file) then
            local out = assert(io.open(txt_file, "w"))
            out:write(text)
            assert(out:close())

            -- Convert file
            flite_command = 'flite --setf duration_stretch=1.5 -voice '..voice..' -f '..txt_file..' -o '..output_file
            --print(flite_command)
            excecute_command(flite_command)
            return output_file
        end

    elseif TTS_ENGINE == 'acapela' then
        --Acapela
        Acapela = require "acapela"
        tts_acapela = Acapela:new{
            ACCOUNT_LOGIN=ACCOUNT_LOGIN,
            APPLICATION_LOGIN=APPLICATION_LOGIN,
            APPLICATION_PASSWORD=APPLICATION_PASSWORD,
            SERVICE_URL=SERVICE_URL,
            QUALITY=QUALITY,
            DIRECTORY=tts_dir}
        tts_acapela:set_cache(true)
        tts_acapela:prepare(text, ACAPELA_LANG, ACAPELA_GENDER, ACAPELA_INTONATION)
        output_file = tts_acapela:run()
    end

    elseif TTS_ENGINE == 'mstranslator' then
        -- Microsoft Translator
        MSTranslator = require "mstranslator"
        tts_mstranslator = MSTranslator:new{
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            DIRECTORY=tts_dir}
        tts_mstranslator:set_cache(true)
        tts_mstranslator:prepare(text, MSTRANSLATOR_LANG)
        output_file = tts_mstranslator:run()
    end
    return output_file
end
