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
# wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-freeswitch.sh
#

FS_CONF_PATH=https://raw.github.com/Star2Billing/newfies-dialer/master/install/freeswitch-conf
FS_INIT_PATH=https://raw.github.com/Star2Billing/newfies-dialer/master/install/freeswitch-init
FS_INSTALLED_PATH=/usr/local/freeswitch
FS_CONFIG_PATH=/etc/freeswitch
FS_DOWNLOAD=http://files.freeswitch.org/freeswitch-1.2.5.tar.bz2
FS_BASE_PATH=/usr/src/
CURRENT_PATH=$PWD



clear
echo ""
echo "This Installer should be run on Ubuntu 12.04 TLS!"
echo ""
echo "FreeSWITCH will be installed in $FS_INSTALLED_PATH"
echo "Press Enter to continue or CTRL-C to exit"
echo ""
read INPUT

func_install_fs_source() {
    #install fs from source
    echo "Installing from source"

    #Add Freeswitch group and user
    grep -c "^freeswitch:" /etc/group &> /dev/null
    if [ $? = 1 ]; then
        /usr/sbin/groupadd -r -f freeswitch
    fi

    grep -c "^freeswitch:" /etc/passwd &> /dev/null
    if [ $? = 1 ]; then
        echo "adding user freeswitch..."
        /usr/sbin/useradd -r -c "freeswitch" -g freeswitch freeswitch
    fi

    # Install FreeSWITCH
    cd $FS_BASE_PATH
    rm -rf freeswitch
    rm -rf freeswitch-*.tar.*
    wget $FS_DOWNLOAD
    tar jxf freeswitch-*.tar.*
    rm freeswitch-*.tar.*
    mv freeswitch-* freeswitch

    cd $FS_BASE_PATH/freeswitch
    ./configure --without-pgsql --prefix=/usr/local/freeswitch --sysconfdir=/etc/freeswitch/
    #sh bootstrap.sh && ./configure --without-pgsql --prefix=/usr/local/freeswitch --sysconfdir=/etc/freeswitch/
    [ -f modules.conf ] && cp modules.conf modules.conf.bak
    sed -i -e \
    "s/#applications\/mod_curl/applications\/mod_curl/g" \
    -e "s/#asr_tts\/mod_flite/asr_tts\/mod_flite/g" \
    -e "s/#asr_tts\/mod_tts_commandline/asr_tts\/mod_tts_commandline/g" \
    -e "s/#formats\/mod_shout/formats\/mod_shout/g" \
    -e "s/#endpoints\/mod_dingaling/endpoints\/mod_dingaling/g" \
    -e "s/#formats\/mod_shell_stream/formats\/mod_shell_stream/g" \
    -e "s/#say\/mod_say_de/say\/mod_say_de/g" \
    -e "s/#say\/mod_say_es/say\/mod_say_es/g" \
    -e "s/#say\/mod_say_fr/say\/mod_say_fr/g" \
    -e "s/#say\/mod_say_it/say\/mod_say_it/g" \
    -e "s/#say\/mod_say_nl/say\/mod_say_nl/g" \
    -e "s/#say\/mod_say_ru/say\/mod_say_ru/g" \
    -e "s/#say\/mod_say_zh/say\/mod_say_zh/g" \
    -e "s/#say\/mod_say_hu/say\/mod_say_hu/g" \
    -e "s/#say\/mod_say_th/say\/mod_say_th/g" \
    -e "s/#xml_int\/mod_xml_cdr/xml_int\/mod_xml_cdr/g" \
    modules.conf
    make && make install && make sounds-install && make moh-install

    #Set permissions
    chown -R freeswitch:freeswitch /usr/local/freeswitch /etc/freeswitch
}


echo "Setting up Prerequisites and Dependencies for FreeSWITCH"
apt-get -y update
apt-get -y install autoconf automake autotools-dev binutils bison build-essential cpp curl flex g++ gcc git-core libaudiofile-dev libc6-dev libdb-dev libexpat1 libexpat1-dev libgdbm-dev libgnutls-dev libmcrypt-dev libncurses5-dev libnewt-dev libpcre3 libpopt-dev libsctp-dev libsqlite3-dev libtiff4 libtiff4-dev libtool libx11-dev libxml2 libxml2-dev lksctp-tools lynx m4 make mcrypt ncftp nmap openssl sox sqlite3 ssl-cert ssl-cert unixodbc-dev unzip zip zlib1g-dev zlib1g-dev
apt-get -y install libssl-dev pkg-config
apt-get -y install libvorbis0a libogg0 libogg-dev libvorbis-dev
apt-get -y install flite flite1-dev

