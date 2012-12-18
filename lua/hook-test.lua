-- hook-test.lua                 
-- demonstrates using env to look at channel variables in hangup hook script

-- See everything
dat = env:serialize()            
freeswitch.consoleLog("INFO","Here's everything:\n" .. dat .. "\n")

-- Grab a specific channel variable
dat = env:getHeader("uuid")      
freeswitch.consoleLog("INFO","Inside hangup hook, uuid is: " .. dat .. "\n")                            

-- Drop some info into a log file...
res = os.execute("echo " .. dat .. " >> /tmp/fax.log")
res = os.execute("echo YOUR COMMAND HERE >> /tmp/fax.log")

-- If you created a custom variable you can get it also...
dat = env:getHeader("my_custom_var")
freeswitch.consoleLog("INFO","my_custom_var is '" .. dat .. "'\n")

