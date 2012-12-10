

local string = require "string"
local oo = require "loop.base"

module("chrono.Date", oo.class)

day = 1
month = 1
year = 1900

function addyears(self, years)
  self.year = self.year + years
end

function __tostring(self)
  return string.format("%d/%d/%d",
                       self.month,
                       self.day,
                       self.year)
end

-- local SimpleDate = require "chrono.Date"
-- local mydate1 = SimpleDate()
-- mydate1:addyears(10)
-- print(mydate1.year)
