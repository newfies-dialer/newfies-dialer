--
-- Easily power a caching system based on Filesystem
-- It's recommended to use ramdisk to get better performances
-- @ mkdir -p /tmp/ram
-- @ sudo mount -t tmpfs -o size=512M tmpfs /tmp/ram/
-- Set the CACHE_DIRECTORY setting to this directory
--
--
-- Copyright (C) 2013 Arezqui Belaid <areski@gmail.com>
--
-- Permission is hereby granted, free of charge, to any person
-- obtaining a copy of this software and associated documentation files
-- (the "Software"), to deal in the Software without restriction,
-- including without limitation the rights to use, copy, modify, merge,
-- publish, distribute, sublicense, and/or sell copies of the Software,
-- and to permit persons to whom the Software is furnished to do so,
-- subject to the following conditions:
--
-- The above copyright notice and this permission notice shall be
-- included in all copies or substantial portions of the Software.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
-- EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
-- MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
-- NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
-- BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
-- ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
-- CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-- SOFTWARE.


require "lfs"
local md5 = require "md5"
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
-- run test
--
if false then

    caching = LFS_Caching(nil)

    local cmsgpack = require 'cmsgpack'
    local inspect = require 'inspect'

    value_test = {}
    value_test["1"] = "Orange"
    value_test["2"] = "Apple"
    value_test["3"] = "Carrot"

    msgpack = cmsgpack.pack(value_test)
    print(msgpack)

    print("Test Get Cache")
    res = caching:get('hashkeydb', 3)
    if not(res) then
        print("Set Cache")
        caching:set('hashkeydb', msgpack)
    else
        print(inspect(cmsgpack.unpack(res)))
    end
end
