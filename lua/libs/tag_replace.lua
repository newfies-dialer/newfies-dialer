--
-- Newfies-Dialer License
-- http://www.newfies-dialer.org
--
-- This Source Code Form is subject to the terms of the Mozilla Public
-- License, v. 2.0. If a copy of the MPL was not distributed with this file,
-- You can obtain one at http://mozilla.org/MPL/2.0/.
--
-- Copyright (C) 2011-2015 Star2Billing S.L.
--
-- The primary maintainer of this project is
-- Arezqui Belaid <info@star2billing.com>
--


function mtable_jsoncontact(contact)
    --decode json from additional_vars
    if contact['additional_vars'] then
        decdata = decodejson(contact['additional_vars'])
        if decdata and type(decdata) == "table" then
            -- Merge Table
            mcontact = table_merge(contact, decdata)
        else
            mcontact = contact
        end
    else
        mcontact = contact
    end
    return mcontact
end

--
-- Function  Replace place holders by tag value.
--     This function will replace all the following tags :
--         {last_name}
--         {first_name}
--         {email}
--         {country}
--         {city}
--         {contact}
--     as well as, get additional_vars, and replace json tags
--
function tag_replace(text, contact)
    --if no text return empty string
    if not text or text == '' then
        return ''
    end
    --check if we got tag {__} in the text
    if not string.find(text, "[{|}]") then
        return text
    end
    --get merged table of contact with the json additional_vars
    mcontact = mtable_jsoncontact(contact)

    if not type(mcontact) == "table" then
        return text
    end

    for k, v in pairs(mcontact) do
        if k == 'contact' or k == 'Phone1' or k == 'Phone2' or k == 'Phone3' then
            newv = ''
            for i = 1, string.len(v) do
                newv = newv..string.sub(v, i, i)..' '
            end
            text = string.gsub(text, '{'..k..'}', newv)
        elseif string.sub(k, -3) ~= '_id' then
            text = string.gsub(text, '{'..k..'}', v)
        end
    end
    -- with .- you match the smallest expression
    text = string.gsub(text, '{.-}', '')
    return text
end

--
-- Merge table
--
function table_merge(t1, t2)
    for k,v in pairs(t2) do
        if type(v) == "table" then
            if type(t1[k] or false) == "table" then
                table_merge(t1[k] or {}, t2[k] or {})
            else
                t1[k] = v
            end
        else
            t1[k] = v
        end
    end
    return t1
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
-- Test
--
if false then

    local inspect = require "inspect"

    text = "Hello there {first_name}, your city is {city} and your age is {age}, your number is {contact}"

    contact = {
      additional_vars = '{"country": "canada", "age": "32", "city":"barcelona"}',
      campaign_id = "38",
      city = "",
      contact = "32132123123",
    }

    print(inspect(contact))

    ntext = tag_replace(text, contact)
    print("\nReplaced Text : "..ntext)

    print("\nend")
end
