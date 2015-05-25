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

-- List of Channels States
-- http://wiki.freeswitch.org/wiki/Event_list#CHANNEL_STATE
--
-- Usage:
-- To stop : luarun /usr/share/newfies-lua/listener.lua stop

local luasql = require "luasql.postgres"
require "settings"

PROGNAME = "listener.lua" -- Program name (used for logging)
LOGLEVEL = "info" -- LOGGING LEVEL

local MAX_RECONNECT = 100 -- 50 minutes
local SLEEP_RECONNECT = 30 -- 30 seconds sleep between reconnect
local env = nil
local dbcon = nil

local results = {}
local incr = 0

-- DROP TABLE if exists call_event;
local create_table_sql = [[
    CREATE TABLE if not exists call_event (
        id serial NOT NULL PRIMARY KEY,
        event_name varchar(200) NOT NULL,
        body varchar(200) NOT NULL,
        job_uuid varchar(200),
        call_uuid varchar(200) NOT NULL,
        used_gateway_id integer,
        callrequest_id integer,
        alarm_request_id integer,
        callerid varchar(200),
        phonenumber varchar(200),
        duration integer DEFAULT 0,
        billsec integer DEFAULT 0,
        hangup_cause varchar(40),
        hangup_cause_q850 varchar(10),
        amd_status varchar(40),
        leg varchar(10) DEFAULT 'aleg',
        starting_date timestamp with time zone,
        status smallint,
        created_date timestamp with time zone NOT NULL
        );
    CREATE INDEX call_event_idx_status ON call_event (status);
    ]]

function logger(message)
    freeswitch.console_log(LOGLEVEL,"["..PROGNAME.."] "..message.."\n")
end

function debug(message)
    -- print(message)
    freeswitch.console_log("ERROR","["..PROGNAME.."] "..message.."\n")
end

function sleep(seconds)
    time = os.clock()
    while os.clock()-time < seconds do end
end

function connect()
    --connect database function supporting reconnection
    env = assert(luasql.postgres())
    dbcon, serr = env:connect(DBNAME, DBUSER, DBPASS, DBHOST, DBPORT)
    if serr then
        countrecon = 0
        while serr do
            debug("serr:"..tostring(serr))
            countrecon = countrecon + 1
            debug("countrecon:"..tostring(countrecon))
            sleep(SLEEP_RECONNECT)
            if countrecon == MAXRECONNECT then
                -- max reconnect reached
                break
            end
            -- reconnect
            dbcon, serr = env:connect(DBNAME, DBUSER, DBPASS, DBHOST, DBPORT)
        end
    end
    if not dbcon then
        return false
    end
    return true
end

function disconnect()
    if dbcon then
        dbcon:close()
    end
    env:close()
end

function get_list(sqlquery)
    debug("Load SQL : "..sqlquery)
    cur, serr = dbcon:execute(sqlquery)
    if serr then
        debug("serr:"..tostring(serr))
    end
    list = {}
    row = cur:fetch ({}, "a")
    while row do
        list[tonumber(row.id)] = row
        row = cur:fetch ({}, "a")
    end
    cur:close()
    return list
end

function exec_sql(sqlquery)
    debug("Execute SQL : "..sqlquery)
    cur, serr = dbcon:execute(sqlquery)
    if serr then
        debug("serr:"..tostring(serr))
    end
    return serr
end

function trim(s)
    --trim text
    if s == nil then
        return ''
    end
    return (string.gsub(s, "^%s*(.-)%s*$", "%1"))
end

function commit_event()
    --Commit events with one bulk insert to the DB
    sql_result = ''
    count = 0
    for k, v in pairs(results) do
        count = count + 1
        if count > 1 then
            sql_result = sql_result..","
        end
        -- VALUES ('%s', '%s', '%s', 4'%s', '%s', now(), 7'%s', '%s', '%s', '%s', '%s', 12'%s', '%s', '%s', 15'%s', %s)]], event_name, body, job_uuid, call_uuid, status, used_gateway_id, callrequest_id, alarm_request_id, duration, billsec, callerid, phonenumber, hangup_cause, hangup_cause_q850, amd_status, 0)
        sql_result = sql_result.."('"..v[1].."', '"..v[2].."', '"..v[3].."', '"..v[4].."', "..v[5]..", "..v[6]..", "..v[7]..", "..v[8]..", "..v[9]..", "..v[10]..", '"..v[11].."', '"..v[12].."', '"..v[13].."', '"..v[14].."', '"..v[15].."', "..""..v[16]..", "..v[16]..", '"..v[18].."')"
    end
    insertsql = "INSERT INTO call_event (event_name, body, job_uuid, call_uuid, used_gateway_id, callrequest_id, alarm_request_id, status, duration, billsec, callerid, phonenumber, hangup_cause, hangup_cause_q850, amd_status, starting_date, created_date, leg) VALUES "..sql_result
    if count > 0 then
        --logger(insertsql)
        connect()
        serr = exec_sql(insertsql)
        if serr then
            -- retry once to execute the sql
            sleep(SLEEP_RECONNECT)
            serr = exec_sql(insertsql)
        end
        disconnect()

        --Reset to zero
        results = {}
        incr = 0
    end
