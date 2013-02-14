-- ==========================================================================================
--
-- Finite State Machine Class for Lua 5.1 & Corona SDK
-- 
-- Written by Erik Cornelisse, inspired by Luiz Henrique de Figueiredo
-- E-mail: e.cornelisse@gmail.com
-- 
-- Version 1.0  April 27, 2011
-- 
-- Class is MIT Licensed
-- Copyright (c) 2011 Erik Cornelisse
-- 
-- Feel free to change but please send new versions, improvements or 
-- new features to me and help us to make it better.
--
-- ==========================================================================================

--[[ A design pattern for doing finite state machines (FSMs) in Lua.

Based on a very appreciated contribution of Luiz Henrique de Figueiredo
Original code from http://lua-users.org/wiki/FiniteStateMachine

The FSM is described with: old_state, event, new_state and action.
One easy way to do this in Lua would be to create a table in exactly 
the form above:

yourStateTransitionTable = { 
	{state1, event1, state2, action1},
	{state1, event2, state3, action2},
	...
}

The function FSM takes the simple syntax above and creates tables 
for (state, event) pairs with fields (action, new):

function FSM(yourStateTransitionTable)
  local stt = {}
  for _,v in ipairs(t) do
    local old, event, new, action = v[1], v[2], v[3], v[4]
    if stt[old] == nil then a[old] = {} end
    stt[old][event] = {new = new, action = action}
  end
  return stt
end

Note that this scheme works for states and events of any type: number, 
string, functions, tables, anything. Such is the power of associate arrays.

However, the double array stt[old][event] caused a problem for event = nil
Instead a single array is used, constructed as stt[state .. SEPARATOR .. event]
Where SEPARATOR is a constant and defined as '.'

Three special state transitions are added to the original code:
- any state but a specific event
- any event but a specific state
- unknown state-event combination to be used for exception handling

The any state and event are defined by the ANY constant, defined as '*' 
The unknown state-event is defined as the combination of ANY.ANY (*.*)

A default exception handler for unknown state-event combinations is 
provided and therefore a specification a your own exception handling is
optional.

After creating a new FSM, the initial state is set to the first defined 
state in your state transition table. With add(t) and delete(t), new state
transition can be added and removed later. 

A DEBUG-like method called silent is included to prevent wise-guy remarks
about things you shouldn't be doing. 

USAGE EXAMPLES:
------------------------------------------------------------------------------- 
FSM = require "fsm"

function action1() print("Performing action 1") end
function action2() print("Performing action 2") end

-- Define your state transitions here
local myStateTransitionTable = {
	{"state1", "event1", "state2", action1},
	{"state2", "event2", "state3", action2},
	{"*",      "event3", "state2", action1},  -- for any state
	{"*", 	   "*",	     "state2", action2}   -- exception handler
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
fsm:fire("event2")
print("Current FSM state: " .. fsm:get())

Output:
-------
Current FSM state: state1
Current FSM state: state2
Performing action 2
Current FSM state: state3

REMARKS:
-------------------------------------------------------------------------------
Sub-states are not supported by additional methods to keep the code simple.
If you need sub-states, you can create them as 'state.substate' directly.

A specific remove method is not provided because I didn't need one (I think)
But feel free to implement one yourself :-)

One more thing, did I already mentioned that I am new to Lua?
Well, I learn a lot of other examples, so do not forget yours. 

CONCLUSION:
-------------------------------------------------------------------------------
A small amount of code is required to use the power of a Finite State Machine.

I wrote this code to implement generic graphical objects where the presentation 
and behaviour of the objects can be specified by using state-transition tables.
This resulted in less code (and less bugs), a higher modularity and above all a 
reduction of the complexity.

Finite state machines can be used to force (at least parts of) your code into 
deterministic behaviour. 

Have fun !!

--]]

--MODULE CODE
------------------------------------------------------------------------------- 
module(..., package.seeall)

-- FSM CONSTANTS --------------------------------------------------------------
SEPARATOR = '.'
ANY       = '*'
ANYSTATE  = ANY .. SEPARATOR
ANYEVENT  = SEPARATOR .. ANY
UNKNOWN   = ANYSTATE .. ANY

function new(t)
	
	local self = {}
	
	-- ATTRIBUTES -------------------------------------------------------------
	local state = t[1][1]	-- current state, default the first one
	local stt = {}			-- state transition table
	local str = ""			-- <state><SEPARATOR><event> combination
	local silence = false	-- use silent() for whisper mode
		
	-- METHODS ----------------------------------------------------------------	
	
	-- some getters and setters
	function self:set(s) state = s end
	function self:get() return state	end
	function self:silent() silence = true end

	-- default exception handling
	local function exception() 
		if silence == false then 
			print("FSM: unknown combination: " .. str) end
		return false
	end	
	
	-- respond based on current state and event
	function self:fire(event)
		local act = stt[state .. SEPARATOR .. event]
		-- raise exception for unknown state-event combination
		if act == nil then 
			-- search for wildcard "states" for this event
			act = stt[ANYSTATE .. event]
			-- if still not a match than check any event
			if act == nil then
				-- check if there is a wildcard event
				act = stt[state .. ANYEVENT]
				if act == nil then
					act = stt[UNKNOWN]; str = state .. SEPARATOR .. event end
			end
		end
		-- set next state as current state
		state = act.newState	
		
		return act.action()
	end

	-- add new state transitions to the FSM
	function self:add(t)
		for _,v in ipairs(t) do
			local oldState, event, newState, action = v[1], v[2], v[3], v[4]
			
			stt[oldState .. SEPARATOR .. event] = {newState = newState, action = action}
		end
		return #t	-- the requested number of state-transitions to be added 
	end
	
	-- remove state transitions from the FSM
	function self:delete(t)
		for _,v in ipairs(t) do
			local oldState, event = v[1], v[2]
			if oldState == ANY and event == ANY then
				if not silence then
					print( "FSM: you should not delete the exception handler" )
					print( "FSM: but assign another exception action" )
				end 
				-- assign default exception handler but stay in current state
				stt[exception] = {newState = state, action = exception}
			else
				stt[oldState .. SEPARATOR .. event] = nil
			end
		end
		return #t 	-- the requested number of state-transitions to be deleted
	end
	
	-- initalise state transition table
	stt[UNKNOWN] = {newState = state, action = exception}
	
	self:add(t)

	-- return FSM methods
	return self
end


