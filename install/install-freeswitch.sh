#!/bin/bash
#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

#
# To download and run the script on your server :
# cd /usr/src/ ; rm install-freeswitch.sh ; wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-freeswitch.sh ; chmod +x install-freeswitch.sh ; ./install-freeswitch.sh
#

#Set branch to install develop / master
BRANCH='master'

FS_CONF_PATH=https://raw.github.com/Star2Billing/newfies-dialer/$BRANCH/install/freeswitch-conf
FS_INIT_PATH=https://raw.github.com/Star2Billing/newfies-dialer/$BRANCH/install/freeswitch-init
FS_CONFIG_PATH=/etc/freeswitch
FS_BASE_PATH=/usr/src/
CURRENT_PATH=$PWD
KERNELARCH=$(uname -p)
# Valid Freeswitch versions are : v1.2.stable
#FS_VERSION=v1.2.stable
FS_VERSION=v1.4


# Identify Linux Distribution type
if [ -f /etc/debian_version ] ; then
    DIST='DEBIAN'
elif [ -f /etc/redhat-release ] ; then
    DIST='CENTOS'
else
    echo "\n\nThis Installer should be run on a Debian 7.X or CentOS 6.X"
    exit 1
fi

clear
echo ""
echo "FreeSWITCH will be installed!"
echo ""
echo "Press Enter to continue or CTRL-C to exit"
echo ""
read INPUT


# -- Functions --

func_install_deps() {
    echo "Setting up Prerequisites and Dependencies for FreeSWITCH"
    case $DIST in
        'DEBIAN')
            #Get Kernel Arch on Debian if reported as unknown.
            if [ $KERNELARCH = "unknown" ]; then
                DEBIANARCH=$(dpkg --print-architecture)
                if [[ $DEBIANARCH = "amd64" ]]; then
                    KERNELARCH=x86_64
                fi
            else
                clear
                echo "we cannot confirm your kernel architecture"
                echo "enter 32 or 64"
                read INPUTARCH
                if [[ $INPUTARCH != "32" ]]; then
                    KERNELARCH=x86_64
                else
                    KERNELARCH=i386
                fi
            fi

            apt-get -y update
            apt-get -y install locales-all

            export LANGUAGE=en_US.UTF-8
            export LANG=en_US.UTF-8
            export LC_ALL=en_US.UTF-8
            locale-gen en_US.UTF-8
            locale-gen es_ES.UTF-8
            locale-gen fr_FR.UTF-8
            locale-gen pt_BR.UTF-8

            apt-get -y install autoconf2.64 automake autotools-dev binutils bison build-essential cpp curl flex g++ gcc git-core libaudiofile-dev libc6-dev libdb-dev libexpat1 libexpat1-dev libgdbm-dev libgnutls-dev libmcrypt-dev libncurses5-dev libnewt-dev libpcre3 libpcre3-dev libpopt-dev libsctp-dev libsqlite3-dev libtiff4 libtiff4-dev libtool libx11-dev libxml2 libxml2-dev lksctp-tools lynx m4 make mcrypt ncftp nmap openssl sox sqlite3 ssl-cert ssl-cert unzip zip zlib1g-dev zlib1g-dev
            apt-get -y install libssl-dev pkg-config
            apt-get -y install libvorbis0a libogg0 libogg-dev libvorbis-dev
            apt-get -y install flite flite1-dev
            apt-get -y install unixodbc-dev odbc-postgresql
            apt-get -y install libldns-dev libspeexdsp-dev libpcre3-dev libedit-dev libcurl4-openssl-dev libpcre3-dev
            ;;
        'CENTOS')
            yum -y update
            yum -y install autoconf automake bzip2 cpio curl curl-devel curl-devel expat-devel fileutils gcc-c++ gettext-devel gnutls-devel libjpeg-devel libogg-devel libtiff-devel libtool libvorbis-devel make ncurses-devel nmap openssl openssl-devel openssl-devel perl patch unixODBC unixODBC-devel unzip wget zip zlib zlib-devel
            yum -y install git
            yum -y install --enablerepo=epel flite flite-devel
        ;;
    esac
}

func_install_fs_sources() {
    echo "Installing from sources"

    #install Dependencies
    func_install_deps

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

    #Download and install FS from git repository.
    cd $FS_BASE_PATH
    rm -rf freeswitch
    # dont use depth :  --depth=1 as we wont be able to checkout
    git clone git://git.freeswitch.org/freeswitch.git
    cd $FS_BASE_PATH/freeswitch
    git checkout $FS_VERSION

    ./bootstrap.sh

    # !!! virtual memory exhausted: Cannot allocate memory !!!
    # we need to make more temporary swap space
    #
    # dd if=/dev/zero of=/root/fakeswap bs=1024 count=1048576
    # mkswap /root/fakeswap
    # swapon /root/fakeswap

    ./configure --without-pgsql --prefix=/usr/local/freeswitch --sysconfdir=/etc/freeswitch/
    [ -f modules.conf ] && cp modules.conf modules.conf.bak
    sed -i -e \
    "s/#applications\/mod_curl/applications\/mod_curl/g" \
    -e "s/#applications\/mod_avmd/applications\/mod_avmd/g" \
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

    # Remove temporary swap
    # swapoff /root/fakeswap
    # rm /root/fakeswap

    #Set permissions
    chown -R freeswitch:freeswitch /usr/local/freeswitch /etc/freeswitch
}

