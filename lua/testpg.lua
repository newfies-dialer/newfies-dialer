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


require "luasql.postgres"
envv = assert (luasql.postgres())
con = assert (envv:connect('newfies2', 'newfiesuser', 'password', "127.0.0.1", 5432))

require "dumper"

-- Define a shortcut function for testing
function dump(...)
  print(DataDumper(...), "\n---")
end

dump(8)

dump({ { {} } },a,true) --> return {{{},},}

-- DROP ANY EXISTING PEOPLE TABLE
res = con:execute("DROP TABLE people")

-- RECREATE PEOPLE TABLE
res = assert (con:execute[[
	CREATE TABLE people(
		id integer,
		fname text,
		lname text,
		job text
	)
]])

-- ADD SOME PEOPLE TO THE PEOPLE TABLE
res = assert(con:execute("INSERT INTO people " ..
	"VALUES (1, 'Roberto', 'Ierusalimschy', 'Programmer')"))
res = assert(con:execute("INSERT INTO people " ..
	"VALUES (2, 'Barack', 'Obama', 'President')"))
res = assert(con:execute("INSERT INTO people " ..
	"VALUES (3, 'Taylor', 'Swift', 'Singer')"))
res = assert(con:execute("INSERT INTO people " ..
	"VALUES (4, 'Usain', 'Bolt', 'Sprinter')"))

-- RETRIEVE THE PEOPLE TABLE SORTED BY LAST NAME INTO CURSOR
cur = assert (con:execute"SELECT * from people order by lname")

-- LOOP THROUGH THE CURSOR AND PRINT
print()
print(string.format("%15s  %-15s %-15s %-15s",
	"#", "FNAME", "LNAME", "JOB"))
print(string.format("%15s  %-15s %-15s %-15s",
	"-", "-----", "-----", "---"))
row = cur:fetch ({}, "a")
while row do
	print(string.format("%15d  %-15s %-15s %-15s",
		row.id, row.fname, row.lname, row.job))
	row = cur:fetch (row, "a")
end
print()

-- CLOSE EVERYTHING
cur:close()
con:close()
envv:close()

