#!/bin/bash
#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

#
# To download and run the script on your server :
# cd /usr/src/ ; rm install-all.sh ; wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/develop/install/install-all.sh ; chmod +x install-all.sh ; ./install-all.sh
#

BRANCH='develop'

# Identify Linux Distribution type
func_identify_os() {

    if [ -f /etc/debian_version ] ; then
        if [ "$(lsb_release -cs)" != "precise" ]; then
            echo "This script is only intended to run on Ubuntu 12.04 TLS"
            exit 1
        fi
    else
        echo ""
        echo "This script is only intended to run on Ubuntu 12.04 TLS"
        echo ""
        exit 1
    fi
}

#Identify the OS
func_identify_os

echo ""
echo "> > > This is only to be installed on a fresh new installation of Ubuntu 12.04 TLS! < < <"
echo ""
echo "It will install Newfies-Dialer and Freeswitch on your server"
echo "Press Enter to continue or CTRL-C to exit"
echo ""
read TEMP


apt-get -y update
apt-get -y install vim git-core

#Install Freeswitch
cd /usr/src/
wget https://raw.github.com/Star2Billing/newfies-dialer/$BRANCH/install/install-freeswitch.sh -O install-freeswitch.sh
bash install-freeswitch.sh
/etc/init.d/freeswitch start


# #Install Plivo
# cd /usr/src/
# wget https://raw.github.com/plivo/plivoframework/master/scripts/plivo_install.sh -O plivo_install.sh
# bash plivo_install.sh /usr/share/plivo

# #UPDATE Plivo configuration
# awk 'NR==12{print "EXTRA_FS_VARS = variable_user_context,Channel-Read-Codec-Bit-Rate,variable_plivo_answer_url,variable_plivo_app,variable_direction,variable_endpoint_disposition,variable_hangup_cause,variable_hangup_cause_q850,variable_duration,variable_billsec,variable_progresssec,variable_answersec,variable_waitsec,variable_mduration,variable_billmsec,variable_progressmsec,variable_answermsec,variable_waitmsec,variable_progress_mediamsec,variable_call_uuid,variable_origination_caller_id_number,variable_caller_id,variable_answer_epoch,variable_answer_uepoch"}1' /usr/share/plivo/etc/plivo/default.conf > /tmp/default.conf
# mv /tmp/default.conf /usr/share/plivo/etc/plivo/default.conf

# #Stop/Start Plivo & Cache Server
# /etc/init.d/plivo stop
# /etc/init.d/plivocache stop
# /etc/init.d/plivo start
# /etc/init.d/plivocache start

# echo "Install Logrotate..."
# #Setup log rotation
# touch /etc/logrotate.d/plivo
# echo '
# /usr/share/plivo/tmp/*.log {
#     daily
#     rotate 10
#     size = 20M
#     missingok
#     compress
# }
# '  >> /etc/logrotate.d/plivo

#Install Newfies
cd /usr/src/
wget https://raw.github.com/Star2Billing/newfies-dialer/develop/install/install-newfies.sh -O install-newfies.sh
bash install-newfies.sh