install_fs_deb_packages() {
    #for 1.2 Stable Branch
    echo 'deb http://files.freeswitch.org/repo/deb/debian/ wheezy main' >> /etc/apt/sources.list.d/freeswitch.list

    curl http://files.freeswitch.org/repo/deb/debian/freeswitch_archive_g0.pub | apt-key add -

    #install Dependencies
    func_install_deps

    apt-get -y install freeswitch-meta-vanilla
    apt-get -y install freeswitch-mod-vmd freeswitch-mod-python freeswitch-mod-sndfile freeswitch-sounds-en
    apt-get -y install libfreeswitch-dev freeswitch-mod-lua freeswitch-mod-flite
    apt-get -y install freeswitch-mod-esl freeswitch-mod-event-socket freeswitch-mod-curl
}

func_install_luasql() {
    #Install Dependencies
    apt-get install -y lua5.2 liblua5.2-dev
    apt-get install -y libpq-dev

    #Install LuaSQL
    cd /usr/src/
    wget https://github.com/keplerproject/luasql/archive/v2.3.0.zip
    unzip v2.3.0.zip
    cd luasql-2.3.0/

    #Copy a config file adapted for 64bit
    cp config config.orig
    rm config
    wget https://gist.githubusercontent.com/areski/4b82058ddf84e9d6f1e5/raw/5fae61dd851960b7063b82581b1b4904ba9413df/luasql_config -O config
    if [ $KERNELARCH != "x86_64" ]; then
        sed -i "s/64//g" config
    fi
    #Compile and install
    make
    make install
}

func_configure_fs() {
    echo "Enable FreeSWITCH modules"
    cd $FS_CONFIG_PATH/autoload_configs/
    [ -f modules.conf.xml ] && cp modules.conf.xml modules.conf.xml.bak
    sed -i -r \
    -e "s/<\!--\s?<load module=\"mod_lua\"\/>\s?-->/<load module=\"mod_lua\"\/>/g" \
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
    #cd $FS_CONFIG_PATH/conf/dialplan/
    #Configure XML CDR
    #cd $FS_CONFIG_PATH/conf/autoload_configs/

    #this is commented as we don't use xml_cdr anymore
    ## Place Newfies XML CDR conf in FreeSWITCH
    #[ -f xml_cdr.conf.xml ] && mv xml_cdr.conf.xml xml_cdr.conf.xml.bak
    #wget --no-check-certificate $FS_CONF_PATH/xml_cdr.conf.xml -O xml_cdr.conf.xml
    #create dir to store send error of CDR
    #mkdir /usr/local/freeswitch/log/err_xml_cdr/
}

func_create_alias_fs_cli() {
    echo "Setup alias fs_cli"
    alias fs_cli='/usr/local/freeswitch/bin/fs_cli'
    chk=`grep "fs_cli" ~/.bashrc|wc -l`
    if [ $chk -lt 1 ] ; then
        echo "alias fs_cli='/usr/local/freeswitch/bin/fs_cli'" >> ~/.bashrc
    fi
}

func_add_init_script() {
    #Install init.d script
    case $DIST in
        'DEBIAN')
            wget --no-check-certificate $FS_INIT_PATH/debian/freeswitch -O /etc/init.d/freeswitch
            chmod 0755 /etc/init.d/freeswitch
            cd /etc/init.d; update-rc.d freeswitch defaults 90
        ;;
        'CENTOS')
            wget --no-check-certificate $FS_INIT_PATH/centos/freeswitch -O /etc/init.d/freeswitch
            chmod 0755 /etc/init.d/freeswitch
            chkconfig --add freeswitch
            chkconfig --level 345 freeswitch on
        ;;
    esac
}


case $DIST in
    'DEBIAN')
        #Install FreeSWITCH from Debian packages
        #install_fs_deb_packages

        #!!! At the moment we cannot install from Deb packages cause we need the sources to compile
        #libs/esl/python

        #Install FreeSWITCH from sources
        func_install_fs_sources
        #Install luaSQL
        func_install_luasql
        #Create alias fs_cli
        func_create_alias_fs_cli
        #Install init.d script
        func_add_init_script
    ;;
    'CENTOS')
        #Install FreeSWITCH from sources
        func_install_fs_sources
        #Install luaSQL
        func_install_luasql
        #Create alias fs_cli
        func_create_alias_fs_cli
        #Install init.d script
        #*Not need if installed from deb packages
        func_add_init_script
    ;;
esac

#Configure FreeSWITCH
func_configure_fs


#Start FreeSWITCH
/etc/init.d/freeswitch start

cd $CURRENT_PATH

echo ""
echo "********************************************"
echo "Congratulations, FreeSWITCH is now installed"
echo "********************************************"
echo