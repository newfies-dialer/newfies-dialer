
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


local event_name
local event_subclass

con = freeswitch.EventConsumer("all") -- too lazy to figure out why "heartbeat CUSTOM lua::stop_event"
                                 -- does not work properly, that is really all we need
api = freeswitch.API()

hostname = api:execute("hostname")

i = 0
while true do
    event_name = false
    event_subclass = false
    if i > 100 then
        break
    end
    i = i + 1
    print(i)
    -- pop(1) blocks until there is an event
    -- pop(1,500) blocks for max half a second until there is an event
    e = con:pop(1)

    -- 1. Get Hangup even
    -- 2. Check vars : if flag Newfies call
    -- 3. Update Call Status if started
    -- 4. Update Call Status when stop
    -- 5. store CDR


    if e then
        event_name = e:getHeader("Event-Name") or ""
        event_subclass = e:getHeader("Event-Subclass") or ""
        logger('-----------------------------')
        logger(event_name)
        logger(event_subclass)

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
