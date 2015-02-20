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


freeswitch.consoleLog("INFO", "SECTION    " .. XML_REQUEST["section"] .. "\n")
freeswitch.consoleLog("INFO", "TAG_NAME   " .. XML_REQUEST["tag_name"] .. "\n")
freeswitch.consoleLog("INFO", "KEY_NAME   " .. XML_REQUEST["key_name"] .. "\n")
freeswitch.consoleLog("INFO", "KEY_VALUE  " .. XML_REQUEST["key_value"] .. "\n")



-- params is the event passed into us we can use params:getHeader to grab things we want.
--io.write("TEST\n" .. params:serialize("xml") .. "\n");

mydialplan = [[
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
  <section name="dialplan" description="RE Dial Plan For FreeSwitch">
    <context name="default">
      <extension name="freeswitch_public_conf_via_sip">
        <condition field="destination_number" expression="^9(888|1616)$">
          <action application="bridge" data="sofia/${use_profile}/$1@conference.freeswitch.org"/>
        </condition>
      </extension>
    </context>
  </section>
</document>
]]

--XML_STRING = mydialplan

callcenter = [[
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
  <section name="configuration" description="Callcenter For FreeSwitch">


    <configuration name="callcenter.conf" description="CallCenter">
      <settings>
        <param name="odbc-dsn" value="odbc://freeswitch"/>
      </settings>

      <queues>
        <queue name="mysupport@default">
          <param name="strategy" value="longest-idle-agent"/>
          <param name="moh-sound" value="$${hold_music}"/>
          <!--<param name="record-template" value="$${base_dir}/recordings/${strftime(%Y-%m-%d-%H-%M-%S)}.${destination_number}.${caller_id_number}.${uuid}.wav"/>-->
          <param name="time-base-score" value="system"/>
          <param name="max-wait-time" value="0"/>
          <param name="max-wait-time-with-no-agent" value="0"/>
          <param name="max-wait-time-with-no-agent-time-reached" value="5"/>
          <param name="tier-rules-apply" value="false"/>
          <param name="tier-rule-wait-second" value="300"/>
          <param name="tier-rule-wait-multiply-level" value="true"/>
          <param name="tier-rule-no-agent-no-wait" value="false"/>
          <param name="discard-abandoned-after" value="60"/>
          <param name="abandoned-resume-allowed" value="false"/>
        </queue>
        <queue name="mysupport55@default">
          <param name="strategy" value="longest-idle-agent"/>
          <param name="moh-sound" value="$${hold_music}"/>
          <!--<param name="record-template" value="$${base_dir}/recordings/${strftime(%Y-%m-%d-%H-%M-%S)}.${destination_number}.${caller_id_number}.${uuid}.wav"/>-->
          <param name="time-base-score" value="system"/>
          <param name="max-wait-time" value="0"/>
          <param name="max-wait-time-with-no-agent" value="0"/>
          <param name="max-wait-time-with-no-agent-time-reached" value="5"/>
          <param name="tier-rules-apply" value="false"/>
          <param name="tier-rule-wait-second" value="300"/>
          <param name="tier-rule-wait-multiply-level" value="true"/>
          <param name="tier-rule-no-agent-no-wait" value="false"/>
          <param name="discard-abandoned-after" value="60"/>
          <param name="abandoned-resume-allowed" value="false"/>
        </queue>
      </queues>

      <agents>
        <agent name="areski@default" type="callback" contact="[call_timeout=10]user/areski@$${domain}" status="Logged Out" max-no-answer="3" wrap-up-time="10" reject-delay-time="10" busy-delay-time="60" />
        <agent name="kiki@default" type="callback" contact="[call_timeout=10]user/areski@$${domain}" status="Logged Out" max-no-answer="3" wrap-up-time="10" reject-delay-time="10" busy-delay-time="60" />
        <agent name="moya@default" type="callback" contact="[call_timeout=10]user/areski@$${domain}" status="Logged Out" max-no-answer="3" wrap-up-time="10" reject-delay-time="10" busy-delay-time="60" />
      </agents>

      <tiers>
        <!-- If no level or position is provided, they will default to 1.  You should do this to keep db value on restart. -->
        <!-- <tier agent="1000@default" queue="support@default" level="1" position="1"/> -->
        <tier agent="areski@default" queue="mysupport@default" level="1" position="1"/>
      </tiers>

    </configuration>


  </section>
</document>
]]

XML_STRING = callcenter