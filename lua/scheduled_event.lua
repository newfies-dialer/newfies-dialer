-- Version: MPL 1.1
--
-- The contents of this file are subject to the Mozilla Public License Version
-- 1.1 (the "License"); you may not use this file except in compliance with
-- the License. You may obtain a copy of the License at
-- http://www.mozilla.org/MPL
--
-- Software distributed under the License is distributed on an "AS IS" basis
-- WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
-- for the specific language governing rights and limitations under the
-- License
--
-- The Original Code is FreeSWITCH[tm] LUA event scheduler
--
-- The primary maintainer of this project is
-- Bret McDanel <bret AT 0xdecafbad dot com>
--
-- Portions created by the Initial Developer are Copyright (C) 2007
-- the Initial Developer. All Rights Reserved
--
-- Contributor(s)
--
-- Why use this?
--  No reason in particular, however if you use sched_api and shut down you lose your scheduled events, by
--  placing them in a database you get the advantage of them being able to survive a shutdown/crash/reboot/etc
--  Additionally this script is written in a way to allow for multiple switch boxes to access the same database
--  and look  for events to process, in this way you can scale this to a very large amount of actions
--
--
-- Usage: in FreeSWITCH console or fs_cli,
-- luarun scheduled_event.lua
--        starts the script - this is not needed if its auto loaded
-- luarun scheduled_event.lua <dbuser username> <dbhost hostname> <dbpass password> <dbname database_name>
--        changes the DB info allowing you to do load management, maintenence, or other things
-- luarun scheduled_event.lua stop
--        stops the running script
--
--      in lua.conf.xml:
--   <param name="startup-script" value="scheduled_event.lua"/>
--
--
-- You need to get "mysql.so" for lua and install it in <freeswitch install>/luasql/mysql.so
--   (or some other place that is in the search path)
--
-- Minimal DB schema **AUTOMAGICALLY CREATED IF IT DOES NOT EXIST** (at script start)
-- CREATE TABLE scheduler (
--    acctid int(11) NOT NULL auto_increment,
--    action varchar(1024) NOT NULL,
--    timestamp timestamp NOT NULL,
--    server varchar(64) NOT NULL DEFAULT '*',
--    primary key (acctid)
-- );
--
-- "actions" in the scheduler table should be api commands eg:
-- insert into scheduler (action,timestamp) values ("pa call 1234",NOW())
--
--
-- Every "heartbeat" events are pulled 1 at a time using write locks on mysql
-- if your MySQL supports those locks, then only one process can access the DB at a time
-- events are immediately deleted, and then processed to keep the lock time low
-- failed events are NOT rescheduled
-- many boxes can pull events and process them, however I did not attempt to process more
-- events than time allows for in a given heartbeat interval, some backlog may exist which
-- may cause this script to totally freak


-- currently this script requires http://jira.freeswitch.org/browse/MODAPP-357

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
PROGNAME = "scheduled_event.lua"

function logger(message)
    freeswitch.console_log(LOGLEVEL,"["..PROGNAME.."] "..message.."\n")
end


if argv[1] then
    i=1
    while argv[i] do
        if argv[i] == "stop" then
            --Send Stop message
            local event = freeswitch.Event("custom", "lua::scheduled_event")
            event:addHeader("Action", "stop")
            event:fire()
            logger("Sent stop message to lua script")
            return
        elseif (argv[i] == "dbuser") then
            i=i+1
            if argv[i] then
                logger("Setting DB Username to "..argv[i])
                USERNAME = argv[i]
            else
                logger("You must specify a username!")
            end
        elseif (argv[i] == "dbhost") then
            i=i+1
            if argv[i] then
                logger("Setting DB Hostname to "..argv[i])
                DBHOST = argv[i]
            else
                logger("You must specify a hostname!")
            end
        elseif (argv[i] == "dbpass") then
            i=i+1
            if argv[i] then
                logger("Setting DB Password to "..argv[i])
                PASSWORD = argv[i]
            else
                logger("You must specify a password!")
            end
        elseif (argv[i] == "dbname") then
            i=i+1
            if argv[i] then
                logger("Setting DB to "..argv[i])
                DATABASE = argv[i]
            else
                logger("You must specify a database name!")
            end
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
blah = assert(dbcon:execute("CREATE TABLE if not exists "..TABLENAME.." ("..
               "acctid serial NOT NULL PRIMARY KEY,"..
               "action varchar(1024) NOT NULL,"..
               "timestamp timestamp with time zone NOT NULL,"..
               "server varchar(64) NOT NULL DEFAULT '*'"..
               ")"))
dbcon:close()
env:close()

local event_name
local event_subclass

con = freeswitch.EventConsumer("all") -- too lazy to figure out why "heartbeat CUSTOM lua::scheduled_event"
                                 -- does not work properly, that is really all we need
api = freeswitch.API()

hostname = api:execute("hostname")

if blah ~= 0 then
    logger("Unable to connect to DB or create the table, something is broken.")
else
    for e in (function() return con:pop(1) end) do
        event_name = e:getHeader("Event-Name") or ""
        event_subclass = e:getHeader("Event-Subclass") or ""

        if(event_name == "HEARTBEAT") then
            -- check the system load
            load = api:execute("status")
            print(load)
            --cur_sessions,rate_sessions,max_rate,max_sessions = string.match(load, "%d+ session.s. - %d+ out of max %d+ per sec\n%d+ session.s. max")
            cur_sessions = "1"
            rate_sessions = "1"
            max_rate = "1"
            max_sessions = "1"
            if ((tonumber(cur_sessions) < tonumber(max_sessions)) and (tonumber(rate_sessions) < tonumber(max_rate))) then
                env = assert (luasql.postgres())
                dbcon = assert (env:connect(DATABASE,USERNAME,PASSWORD,DBHOST, 5432))
                while true do
                    assert (dbcon:execute("LOCK TABLE "..TABLENAME.." WRITE"))
                    cur = assert (dbcon:execute("select * from "..TABLENAME.." where timestamp < NOW() and (server = '"..hostname.."' or server = '*') order by timestamp limit 1"))
                    row = cur:fetch({},"a")
                    if not row then
                        break
                    end
                    assert (dbcon:execute("delete from "..TABLENAME.." where acctid = "..row.acctid));
                    assert (dbcon:execute("UNLOCK TABLES"))
                    apicmd,apiarg = string.match(row.action,"(%w+) (.*)")
                    api:execute(apicmd,apiarg)
                end -- while
                dbcon:close()
                env:close()
            end -- rate limiting
        else
            if (event_name == "CUSTOM" and event_subclass == "lua::scheduled_event") then
                action = e:getHeader("Action") or ""
                if (action == "stop") then
                    logger("got stop message, Exiting")
                    break
                end
            end -- not a custom message
        end -- not a processable event
    end -- foreach event
end -- main loop, DB connection established
