
-- this file contain function to :
--
-- excecute_command
-- trim
-- tts : produce texttospeec
-- acapela
--

require "luarocks.require"


function skip2(_,_, ...) return unpack(arg) end


function simple_command(command)
    local file = assert(io.popen(command, 'r'))
    local output = file:read('*all')
    file:close()
    return output
end

-- Excecute Command function
function excecute_command (cmd, quiet)
    --
    quiet = quiet or 0   -- nul mask
    local rc,sout,serr
    -- We need some output to get the return code:
    --
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
    if s == nil then
        return ''
    end
    return (string.gsub(s, "^%s*(.-)%s*$", "%1"))
end

--
-- TTS with Flite
--
function tts(text, dir)

    engine = 'flite'
    if engine == 'cepstral' then
        voice = "-n Allison-8kHz"
        frequency = 8000;
        text = trim(text);
        if string.len(text) == 0 then
            return false;
        end

        hash = md5.sumhexa(text)
        filename = dir..'cepstral_'..hash
        wav_file = filename..'.wav'
        txt_file = filename..'.txt'

        if not file_exists(wav_file) then
            local out = assert(io.open(txt_file, "w"));
            out:write(text);
            assert(out:close());

            swift_command = "swift -p speech/rate=150,audio/channels=1,audio/sampling-rate="..frequency.." "..voice.." -o "..wav_file.." -f "..txt_file
            excecute_command(swift_command)
        end

    elseif engine == 'flite' then
        voice = "-n Allison-8kHz"
        frequency = 8000;
        text = trim(text);
        if string.len(text) == 0 then
            return false;
        end

        hash = md5.sumhexa(text)
        filename = dir..'flite_'..hash
        wav_file = filename..'.wav'
        txt_file = filename..'.txt'

        if not file_exists(wav_file) then
            local out = assert(io.open(txt_file, "w"));
            out:write(text);
            assert(out:close());

            swift_command = "swift -p speech/rate=150,audio/channels=1,audio/sampling-rate="..frequency.." "..voice.." -o "..wav_file.." -f "..txt_file
            excecute_command(swift_command)
        end

    elseif engine == 'acapela' then
        -- TODO: code for acapela

    end

    return wav_file
end

-- Test Code

