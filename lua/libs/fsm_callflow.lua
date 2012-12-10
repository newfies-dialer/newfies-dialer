--
-- Newfies-Dialer License
-- http://www.newfies-dialer.org
--
-- This Source Code Form is subject to the terms of the Mozilla Public
-- License, v. 2.0. If a copy of the MPL was not distributed with this file,
-- You can obtain one at http://mozilla.org/MPL/2.0/.
--
-- Copyright (C) 2011-2012 Star2Billing S.L.
--
-- The Initial Developer of the Original Code is
-- Arezqui Belaid <info@star2billing.com>
--


package.path = package.path .. ";/home/areski/public_html/django/MyProjects/newfies-dialer/lua/?.lua";
package.path = package.path .. ";/home/areski/public_html/django/MyProjects/newfies-dialer/lua/libs/?.lua";

local dumper = require "dumper"
local oo = require "loop.simple"


FSMCall = oo.class{
    -- default field values
    list_section = nil,
    list_branch = nil,
}

function FSMCall:__init(timecache)
    -- self is the class
    return oo.rawnew(self, {
        timecache   = timecache
    })
end


function FSMCall:init_call()
    extension_list = session:getVariable("extension_list")
    caller_id_name = session:getVariable("caller_id_name")
    caller_id_number = session:getVariable("caller_id_number")
    destination_number = session:getVariable("destination_number")
    uuid = session:getVariable("uuid")
end

function FSMCall:end_call()

end

function FSMCall:start_call()

end
