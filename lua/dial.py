#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#


import ESL
c = ESL.ESLconnection("localhost", "8021", "ClueCon")
c.connected()


# {ignore_early_media=true,continue_on_fail=true,bypass_media=false,hangup_after_bridge=true,originate_timeout=10,api_hangup_hook='luarun hangup.lua ${uuid}'}sofia/gateway/phoneno &park()

#origination_caller_id_number=8888888888,origination_caller_id_name=8888888888,effective_caller_id_name=8888888888,effective_caller_id_number=8888888888,caller_id_number=8888888888


dial = "originate {bridge_early_media=true,hangup_after_bridge=true,originate_timeout=10,newfiesdialer=true,used_gateway_id=1,callrequest_id=26,leg_type=1}user/areski &playback(/tmp/myfile.wav)"
# originate {bridge_early_media=true,hangup_after_bridge=true,originate_timeout=10}user/areski &playback(/tmp/myfile.wav)
ev = c.api("bgapi", dial)
print ev.serialize()
