//
// Newfies-Dialer License
// http://www.newfies-dialer.org
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this file,
// You can obtain one at http://mozilla.org/MPL/2.0/.
//
// Copyright (C) 2011-2012 Star2Billing S.L.
//
// The Initial Developer of the Original Code is
// Arezqui Belaid <info@star2billing.com>
//

// Add <load module="mod_spidermonkey_curl"/> in spidermonkey.conf.xml
// jsrun /path/callback.js
// 
//     
//    <extension name="callback">
//      <condition field="destination_number" expression="^1111$">
//        <action application="javascript" data="/path/callback.js" /> 
//      </condition>
//    </extension>
//

use("CURL");

function logger(logstuff, loglevel) {
    console_log(loglevel, logstuff + "\n");
}

function my_callback(string, arg)
{
    //logger(string, "info");
    return true;
}

// Country from where the callback is requested
country_prefix = '44'

if (session.ready()) {
    session.preAnswer();
    var curl = new CURL();
    cidnum = session.caller_id_number; 
    logger("caller id is " + session.caller_id_number, "info");
    cidnum = country_prefix + cidnum.substring(1);
    curl.run("POST", "http://serverIP:8008/api/v1/campaignsubscriber/", "contact=" + cidnum + "&last_name=callback&phonebook_id=1", my_callback, "my arg\n", "test:test");
    session.hangup();
}

