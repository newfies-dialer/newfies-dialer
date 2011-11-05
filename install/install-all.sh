#!/bin/bash
#   Installation script for Newfies
#   Copyright (C) <2011>  <Star2Billing S.L> 
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# To download this script to your server,
#
# cd /usr/src/ ; rm install-all.sh ; wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-all.sh ; chmod +x install-all.sh ; ./install-all.sh
#
#------------------------------------------------------------------------------------


# Identify Linux Distribution type
if [ -f /etc/debian_version ] ; then
    DIST='DEBIAN'
elif [ -f /etc/redhat-release ] ; then
    DIST='CENTOS'
else
    echo ""
    echo "This Installer should be run on a CentOS or a Debian based system"
    echo ""
    exit 1
fi


echo ""
echo ""
echo "> > > This is only to be installed on a fresh new installation of CentOS, Debian or Ubuntu! < < <"
echo ""
echo "It will install Freeswitch, Plivo & Newfies on your server"
echo "Press Enter to continue or CTRL-C to exit"
echo ""
read TEMP


case $DIST in
    'DEBIAN')
        #Update repositories
        apt-get update
    ;;
esac


cd /usr/src/

#Download Scripts
wget https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-freeswitch.sh
wget https://raw.github.com/plivo/plivo/master/scripts/plivo_install_beta.sh
wget https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-newfies.sh

#Run the Install Scripts
bash install-freeswitch.sh
bash plivo_install_beta.sh /usr/share/plivo
bash install-newfies.sh




