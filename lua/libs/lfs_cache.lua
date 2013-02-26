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

require "lfs"
require "md5"
local oo = require "loop.simple"
local inspect = require 'inspect'


CACHE_DIRECTORY = '/tmp'



LFS_Caching = oo.class{
    -- default field values
    debugger = nil,
}

function LFS_Caching:__init(debugger)
    -- self is the class
    return oo.rawnew(self, {
        debugger = debugger,
    })
end

--
-- Check file exists and readable
function LFS_Caching:file_exists(path)
    local attr = lfs.attributes(path)
    if (attr ~= nil) then
        return true
    else
        return false
    end
end

--
-- return a md5 file for the caching
function LFS_Caching:key_filepath(key)
    return CACHE_DIRECTORY..'/'..md5.sumhexa(key)
end


-- get all lines from a file, returns an empty
-- list/table if the file does not exist
function LFS_Caching:read_from_file(file)
    if not self:file_exists(file) then
        return nil
    end
    local f = io.open(file, "rb")
    local content = f:read("*all")
    f:close()
    return content
end

--
-- Write content to file
function LFS_Caching:write_to_file(path, content)
    local file = io.open(path, "w")
    file:write(content)
    file:close()
    return true
end

-- Creates a cache for the key with content
-- key: value of the cache
-- content: object # whatever is compatible
function LFS_Caching:set(key, content)
    local path = self:key_filepath(key)
    local success = self:write_to_file(path, content)
    if not success then
        --print("Couldn't archive cache '%s' to '%s'", key, path)
    end
end

-- Returns contents of cache keys
-- key: value of the cache
-- ttl: number [optional] max age of file in seconds
function LFS_Caching:get(key, ttl)
    local path = self:key_filepath(key)
    if not self:file_exists(path) then
        return nil
    end

    if ttl then
        local cache_age = os.time() - lfs.attributes(path).modification
        if cache_age > ttl then
            return nil
        end
    end
    result = self:read_from_file(path)
    return result
end


--
-- test
if false then

    caching = LFS_Caching(nil)

    -- print("get Cache")
    -- res = caching:get('mykey', 10)
    -- print(res)
    -- if not(res) then
    --     print("Set Cache")
    --     caching:set('mykey', 12345)
    --     res = 12345
    --     print(res)
    -- end

    local cmsgpack = require 'cmsgpack'
    local inspect = require 'inspect'

    value_test = {}
    value_test["1"] = "Orange"
    value_test["2"] = "Apple"
    value_test["3"] = "Carrot"

    msgpack = cmsgpack.pack(value_test)
    print(msgpack)

    print("get Cache")
    res = caching:get('hashkeydb', 3)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~")
    if not(res) then
        print("Set Cache")
        caching:set('hashkeydb', msgpack)
    else
        print("res ==> "..res)
        print("UNPACK RESUlt => ")
        print(inspect(cmsgpack.unpack(res)))
    end
end
