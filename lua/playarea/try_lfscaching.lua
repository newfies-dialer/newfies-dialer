--
-- run example LFS_Caching
--

package.path = package.path .. ";/usr/share/newfies-lua/?.lua";
package.path = package.path .. ";/usr/share/newfies-lua/libs/?.lua";

local inspect = require "inspect"
local cmsgpack = require 'cmsgpack'
local LFS_Caching = require 'lfs_cache'

local caching = LFS_Caching:new{}


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
