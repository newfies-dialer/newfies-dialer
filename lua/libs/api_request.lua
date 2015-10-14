--
-- Sample API HTTP Get request using Lua-cURL v3
--


local cURL = require "cURL"
local scurl = require "cURL.safe"


--
-- URL Encoder
--
function url_encode(str)
    if (str) then
        str = string.gsub (str, "\n", "\r\n")
        str = string.gsub (str, "([^%w ])",
        function (c) return string.format ("%%%02X", string.byte(c)) end)
        str = string.gsub (str, " ", "+")
    end
    return str
end


--
-- Decode Json and return false if the json have an error
--
function decodejson(jsondata)
    local json = require("json")
    cError, res = pcall(json.decode,jsondata)
    if not cError then
        return false
    end
    return res
end


--
-- Perform API Request
--
function api_request(api_url, params, timeout)
    local get_params = ''
    -- URLEncode the parameters
    for k, v in pairs(params) do
        if get_params ~= '' then
            get_params = get_params..'&'
        end
        local v_encoded = url_encode(v)
        if v_encoded then
            get_params = get_params..tostring(k)..'='..url_encode(v)
        end
    end
    if string.find(api_url, "?") then
        api_url = api_url.."&"..get_params
    else
        api_url = api_url.."?"..get_params
    end
    -- print("api_url => "..api_url)

    local buffer = ""
    c = scurl.easy()
        :setopt_url(api_url)
        :setopt(scurl.OPT_TIMEOUT, timeout)
        :setopt_ssl_verifypeer(0)
        :setopt_httpheader{
            "X-Lua-Curl: Newfies-Dialer backend",
        }
        :setopt_writefunction(function(str)
                                  buffer = buffer..str
                              end)
    local _, e = c:perform()
    if string.find(tostring(e), "[OPERATION_TIMEDOUT]") then
        return nil, "ERROR: OPERATION_TIMEDOUT"
    end

    c:close()

    -- Turn the JSON response string into a table
    jdata = decodejson(buffer)
    if jdata then
        -- Return the api_result field
        return jdata["api_result"], nil
    else
        return false, "ERROR_DECODEJSON"
    end
end



function test_api_request()

    -- tested with http://mockbin.org/
    -- nice to check https://httpbin.org/

    -- local api_url = "http://requestb.in/xxlxgzxx"
    local api_url = "http://mockbin.org/bin/e0be1bf7-a5d9-4239-9980-d8ce472fca57"
    -- local api_url = 'http://localhost:8001/sleep.php'
    local params = {
        onevar = "value1",
        twovar = "value2"
    }
    timeout = 1
    local api_result, err = api_request(api_url, params, timeout)
    print(api_result, err)

end