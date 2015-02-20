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


--TODO: It might worth to rename this to dbh_luasql

local luasql = require "luasql.postgres"
local cmsgpack = require 'cmsgpack'
--local redis = require 'redis'
local LFS_Caching = require "lfs_cache"
local md5 = require "md5"
require "constant"
require "settings"


--redis.commands.expire = redis.command('EXPIRE')
--redis.commands.ttl = redis.command('TTL')

local DBH = {
    env = nil,
    con = nil,
    debug_mode = nil,
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
    self.env = assert(luasql.postgres())
    self.con = self.env:connect(DBNAME, DBUSER, DBPASS, DBHOST, DBPORT)
    if not self.con then
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
    if self.con then
        self.con:close()
    end
    self.env:close()
end

function DBH:get_list(sqlquery)
    self.debugger:msg("DEBUG", "Load SQL : "..sqlquery)
    cur = assert(self.con:execute(sqlquery))
    list = {}
    row = cur:fetch ({}, "a")
    while row do
        list[tonumber(row.id)] = row
        row = cur:fetch ({}, "a")
    end
    cur:close()
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
    cur = assert(self.con:execute(sqlquery))
    row = cur:fetch ({}, "a")
    cur:close()
    return row
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
    res = self.con:execute(sqlquery)
    return res
end

return DBH
