--
-- Test & demonstration file for "fsm.lua"
--

FSM = require "fsm"


-- function playmessage()
--     print("Play Message")
-- end

-- -- Define your state transitions here
-- local myStateTransitionTable = {
--     {"section1", "start", "section1", playmessage},
--     {"section1", "DTMF1", "section2", action1},
--     {"state2", "event2", "state3", action2},
--     {"state3", "event1", "state1", action3},
--     {"*",      "event3", "state3", action3},  -- for any state
--     {"*",      "*",      "unknow", unknow}   -- exception handler
-- }


function action1() print("Performing action 1") end
function action2() print("Performing action 2") end
function action3() print("Performing action 3") end
function unknow()
    print("Performing unknow")
    fsm:fire("event0")
end
function notunknow() print("Performing notunknow") end

-- Define your state transitions here
local myStateTransitionTable = {
    {"state1", "event1", "state2", action1},
    {"state2", "event2", "state3", action2},
    {"state3", "event1", "state1", action3},
    {"*",      "event3", "state3", action3},  -- for any state
    {"*",      "*",      "unknow", unknow},   -- exception handler
    {"unknow", "event0", "state2", notunknow},
    {"unknow", "*",      "state1", notunknow}
}

-- Create your finite state machine
fsm = FSM.new(myStateTransitionTable)

-- Use your finite state machine
-- which starts by default with the first defined state
print("Current FSM state: " .. fsm:get())

-- Or you can set another state
fsm:set("state2")
print("Current FSM state: " .. fsm:get())

-- Resond on "event" and last set "state"
fsm:fire("event3")
print("Current FSM state: " .. fsm:get())

fsm:fire("event1")
print("Current FSM state: " .. fsm:get())

fsm:fire("bloufff")
print("Current FSM state: " .. fsm:get())


-- function action1() print("Performing action 1") end

-- function action2() print("Performing action 2") end

-- function action3() print("Action 3: Exception raised") end

-- function action4() print("Wildcard in action !!!") end

-- -- Define your state transitions here
-- local myStateTransitionTable = {
-- 	{"state1", "event1", "state2", action1},
-- 	{"state2", "event2", "state3", action2}
-- }

-- -- Create your instance of a finite state machine
-- fsm = FSM.new(myStateTransitionTable)

-- -- print( "Constant UNKNOWN = " .. UNKNOWN )
-- print( "Constant FSM.UNKNOWN = " .. FSM.UNKNOWN )

-- -- Use your finite state machine
-- -- which starts by default with the first defined state
-- print("Current FSM state: " .. fsm:get())

-- -- Or you can set another state
-- fsm:set("state2")
-- print("Current FSM state: " .. fsm:get())

-- -- Respond on "event" and last set "state"
-- fsm:fire("event2")
-- print("Current FSM state: " .. fsm:get())

-- -- Force exception
-- print("Force exception by firing unknown event")
-- fsm:fire("event3")
-- print("Current FSM state: " .. fsm:get())

-- -- Test automated exception handling
-- local myStateTransitionTable2 = {
-- 	{"state1", "event1", "state2", action1},
-- 	{"state2", "event2", "state3", action2},
-- 	{"*"     , "event3", "state1", action4},
-- 	{"*"     , "?",      "state1", action3}
-- }

-- -- Create your instance of a finite state machine
-- fsm2 = FSM.new(myStateTransitionTable2)
-- fsm2:set("state2")
-- print("\nCurrent FSM-2 state: " .. fsm2:get())

-- fsm2:delete({{"state2", "event2"}} )
-- -- Force exception
-- fsm2:fire("event2")

-- fsm2:delete({{"*", "?"}} )
-- print("Force third exception (silence = true)")
-- fsm2:silent() -- prevent unknown state-event notificaton to be printed

-- fsm2:fire("event3")
-- print("Current FSM-2 state after firing  wildcard 'event3': " .. fsm2:get())

-- fsm2:add({{"*"     , "*",      "state2", action3}})
-- fsm2:fire("event2")
-- print("Current FSM-2 state: " .. fsm2:get())
-- print("Current FSM state: " .. fsm:get())

--[[
Expected output:

Constant FSM.UNKNONW = *.*
Current FSM state: state1
Current FSM state: state2
Performing action 2
Current FSM state: state3
Force exception by firing unknown event
FSM: unknown combination: state3.event3
Current FSM state: state1

Current FSM-2 state: state2
FSM: unknown combination: state2.event2
Force third exception (silence = true)
Wildcard in action !!!
Current FSM-2 state after firing  wildcard 'event3': state1
Action 3: Exception raised
Current FSM-2 state: state2
Current FSM state: state1
--]]