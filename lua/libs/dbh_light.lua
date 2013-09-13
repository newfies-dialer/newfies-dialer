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


--It might worth to rename this to model.lua

local oo = require "loop.simple"
--local redis = require 'redis'
--require "memcached"
require "constant"
require "settings"

--redis.commands.expire = redis.command('EXPIRE')
--redis.commands.ttl = redis.command('TTL')

DBH = oo.class{
    dbh = nil,
    debugger = nil,
    results = {},
    caching = false,
}

function DBH:__init(debug_mode, debugger)
    -- self is the class
    return oo.rawnew(self, {
        debug_mode = debug_mode,
        debugger = debugger,
    })
end

function DBH:connect()
    -- connect to ODBC database
    ODBC_DBNAME = 'newfiesdialer'
    self.dbh = freeswitch.Dbh("odbc://"..ODBC_DBNAME..":"..DBUSER..":"..DBPASS)
    assert(self.dbh:connected())
end

function DBH:disconnect()
    self.dbh:release() -- optional
end

function DBH:get_list(sqlquery)
    self.debugger:msg("DEBUG", "Load SQL : "..sqlquery)
    local list = {}
    self.dbh:query(sqlquery, function(row)
        --Let's transform empty value to False
        --We do this to have similar behavior to luasql
        --luasql doesn't return the empty/null fields
        for k, v in pairs(row) do
            if v == '' then
                row[k] = false
            end
        end
        list[tonumber(row.id)] = row
        --freeswitch.consoleLog(fslevel, string.format("%5s : %s\n", row.id, row.name))
    end)
    return list
end

function DBH:get_cache_list(sqlquery, ttl)
    return self:get_list(sqlquery)
end

function DBH:get_object(sqlquery)
    self.debugger:msg("DEBUG", "Load SQL : "..sqlquery)
    local res_get_object
    self.dbh:query(sqlquery, function(row)
        res_get_object = row
        for k, v in pairs(res_get_object) do
            if v == '' then
                res_get_object[k] = false
            end
        end
        --freeswitch.consoleLog(fslevel, string.format("%5s : %s\n", row.id, row.name))
    end)
    return res_get_object
end

function DBH:get_cache_object(sqlquery, ttl)
    return self:get_object(sqlquery)
end

function DBH:execute(sqlquery)
    local res = self.dbh:query(sqlquery)
    return res
end
