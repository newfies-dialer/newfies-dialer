-- test_db.lua
-- Connects to a database using freeswitch.dbh connection pooling, checks PIN, reads balance
-- A hangup function makes the code a bit cleaner

package.path = package.path .. ";/usr/share/newfies-lua/?.lua";
package.path = package.path .. ";/usr/share/newfies-lua/libs/?.lua";

local inspect = require 'inspect'
require "debugger"
require "settings"


-- connect to ODBC database
local ODBC_DBNAME = 'newfiesdialer'
local dbh = freeswitch.Dbh("odbc://"..ODBC_DBNAME..":"..DBUSER..":"..DBPASS)
local row = {}

function hangup_call ()
    session:sleep(250)
    session:streamFile("voicemail/vm-goodbye.wav")
    session:hangup()
end

if dbh:connected() == false then
   freeswitch.consoleLog("notice", " cannot connect to database" .. dsn .. "\n")
   hangup_call()
end

--answer the call
session:answer()

-- Pull account from database -> assumes that acct is unique
my_query = "select * from dialer_contact where id=1"
assert(dbh:query(my_query, function(qrow)
for key, val in pairs(qrow) do
    row[key] = val
end
end))

print(inspect(row))

local fs_env = false
local debugger = Debugger(fs_env)
debugger:msg("ERROR", "Play...")
debugger:msg("ERROR", inspect(row))

session:streamFile("/usr/share/newfies_ramdisk/tts/flite_d75315bfe82444aa79abb31140028701.wav")
session:hangup()
