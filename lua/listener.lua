

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

function db_insert_event(event_name, body, job_uuid, call_uuid, used_gateway_id, callrequest_id, status, duration, billsec, callerid, phonenumber, hangup_cause, hangup_cause_q850, starting_date)
    -- event_name, body, job_uuid, call_uuid
    sql = string.format([[
    INSERT INTO call_event (event_name, body, job_uuid, call_uuid, status, created_date, used_gateway_id, callrequest_id, duration, billsec, callerid, phonenumber, hangup_cause, hangup_cause_q850, starting_date)
    VALUES ('%s', '%s', '%s', '%s', '%s', now(), '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s)]], event_name, body, job_uuid, call_uuid, status, used_gateway_id, callrequest_id, duration, billsec, callerid, phonenumber, hangup_cause, hangup_cause_q850, starting_date)
    --logger(sql)
    env = assert (luasql.postgres())
    dbcon = assert (env:connect(DATABASE,USERNAME,PASSWORD,DBHOST, 5432))
    res = assert (dbcon:execute(sql))
    dbcon:close()
    env:close()
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
-- DROP TABLE call_event;
blah = assert(dbcon:execute([[
    DROP TABLE call_event;
    CREATE TABLE if not exists call_event (
        id serial NOT NULL PRIMARY KEY,
        event_name varchar(200) NOT NULL,
        body varchar(200) NOT NULL,
        job_uuid varchar(200),
        call_uuid varchar(200) NOT NULL,
        used_gateway_id integer,
        callrequest_id integer,
        callerid varchar(200),
        phonenumber varchar(200),
        duration integer DEFAULT 0,
        billsec integer DEFAULT 0,
        hangup_cause varchar(40),
        hangup_cause_q850 varchar(10),
        starting_date timestamp with time zone,
        status integer,
        created_date timestamp with time zone NOT NULL
        );
    CREATE INDEX call_event_idx_uuid ON call_event (call_uuid);
    CREATE INDEX call_event_idx_status ON call_event (status);
    CREATE INDEX call_event_idx_date ON call_event (created_date);
    ]]))
--UNIQUE (event_name, call_uuid)
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
    -- if i > 200 then
    --     break
    -- end
    i = i + 1
    -- pop(1) blocks until there is an event
    -- pop(1,500) blocks for max half a second until there is an event
    e = con:pop(1)

    if e then
        --default status
        status = 1
        -- Get the Events info
        event_name = e:getHeader("Event-Name") or ""
        event_subclass = e:getHeader("Event-Subclass") or ""
        job_uuid = e:getHeader("Job-UUID") or ""
        call_uuid = e:getHeader("Channel-Call-UUID") or ""
        used_gateway_id = e:getHeader("variable_used_gateway_id") or 0
        callrequest_id = e:getHeader("variable_callrequest_id") or 0
        duration = e:getHeader("variable_duration") or 0
        billsec = e:getHeader("variable_billsec") or 0
        callerid = e:getHeader("variable_outbound_caller_id_number") or ""
        accountcode = e:getHeader("variable_accountcode") or ""
        phonenumber = e:getHeader("variable_dialed_user") or ""
        hangup_cause = e:getHeader("variable_hangup_cause") or ""
        hangup_cause_q850 = e:getHeader("variable_hangup_cause_q850") or ""
        start_uepoch = e:getHeader("variable_start_uepoch") -- 1355809698350872
        if start_uepoch ~= nil then
            starting_date = 'to_timestamp('..start_uepoch..')'
        else
            starting_date = 'NOW()'
        end

        -- CHANNEL_ANSWER
        if event_name == 'CHANNEL_HANGUP_COMPLETE' or event_name == 'BACKGROUND_JOB' then

            --logger('-----------------------------')
            logger('Listener Event : '..event_name)
            --logger(event_subclass)
            body = e:getBody() or ''

            if event_name == 'BACKGROUND_JOB' then
                variable_newfiesdialer = e:getHeader("variable_newfiesdialer")
                -- if variable_newfiesdialer ~= nil then
                --     logger("variable_newfiesdialer is: " .. variable_newfiesdialer .. "\n")
                -- end

                if body ~= nil then
                    if string.len(body) > 10 then
                        if string.sub(body, 0, 4) == '-ERR' then
                            logger("ERROR OUTBOUND: " .. string.sub(body, 5) .. "(END)\n")
                        elseif string.sub(body, 0, 3) == '+OK' then
                            call_uuid = string.sub(body, 5, 40)
                            -- status 0 cause we dont need to use background job for success call
                            status = 0
                            logger("GOOD OUTBOUND: " .. call_uuid .. "(END)\n")
                        end
                    end
                    --logger("Here's getBody: " .. trim(body) .. "(END)\n")
                end

                --Insert Event to Database
                db_insert_event(event_name, body, job_uuid, call_uuid, used_gateway_id, callrequest_id, status, duration, billsec, callerid, phonenumber, hangup_cause, hangup_cause_q850, starting_date)

            elseif event_name == 'CHANNEL_HANGUP_COMPLETE' then

                variable_newfiesdialer = e:getHeader("variable_newfiesdialer") or ""
                -- if variable_newfiesdialer ~= nil then
                --     logger("variable_newfiesdialer is: " .. variable_newfiesdialer .. "\n")
                -- end

                if hangup_cause ~= 'NORMAL_CLEARING' then
                    status = 0
                end

                --Insert Event to Database
                db_insert_event(event_name, body, job_uuid, call_uuid, used_gateway_id, callrequest_id, status, duration, billsec, callerid, phonenumber, hangup_cause, hangup_cause_q850, starting_date)

            end

            -- dat = e:serialize()
            -- logger("Here's everything:\n" .. dat .. "\n")

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