end

function push_event(event_name, body, job_uuid, call_uuid, used_gateway_id, callrequest_id, alarm_request_id, status, duration, billsec, callerid, phonenumber, hangup_cause, hangup_cause_q850, amd_status, starting_date, leg)
    results[incr] = {event_name, body, job_uuid, call_uuid, used_gateway_id, callrequest_id, alarm_request_id, status, duration, billsec, callerid, phonenumber, hangup_cause, hangup_cause_q850, amd_status, starting_date, os.time(), leg}
    incr = incr + 1
    if (incr >= 500) then
        commit_event()
    end
end

if argv and argv[1] then
    i = 1
    while argv[i] do
        if argv[i] == "stop" then
            --Send Stop message
            local event = freeswitch.Event("custom", "lua::stop_event")
            event:addHeader("Action", "stop")
            event:fire()
            logger("Sent stop message to lua script")
            return
        end
        i = i + 1
    end
    return
end

--
-- Main function starts here
--
logger("Starting")

connect()
serr = exec_sql(create_table_sql)
if serr then
    -- retry once to execute the sql
    sleep(SLEEP_RECONNECT)
    serr = exec_sql(create_table_sql)
end
disconnect()

-- prepare event capture
local event_name
local event_subclass
local fscon

-- Listen to FreeSWITCH Events
fscon = freeswitch.EventConsumer("ALL")
-- fscon = freeswitch.EventConsumer("CHANNEL_HANGUP_COMPLETE HEARTBEAT BACKGROUND_JOB CUSTOM lua::stop_event")

api = freeswitch.API()

hostname = api:execute("hostname")

i = 0
while true do
    event_name = false
    event_subclass = false
    i = i + 1
    -- pop(1) blocks until there is an event
    -- pop(1,500) blocks for max half a second until there is an event
    e = fscon:pop(1)

    if e then
        --default status: Pending
        status = 1
        -- Get the Events info
        event_name = e:getHeader("Event-Name") or ""
        event_subclass = e:getHeader("Event-Subclass") or ""
        job_uuid = e:getHeader("Job-UUID") or ""
        call_uuid = e:getHeader("Channel-Call-UUID") or ""
        used_gateway_id = e:getHeader("variable_used_gateway_id") or 0
        callrequest_id = e:getHeader("variable_callrequest_id") or 0
        alarm_request_id = e:getHeader("variable_alarm_request_id") or 0
        duration = e:getHeader("variable_duration") or 0
        billsec = e:getHeader("variable_billsec") or 0
        callerid = e:getHeader("variable_origination_caller_id_number") or ""
        accountcode = e:getHeader("variable_accountcode") or ""
        -- phonenumber = e:getHeader("Caller-Destination-Number") or ""
        phonenumber = e:getHeader("variable_dialout_phone_number") or ""
        hangup_cause = e:getHeader("variable_hangup_cause") or ""
        amd_status = e:getHeader("variable_amd_status") or "person"
        leg = e:getHeader("variable_legtype") or "aleg"
        hangup_cause_q850 = e:getHeader("variable_hangup_cause_q850") or ""
        start_uepoch = e:getHeader("variable_start_uepoch") -- 1355809698350872

        -- Enable for Event debugging
        -- freeswitch.consoleLog("info","--------------------------------------")
        -- freeswitch.consoleLog("info",e:serialize())

        if start_uepoch ~= nil then
            starting_date = 'to_timestamp('..start_uepoch..'/1000000)'
        else
            starting_date = 'NOW()'
        end
        if alarm_request_id == 'None' then
            alarm_request_id = 'NULL'
        end

        -- HEARTBEAT happening every 30 seconds
        if event_name == 'HEARTBEAT' then
            logger(event_name .. "\n")
            --let's empty the buffer
            commit_event()
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
                push_event(event_name, body, job_uuid, call_uuid, used_gateway_id, callrequest_id, alarm_request_id, status, duration, billsec, callerid, phonenumber, hangup_cause, hangup_cause_q850, amd_status, starting_date, leg)

            elseif event_name == 'CHANNEL_HANGUP_COMPLETE' then

                variable_newfiesdialer = e:getHeader("variable_newfiesdialer") or ""
                -- if variable_newfiesdialer ~= nil then
                --     logger("variable_newfiesdialer is: " .. variable_newfiesdialer .. "\n")
                -- end

                if hangup_cause ~= 'NORMAL_CLEARING' and hangup_cause ~= 'ALLOTTED_TIMEOUT' and leg ~= 'bleg' then
                    status = 0
                end

                --Insert Event to Database
                push_event(event_name, body, job_uuid, call_uuid, used_gateway_id, callrequest_id, alarm_request_id, status, duration, billsec, callerid, phonenumber, hangup_cause, hangup_cause_q850, amd_status, starting_date, leg)
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