#Install Freeswitch
func_install_fs_source

# Enable FreeSWITCH modules
cd $FS_CONFIG_PATH/autoload_configs/
[ -f modules.conf.xml ] && cp modules.conf.xml modules.conf.xml.bak
sed -i -r \
-e "s/<\!--\s?<load module=\"mod_lua\"\/>\s?-->/<load module=\"mod_lua\"\/>/g" \
-e "s/<\!--\s?<load module=\"mod_xml_curl\"\/>\s?-->/<load module=\"mod_xml_curl\"\/>/g" \
-e "s/<\!--\s?<load module=\"mod_xml_cdr\"\/>\s?-->/<load module=\"mod_xml_cdr\"\/>/g" \
-e "s/<\!--\s?<load module=\"mod_dingaling\"\/>\s?-->/<load module=\"mod_dingaling\"\/>/g" \
-e "s/<\!--\s?<load module=\"mod_shell_stream\"\/>\s?-->/<load module=\"mod_shell_stream\"\/>/g" \
-e "s/<\!-- \s?<load module=\"mod_shell_stream\"\/>\s? -->/<load module=\"mod_shell_stream\"\/>/g" \
-e "s/<\!--\s?<load module=\"mod_shout\"\/>\s?-->/<load module=\"mod_shout\"\/>/g" \
-e "s/<\!--\s?<load module=\"mod_tts_commandline\"\/>\s?-->/<load module=\"mod_tts_commandline\"\/>/g" \
-e "s/<\!--\s?<load module=\"mod_flite\"\/>\s?-->/<load module=\"mod_flite\"\/>/g" \
-e "s/<\!--\s?<load module=\"mod_say_ru\"\/>\s?-->/<load module=\"mod_say_ru\"\/>/g" \
-e "s/<\!--\s?<load module=\"mod_say_zh\"\/>\s?-->/<load module=\"mod_say_zh\"\/>/g" \
-e 's/mod_say_zh.*$/&\n    <load module="mod_say_de"\/>\n    <load module="mod_say_es"\/>\n    <load module="mod_say_fr"\/>\n    <load module="mod_say_it"\/>\n    <load module="mod_say_nl"\/>\n    <load module="mod_say_hu"\/>\n    <load module="mod_say_th"\/>/' \
modules.conf.xml

[ -f lua.conf.xml ] && mv lua.conf.xml lua.conf.xml.bak
wget --no-check-certificate $FS_CONF_PATH/lua.conf.xml -O lua.conf.xml

#Configure Dialplan
cd $FS_CONFIG_PATH/conf/dialplan/

# Place Plivo Default Dialplan in FreeSWITCH
[ -f default.xml ] && mv default.xml default.xml.bak
wget --no-check-certificate $FS_CONF_PATH/default.xml -O default.xml

# Place Plivo Public Dialplan in FreeSWITCH
[ -f public.xml ] && mv public.xml public.xml.bak
wget --no-check-certificate $FS_CONF_PATH/public.xml -O public.xml


#Configure XML CDR
#cd $FS_INSTALLED_PATH/conf/autoload_configs/

#this is commented as we don't use xml_cdr anymore
## Place Newfies XML CDR conf in FreeSWITCH
#[ -f xml_cdr.conf.xml ] && mv xml_cdr.conf.xml xml_cdr.conf.xml.bak
#wget --no-check-certificate $FS_CONF_PATH/xml_cdr.conf.xml -O xml_cdr.conf.xml
#create dir to store send error of CDR
#mkdir /usr/local/freeswitch/log/err_xml_cdr/

#Return to current path
cd $CURRENT_PATH
#Install init.d script
wget --no-check-certificate $FS_INIT_PATH/debian/freeswitch -O /etc/init.d/freeswitch
chmod 0755 /etc/init.d/freeswitch
cd /etc/init.d; update-rc.d freeswitch defaults 90

echo "installing from source"
#Add alias fs_cli
chk=`grep "fs_cli" ~/.bashrc|wc -l`
if [ $chk -lt 1 ] ; then
    echo "alias fs_cli='/usr/local/freeswitch/bin/fs_cli'" >> ~/.bashrc
fi

# Install Complete
echo ""
echo "********************************************************************"
echo "Congratulations, FreeSWITCH is now installed at '$FS_INSTALLED_PATH'"
echo "********************************************************************"
echo
echo "* To Start FreeSWITCH in foreground :"
echo "    '$FS_INSTALLED_PATH/bin/freeswitch'"
echo
echo "* To Start FreeSWITCH in background :"
echo "    '$FS_INSTALLED_PATH/bin/freeswitch -nc'"
echo
echo "********************************************************************"
echo ""
