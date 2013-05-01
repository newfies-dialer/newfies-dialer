#!/bin/bash
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

#
# To download and run the script on your server :
# cd /usr/src/ ; rm install-all.sh ; wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-all.sh ; chmod +x install-all.sh ; ./install-all.sh
#

BRANCH='develop'

# Identify Linux Distribution type
func_identify_os() {
    if [ -f /etc/debian_version ] ; then
        DIST='DEBIAN'
        if [ "$(lsb_release -cs)" != "precise" ]; then
            echo "This script is only intended to run on Ubuntu LTS 12.04 or CentOS 6.X"
            exit 255
        fi
    elif [ -f /etc/redhat-release ] ; then
        DIST='CENTOS'
        if [ "$(awk '{print $3}' /etc/redhat-release)" != "6.2" ] && [ "$(awk '{print $3}' /etc/redhat-release)" != "6.3" ] && [ "$(awk '{print $3}' /etc/redhat-release)" != "6.4" ] ; then
            echo "This script is only intended to run on Ubuntu LTS 12.04 or CentOS 6.X"
            exit 255
        fi
    else
        echo "This script is only intended to run on Ubuntu LTS 12.04 or CentOS 6.X"
        exit 1
    fi
}

#install the epel repository.
func_install_epel_repo() {

	if [ ! -f /etc/yum.repos.d/epel.repo ];
		then
			echo '
[epel]
name=Extra Packages for Enterprise Linux 6 - $basearch
#baseurl=http://download.fedoraproject.org/pub/epel/6/$basearch
mirrorlist=https://mirrors.fedoraproject.org/metalink?repo=epel-6&arch=$basearch
failovermethod=priority
enabled=0
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-6
		' > /etc/yum.repos.d/epel.repo
	fi
}

#install the rpmforge repository.
func_install_rpmforge_repo() {

	if [ ! -f /etc/yum.repos.d/rpmforge.repo ];
		then
			echo '
[rpmforge]
name = RHEL $releasever - RPMforge.net - dag
baseurl = http://apt.sw.be/redhat/el6/en/$basearch/rpmforge
mirrorlist = http://apt.sw.be/redhat/el6/en/mirrors-rpmforge
#mirrorlist = file:///etc/yum.repos.d/mirrors-rpmforge
enabled = 0
protect = 0
gpgkey = file:///etc/pki/rpm-gpg/RPM-GPG-KEY-rpmforge-dag
gpgcheck = 0
		' > /etc/yum.repos.d/rpmforge.repo
	fi
}




#Identify the OS
func_identify_os

echo ""
echo "> > > This is only to be installed on a fresh new installation of CentOS 6.X or Ubuntu 12.04 TLS! < < <"
echo ""
echo "It will install Newfies-Dialer and Freeswitch on your server"
echo "Press Enter to continue or CTRL-C to exit"
echo ""
read TEMP





case $DIST in
    'DEBIAN')
        apt-get -y update
        apt-get -y install vim git-core
    ;;
    'CENTOS')
		func_install_epel_repo
		func_install_rpmforge_repo
        yum -y update
        yum -y install mlocate vim git wget
        yum -y install policycoreutils-python
    ;;
esac



#Install Freeswitch
cd /usr/src/
wget --no-check-certificate  https://raw.github.com/Star2Billing/newfies-dialer/$BRANCH/install/install-freeswitch.sh -O install-freeswitch.sh
bash install-freeswitch.sh
/etc/init.d/freeswitch start

#Install Newfies
cd /usr/src/
wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/$BRANCH/install/install-newfies.sh -O install-newfies.sh
bash install-newfies.sh

