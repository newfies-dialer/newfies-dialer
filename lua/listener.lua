

-- List of Channels States
-- http://wiki.freeswitch.org/wiki/Event_list#CHANNEL_STATE

local luasql = require "luasql.postgres"

-- Database setup
DATABASE = "newfies2"
USERNAME = "newfiesuser"
PASSWORD = "password"
DBHOST   = "localhost"
TABLENAME = "scheduler"

-- LOGGING
LOGLEVEL = "info"

-- PROGNAME
PROGNAME = "dialer.lua"

function logger(message)
    freeswitch.console_log(LOGLEVEL,"["..PROGNAME.."] "..message.."\n")
end

function sleep(seconds)
    time = os.clock()
    while os.clock()-time < seconds do end
end

function trim(s)
    --trim text
    if s == nil then
        return ''
    end
    return (string.gsub(s, "^%s*(.-)%s*$", "%1"))
end

if argv[1] then
    i=1
    while argv[i] do
        if argv[i] == "stop" then
            --Send Stop message
            local event = freeswitch.Event("custom", "lua::stop_event")
            event:addHeader("Action", "stop")
            event:fire()
            logger("Sent stop message to lua script")
            return
        end
        i=i+1
    end
    return
end

--Main function starts here
logger("Starting")

-- ensure DB works, create table if it doesnt exist
env = assert (luasql.postgres())
dbcon = assert (env:connect(DATABASE,USERNAME,PASSWORD,DBHOST, 5432))
blah = assert(dbcon:execute([["CREATE TABLE if not exists call_event (
        id serial NOT NULL PRIMARY KEY,
        event_name varchar(200) NOT NULL,
        body varchar(200) NOT NULL,
        job_uuid varchar(200),
        core_uuid varchar(200) NOT NULL,
        status integer,
        created_date timestamp with time zone NOT NULL,
        UNIQUE ("event_name", "core_uuid")
        )"]]))
dbcon:close()
env:close()



local event_name
local event_subclass


con = freeswitch.EventConsumer("ALL")
-- con = freeswitch.EventConsumer("CHANNEL_CALLSTATE")
-- con = freeswitch.EventConsumer("CHANNEL_CREATE")
-- con = freeswitch.EventConsumer("CHANNEL_PROGRESS")
-- con = freeswitch.EventConsumer("CHANNEL_PROGRESS_MEDIA")
-- con = freeswitch.EventConsumer("CHANNEL_HANGUP_COMPLETE")
-- con = freeswitch.EventConsumer("BACKGROUND_JOB")
-- -- con = freeswitch.EventConsumer("CHANNEL_STATE")
-- con = freeswitch.EventConsumer("CUSTOM lua::stop_event")

api = freeswitch.API()

hostname = api:execute("hostname")

i = 0
while true do
    event_name = false
    event_subclass = false
    if i > 50 then
        break
    end
    i = i + 1
    print(i)
    -- pop(1) blocks until there is an event
    -- pop(1,500) blocks for max half a second until there is an event
    e = con:pop(1)

    -- 0. Check Background job -> assign uuid to callrequest
    -- 1. Get Hangup even
    -- 2. Check vars : if flag Newfies call
    -- 3. Update Call Status if started
    -- 4. Update Call Status when stop
    -- 5. store CDR


    if e then
        -- Get the Events info
        event_name = e:getHeader("Event-Name") or ""
        event_subclass = e:getHeader("Event-Subclass") or ""

        if event_name == 'CHANNEL_CREATE' or event_name == 'CHANNEL_HANGUP_COMPLETE' or event_name == 'BACKGROUND_JOB' or event_name == 'CHANNEL_ANSWER' then

            logger('-----------------------------')
            logger(event_name)
            logger(event_subclass)

            if event_name == 'BACKGROUND_JOB' then
                variable_newfiesdialer = e:getHeader("variable_newfiesdialer")
                if variable_newfiesdialer ~= nil then
                    logger("variable_newfiesdialer is: " .. variable_newfiesdialer .. "\n")
                end
                data = e:getBody()
                if data ~= nil then
                    if string.len(data) > 10 then
                        if string.sub(data, 0, 4) == '-ERR' then
                            logger("ERROR OUTBOUND: " .. string.sub(data, 5) .. "(END)\n")
                        end
                    end
                    logger("Here's getBody: " .. trim(data) .. "(END)\n")
                end
            end

            if event_name == 'CHANNEL_HANGUP_COMPLETE' then
                logger('************************************')
                variable_newfiesdialer = e:getHeader("variable_newfiesdialer") or ""
                logger(variable_newfiesdialer)
                logger('************************************')
                if variable_newfiesdialer ~= nil then
                    logger("variable_newfiesdialer is: " .. variable_newfiesdialer .. "\n")
                end
            end

            data = e:getBody()
            if data ~= nil then
                logger("Here's getBody:\n" .. trim(data) .. "\n")
            end
            --logger("Here's everything:\n" .. data .. "\n")

            -- Grab a specific channel variable
            uuid = e:getHeader("uuid")
            if uuid ~= nil then
                logger("uuid is: " .. uuid .. "\n")
            end
        end

        --load = api:execute("status")

        if (event_name == "CUSTOM" and event_subclass == "lua::stop_event") then
            action = e:getHeader("Action") or ""
            if (action == "stop") then
                logger("got stop message, Exiting")
                break
            end
        end -- not a custom message
    end

end -- while
