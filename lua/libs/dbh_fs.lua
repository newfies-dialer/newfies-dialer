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
local inspect = require 'inspect'
local cmsgpack = require 'cmsgpack'
--local redis = require 'redis'
--require "memcached"
local lfs_cache = require "lfs_cache"
require "constant"
require "settings"
require "md5"

--redis.commands.expire = redis.command('EXPIRE')
--redis.commands.ttl = redis.command('TTL')

USE_CACHE = false

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

    if USE_CACHE then
        --self.caching = redis.connect('127.0.0.1', 6379)
        --self.caching = memcached.connect('127.0.0.1', 11211)
        self.caching = LFS_Caching(nil)
    end
end

function DBH:disconnect()
    self.dbh:release() -- optional
end

function DBH:get_list(sqlquery)
    self.debugger:msg("DEBUG", "Load SQL : "..sqlquery)
    local list = {}
    sql = "SELECT id, name FROM my_table"
    self.dbh:query(sqlquery, function(row)
        --Let's transform empty value to False
        --We do this to have similar behavior to luasql
        --luasql doesn't return the empty/null fields
        for k, v in pairs(row) do
            if v == '' then
                row[k] = false
            end
        end
        list[row.id] = row
        --freeswitch.consoleLog(fslevel, string.format("%5s : %s\n", row.id, row.name))
    end)
    return list
end

function DBH:get_cache_list(sqlquery, ttl)
    --If not Cache
    if not USE_CACHE then
        return self:get_list(sqlquery)
    end
    hashkey = md5.sumhexa(sqlquery)
    --memcached / redis
    --local value = self.caching:get(hashkey)
    --lfs_cache
    local value = self.caching:get(hashkey, ttl)
    if value then
        --Cached
        return cmsgpack.unpack(value)
    else
        --Not in Cache
        cur = assert(self.con:execute(sqlquery))
        list = {}
        row = cur:fetch ({}, "a")
        while row do
            list[tonumber(row.id)] = row
            row = cur:fetch ({}, "a")
        end
        cur:close()
        --Add in Cache
        msgpack = cmsgpack.pack(list)
        --Redis
        --self.caching:set(hashkey, msgpack)
        --self.caching:expire(hashkey, ttl)
        --Memcache
        --self.caching:set(hashkey, msgpack, ttl)
        --lfs_cache
        self.caching:set(hashkey, msgpack)
        return list
    end
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
    --If not Cache
    if not USE_CACHE then
        return self:get_object(sqlquery)
    end
    hashkey = md5.sumhexa(sqlquery)
    --local value = self.caching:get(hashkey)
    --lfs_cache
    local value = self.caching:get(hashkey, ttl)
    if value then
        --Cached
        return cmsgpack.unpack(value)
    else
        --Not in Cache
        cur = assert(self.con:execute(sqlquery))
        row = cur:fetch ({}, "a")
        cur:close()
        --Add in Cache
        msgpack = cmsgpack.pack(row)
        --Redis
        --self.caching:set(hashkey, msgpack)
        --self.caching:expire(hashkey, ttl)
        --Memcache
        --self.caching:set(hashkey, msgpack, ttl)
        --lfs_cache
        self.caching:set(hashkey, msgpack)
        return row
    end
end

function DBH:execute(sqlquery)
    res = self.dbh:query(sqlquery)
    --Get affected rows
    --self.dbh:affected_rows()
    return res
end
