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

--TODO: It might worth to rename this to model.lua

local cmsgpack = require "cmsgpack"
local LFS_Caching = require "lfs_cache"
local md5 = require "md5"
require "constant"
require "settings"


local DBH = {
    dbh = nil,
    debugger = nil,
    results = {},
    caching = false,
}

function DBH:new (o)
    o = o or {}   -- create object if user does not provide one
    setmetatable(o, self)
    self.__index = self
    return o
end

function DBH:connect()
    -- connect to ODBC database
    ODBC_DBNAME = 'newfiesdialer'
    self.dbh = freeswitch.Dbh("odbc://"..ODBC_DBNAME..":"..DBUSER..":"..DBPASS)
    -- assert(self.dbh:connected())
    if self.dbh:connected() == false then
        self.debugger:msg("ERROR", "Cannot connect to database")
        return false
    end

    if USE_CACHE then
        --self.caching = redis.connect('127.0.0.1', 6379)
        --self.caching = memcached.connect('127.0.0.1', 11211)
        self.caching = LFS_Caching:new{}
    end
    return true
end

function DBH:disconnect()
    -- self.dbh:release() -- optional
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
    --If not Cache
    if not USE_CACHE then
        return self:get_list(sqlquery)
    end
    local hashkey = md5.sumhexa(sqlquery)
    --memcached / redis
    --local value = self.caching:get(hashkey)
    --lfs_cache
    local value = self.caching:get(hashkey, ttl)
    if value then
        --Cached
        return cmsgpack.unpack(value)
    else
        --Not in Cache
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
        --Add in Cache
        local msgpack = cmsgpack.pack(list)
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
    local hashkey = md5.sumhexa(sqlquery)
    --local value = self.caching:get(hashkey)
    --lfs_cache
    local value = self.caching:get(hashkey, ttl)
    if value then
        --Cached
        return cmsgpack.unpack(value)
    else
        --Not in cache
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

        --Add in cache
        local msgpack = cmsgpack.pack(res_get_object)
        --Redis
        --self.caching:set(hashkey, msgpack)
        --self.caching:expire(hashkey, ttl)
        --Memcache
        --self.caching:set(hashkey, msgpack, ttl)
        --lfs_cache
        self.caching:set(hashkey, msgpack)
        return res_get_object
    end
end

function DBH:execute(sqlquery)
    local res = self.dbh:query(sqlquery)
    -- local res = assert(self.dbh:query(sql_query))
    --Get affected rows
    --self.dbh:affected_rows()
    return res
end

return DBH
