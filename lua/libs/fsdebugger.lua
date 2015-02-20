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

-- local oo = require "loop.base"
local logging_file = require "logging.file"
local logging = require "logging"

local LOGDIR = '/var/log/newfies/'
local logger = logging_file(LOGDIR .. "newfieslua_logs_%s.log", "%Y-%m-%d", "%date %level %message\n")

--
-- Set Logging Level
-- logging.DEBUG
-- The DEBUG level designates fine-grained informational events that are most useful to debug an application.
-- logging.INFO
-- The INFO level designates informational messages that highlight the progress of the application at coarse-grained level.
-- logging.WARN
-- The WARN level designates potentially harmful situations.
-- logging.ERROR
-- The ERROR level designates error events that might still allow the application to continue running.
-- logging.FATAL
-- The FATAL level designates very severe error events that would presumably lead the application to abort.
--
logger:setLevel(logging.DEBUG)


local Debugger = {
    -- default field values
    fs_env = false,
    call_id = '',
}

function Debugger:new (o)
    o = o or {}   -- create object if user does not provide one
    setmetatable(o, self)
    self.__index = self
    return o
end

function Debugger:set_call_id(call_id)
    --Set property call_id
    self.call_id = call_id
end

function Debugger:msg_inspect(level, message)
    --inspect the message prior calling the debugger
    local inspect = require "inspect"
    self:msg(level, inspect(message))
end

function Debugger:getfs_level(level)
    --get freeswitch log level
    if level == 'DEBUG' then
        return 'debug'
    elseif level == 'WARN' then
        return 'warning'
    elseif level == 'ERROR' then
        return 'err'
    elseif level == 'NOTICE' then
        return 'notice'  --notice not supported by logger
    elseif level == 'INFO' then
        return 'info'
    else
        return 'info'  -- default value info
    end
end

function Debugger:msg(level, message)
    --Print out or logger message according to the verbosity
    local msg = self.call_id..' '..message
    -- level : DEBUG, INFO, WARN, ERROR
    if not self.fs_env then
        print(msg)
    else
        freeswitch.consoleLog(self:getfs_level(level), msg.."\n")
    end
    if level == 'DEBUG' then
        logger:debug(msg)
    elseif level == 'INFO' then
        logger:info(msg)
    elseif level == 'WARN' then
        logger:warn(msg)
    elseif level == 'ERROR' then
        logger:error(msg)
    end
end

return Debugger
