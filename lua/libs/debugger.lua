

package.path = package.path .. ";/home/areski/public_html/django/MyProjects/newfies-dialer/lua/?.lua";
package.path = package.path .. ";/home/areski/public_html/django/MyProjects/newfies-dialer/lua/libs/?.lua";

-- local oo = require "loop.base"
local oo = require "loop.simple"
require "logging.file"

local LOGDIR = '/home/areski/public_html/django/MyProjects/newfies-dialer/lua/'
local logger = logging.file(LOGDIR .. "logs_%s.log", "%Y-%m-%d")
logger:setLevel(logging.DEBUG)


Debugger = oo.class{
    -- default field values
    fs_env = nil,
    verbosity_level = 'INFO',
}

function Debugger:__init(verbosity_level, fs_env)
    -- self is the class
    return oo.rawnew(self, {
        verbosity_level = verbosity_level,
        fs_env = fs_env
    })
end


function Debugger:msg(level, message)
    -- level : INFO, NOTICE, ...
    if self.fs_env then
        freeswitch.consoleLog(level, message)
    else
        print(message)
    end
    logger:info(message)
end

