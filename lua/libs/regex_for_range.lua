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

local inspect = require 'inspect'

-- range(a) returns an iterator from 1 to a (step = 1)
-- range(a, b) returns an iterator from a to b (step = 1)
-- range(a, b, step) returns an iterator from a to b, counting by step.
function range(a, b, step)
  if not b then
    b = a
    a = 1
  end
  step = step or 1
  local f =
    step > 0 and
      function(_, lastvalue)
        local nextvalue = lastvalue + step
        if nextvalue <= b then return nextvalue end
      end or
    step < 0 and
      function(_, lastvalue)
        local nextvalue = lastvalue + step
        if nextvalue >= b then return nextvalue end
      end or
      function(_, lastvalue) return lastvalue end
  return f, nil, a - step
end


function naive_range(min,max)
    -- Simply matches min, to max digits by position.  Should create a
    -- valid regex when min and max have same num digits and has same 10s
    -- place digit.
    _min,_max = tostring(min),tostring(max)
    pattern = ''
    for i in range(string.len(_min)) do
        if string.sub(_min, i, i) == string.sub(_max, i, i) then
            pattern = pattern..string.sub(_min, i, i)
        else
            pattern = pattern..'['..string.sub(_min, i, i)..'-'..string.sub(_max, i, i)..']'
        end
    end
    return tostring(pattern)
end

--create a function to return a floor to the correct digit position
--e.g., floor_digit_n(1336) => 1300 when increment is 100
function floor_digit_n(x, increment)
    return math.floor(x / increment) * increment
end

-- multiple of a string
-- mult('a', 5) -> aaaaa
function mult_str(str, x)
    res_str = ''
    for i in range(x) do
        res_str = res_str..str
    end
    return res_str
end

function regex_for_range(min,max)
    -- A recursive function to generate a regular expression that matches
    -- any number in the range between min and max inclusive.
    -- >>> regex_for_range(13,57)
    -- '4[0-9]|3[0-9]|2[0-9]|1[3-9]|5[0-7]'
    -- >>> regex_for_range(1983,2011)
    -- '200[0-9]|199[0-9]|198[3-9]|201[0-1]'
    -- >>> regex_for_range(99,112)
    -- '99|10[0-9]|11[0-2]'

    _min,_max = tostring(min),tostring(max)
    local patterns = {}
    print(min, max)
    -- calculations
    if min == max then
        return max
    end
    if string.len(_max) > string.len(_min) then
        -- more digits in max than min, so we pair it down into sub ranges
        -- that are the same number of digits.  If applicable we also create a pattern to
        -- cover the cases of values with number of digits in between that of
        -- max and min.
        re_middle_range = nil
        if (string.len(_max) > string.len(_min) + 2) then
            --digits more than 2 off, create mid range
            re_middle_range = '[0-9]{'..tostring(string.len(_min) + 1)..','..tostring(string.len(_max) - 1)..'}'
        elseif (string.len(_max) > string.len(_min) + 1) then
            --digits more than 1 off, create mid range
            re_middle_range = '[0-9]{'..tostring(string.len(_min) + 1)..'}'
        end
        --pair off into sub ranges
        max_big = max
        min_big = tonumber('1'..mult_str('0', string.len(_max)-1))
        re_big = regex_for_range(min_big, max_big)
        max_small = tonumber(mult_str('9', string.len(_min)-1))
        min_small = min
        digits=io.read()
        re_small = regex_for_range(min_small, max_small)
        if re_middle_range then
            return table.concat({re_small, re_middle_range, re_big}, "|")
        else
            return table.concat({re_small, re_big}, "|")
        end
    elseif string.len(_max)==string.len(_min) then

        if string.len(_max)==1 then
            patterns={naive_range(min,max)}
        else
            --this is probably the trickiest part so we'll follow the example of
            --1336 to 1821 through this section
            distance = tostring(max - min) --e.g., distance = 1821-1336 = 485
            increment = tonumber('1'..mult_str('0',string.len(distance) - 1)) --e.g., 100 when distance is 485

            if increment == 1 then
                --it's safe to do a naive_range see, see def since 10's place is the same for min and max
                patterns = {naive_range(min,max)}
            else
                --capture a safe middle range
                --e.g., create regex patterns to cover range between 1400 to 1800 inclusive
                --so in example we should get: 14[0-9]{2}|15[0-9]{2}|16[0-9]{2}|17[0-9]{2}
                for i in range(floor_digit_n(max,increment) - increment,floor_digit_n(min,increment),-increment) do
                    len_end_to_replace = string.len(tostring(increment))
                    print(len_end_to_replace)
                    print(tostring(i), -len_end_to_replace)
                    pattern_suf = string.sub(tostring(i), 0, -len_end_to_replace)
                    print("pattern_suf:"..pattern_suf)
                    if (len_end_to_replace - 1)==1 then
                        pattern = pattern_suf..'[0-9]'
                    else
                        pattern = pattern_suf..'[0-9]{'..len_end_to_replace..'}'
                    end
                    table.insert(patterns, pattern)
                    print(inspect(patterns))
                end
                --split off ranges outside of increment digits, i.e., what isn't covered in last step.
                --low side: e.g., 1336 -> min=1336, max=1300+(100-1) = 1399
                new_pattern = regex_for_range(min, floor_digit_n(min,increment)+(increment-1))
                print(inspect(new_pattern))
                table.insert(patterns, new_pattern)
                --high side: e.g., 1821 -> min=1800 max=1821
                new_pattern = regex_for_range(floor_digit_n(max,increment),max)
                print(inspect(new_pattern))
                table.insert(patterns, regex_for_range(floor_digit_n(max,increment),max))
            end
        end
        print(inspect(patterns))
        return table.concat(patterns, "|")
    else
        return('max value must have more or the same num digits as min')
    end
end


--
-- Test
rating_laps = '955'

print(regex_for_range(99, 112))
