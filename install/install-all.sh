#!/bin/bash
#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

#
# To download and run the script on your server :
# cd /usr/src/ ; rm install-all.sh ; wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-all.sh ; chmod +x install-all.sh ; ./install-all.sh
#
# BRANCH = develop
# cd /usr/src/ ; rm install-all.sh ; wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/develop/install/install-all.sh ; chmod +x install-all.sh ; ./install-all.sh
#

#Set branch to install develop / master
BRANCH='develop'

SCRIPT_NOTICE="This script is only intended to run on Debian 7.X"

# Identify Linux Distribution type
func_identify_os() {
    if [ -f /etc/debian_version ] ; then
        DIST='DEBIAN'
        apt-get -y install lsb-release
        if [ "$(lsb_release -cs)" != "wheezy" ] && [ "$(lsb_release -cs)" != "jessie" ]; then
            echo $SCRIPT_NOTICE
            exit 255
        fi
        DEBIANCODE=$(lsb_release -cs)
    elif [ -f /etc/redhat-release ] ; then
        DIST='CENTOS'
        if [ "$(awk '{print $3}' /etc/redhat-release)" != "6.2" ] && [ "$(awk '{print $3}' /etc/redhat-release)" != "6.3" ] && [ "$(awk '{print $3}' /etc/redhat-release)" != "6.4" ] && [ "$(awk '{print $3}' /etc/redhat-release)" != "6.5" ]; then
            echo $SCRIPT_NOTICE
            exit 255
        fi
    else
        echo $SCRIPT_NOTICE
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
echo "> > > This is only to be installed on a fresh new installation of Debian 7.X or CentOS 6.X! < < <"
echo ""
echo "It will install Newfies-Dialer and Freeswitch on your server"
echo ""
echo ""
echo ""

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
