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
#
# >> Install with Master script :
# cd /usr/src/ ; rm install-newfies.sh ; wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-newfies.sh ; chmod +x install-newfies.sh ; ./install-newfies.sh
#
# >> Install with develop script :
# cd /usr/src/ ; rm install-newfies.sh ; wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/develop/install/install-newfies.sh ; chmod +x install-newfies.sh ; ./install-newfies.sh
#
# >> Install with appointment script :
# cd /usr/src/ ; rm install-newfies.sh ; wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/appointment/install/install-newfies.sh ; chmod +x install-newfies.sh ; ./install-newfies.sh
#

#Set branch to install develop / master / appointment
BRANCH="appointment"

DATETIME=$(date +"%Y%m%d%H%M%S")
INSTALL_DIR='/usr/share/newfies'
CONFIG_DIR='/usr/share/newfies/newfies_dialer/'
LUA_DIR='/usr/share/newfies-lua'
WELCOME_DIR='/var/www/newfies'
DATABASENAME='newfies_dialer_db'
DB_USERSALT=`</dev/urandom tr -dc 0-9| (head -c $1 > /dev/null 2>&1 || head -c 5)`
DB_USERNAME="newfies_dialer_$DB_USERSALT"
DB_PASSWORD=`</dev/urandom tr -dc A-Za-z0-9| (head -c $1 > /dev/null 2>&1 || head -c 20)`
DB_HOSTNAME='localhost'
DB_PORT='5432'
FS_INSTALLED_PATH='/usr/local/freeswitch'
NEWFIES_USER='newfies_dialer'
CELERYD_USER='celery'
CELERYD_GROUP='celery'
NEWFIES_ENV='newfies-dialer'
HTTP_PORT='8008'


#Django bug https://code.djangoproject.com/ticket/16017
export LANG="en_US.UTF-8"

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


#Function accept_license
func_accept_license() {
    clear
    echo ""
    echo "Newfies-Dialer License MPL V2.0"
    echo "Further information at http://www.newfies-dialer.org/support/licensing/"
    echo ""
    echo "This Source Code Form is subject to the terms of the Mozilla Public"
    echo "License, v. 2.0. If a copy of the MPL was not distributed with this file,"
    echo "You can obtain one at http://mozilla.org/MPL/2.0/."
    echo ""
    echo "Copyright (C) 2011-2013 Star2Billing S.L."
    echo ""
    echo ""
    echo "I agree to be bound by the terms of the license - [YES/NO]"
    echo ""
    read ACCEPT

    while [ "$ACCEPT" != "yes" ]  && [ "$ACCEPT" != "Yes" ] && [ "$ACCEPT" != "YES" ]  && [ "$ACCEPT" != "no" ]  && [ "$ACCEPT" != "No" ]  && [ "$ACCEPT" != "NO" ]; do
        echo "I agree to be bound by the terms of the license - [YES/NO]"
        read ACCEPT
    done
    if [ "$ACCEPT" != "yes" ]  && [ "$ACCEPT" != "Yes" ] && [ "$ACCEPT" != "YES" ]; then
        echo "License rejected !"
        exit 0
    fi
}


#Function install the landing page
func_install_landing_page() {
    mkdir -p $WELCOME_DIR
    # Copy files
    cp -r /usr/src/newfies-dialer/install/landing-page/* $WELCOME_DIR
    echo ""
    echo "Add Nginx configuration for Welcome page..."
    cp -rf /usr/src/newfies-dialer/install/nginx/global /etc/nginx/
    case $DIST in
        'DEBIAN')
            cp /usr/src/newfies-dialer/install/nginx/sites-available/newfies_dialer.conf /etc/nginx/sites-available/
            ln -s /etc/nginx/sites-available/newfies_dialer.conf /etc/nginx/sites-enabled/newfies_dialer.conf
            #Remove default NGINX landing page
            rm /etc/nginx/sites-enabled/default
        ;;
        'CENTOS')
            cp /usr/src/newfies-dialer/install/nginx/sites-available/newfies_dialer.conf /etc/nginx/conf.d/
            rm /etc/nginx/conf.d/default.conf
        ;;
    esac

    cp -rf /usr/src/newfies-dialer/install/nginx/global /etc/nginx/

    #Restart Nginx
    service nginx restart

    #Update Welcome page IP
    sed -i "s/LOCALHOST/$IPADDR:$HTTP_PORT/g" $WELCOME_DIR/index.html
}

func_check_dependencies() {
    echo ""
    echo "Checking Python dependencies..."
    echo ""

    #Check South
    grep_pip=`pip freeze| grep South`
    if echo $grep_pip | grep -i "South" > /dev/null ; then
        echo "OK : South installed..."
    else
        echo "Error : South not installed..."
        exit 1
    fi

    #Check Django
    grep_pip=`pip freeze| grep Django`
    if echo $grep_pip | grep -i "Django" > /dev/null ; then
        echo "OK : Django installed..."
    else
        echo "Error : Django not installed..."
        exit 1
    fi

    #Check celery
    grep_pip=`pip freeze| grep celery`
    if echo $grep_pip | grep -i "celery" > /dev/null ; then
        echo "OK : celery installed..."
    else
        echo "Error : celery not installed..."
        exit 1
    fi

    echo ""
    echo "Python dependencies successfully installed!"
    echo ""
}

#Configure Firewall
func_iptables_configuration() {
    #add http port
    iptables -I INPUT 2 -p tcp -m state --state NEW -m tcp --dport $HTTP_PORT -j ACCEPT
    iptables -I INPUT 3 -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT

    service iptables save
}

#Fuction to create the virtual env
func_setup_virtualenv() {
    echo "This will install virtualenv & virtualenvwrapper"
    echo "and create a new virtualenv : $NEWFIES_ENV"

    pip install virtualenv
    pip install virtualenvwrapper

    #Prepare settings for installation
    case $DIST in
        'DEBIAN')
            SCRIPT_VIRTUALENVWRAPPER="/usr/local/bin/virtualenvwrapper.sh"
        ;;
        'CENTOS')
            SCRIPT_VIRTUALENVWRAPPER="/usr/bin/virtualenvwrapper.sh"
        ;;
    esac

    # Enable virtualenvwrapper
    chk=`grep "virtualenvwrapper" ~/.bashrc|wc -l`
    if [ $chk -lt 1 ] ; then
        echo "Set Virtualenvwrapper into bash"
        echo "export WORKON_HOME=/usr/share/virtualenvs" >> ~/.bashrc
        echo "source $SCRIPT_VIRTUALENVWRAPPER" >> ~/.bashrc
    fi

    # Setup virtualenv
    export WORKON_HOME=/usr/share/virtualenvs
    source $SCRIPT_VIRTUALENVWRAPPER

    mkvirtualenv $NEWFIES_ENV
    workon $NEWFIES_ENV

    echo "Virtualenv $NEWFIES_ENV created and activated"
}


#Function to install Dependencies
func_install_dependencies(){

    #python setup tools
    echo "Install Dependencies and python modules..."

    case $DIST in
        'DEBIAN')
            export LANGUAGE=en_US.UTF-8
            export LANG=en_US.UTF-8
            export LC_ALL=en_US.UTF-8
            locale-gen en_US.UTF-8
            dpkg-reconfigure locales

            apt-get -y install python-software-properties
            add-apt-repository -y ppa:chris-lea/node.js
            apt-get update
            apt-get -y remove apache2.2-common apache2
            apt-get -y install --reinstall language-pack-en

            apt-get -y install python-setuptools python-dev build-essential
            apt-get -y install nginx supervisor
            apt-get -y install git-core mercurial gawk cmake
            apt-get -y install python-pip python-dev
            # for audiofile convertion
            apt-get -y install libsox-fmt-mp3 libsox-fmt-all mpg321 ffmpeg
            # install Node & npm
            apt-get -y install nodejs

            # postgresql
            apt-get -y install postgresql-9.1 postgresql-contrib-9.1
            apt-get -y install libpq-dev
            # start postgresql
            /etc/init.d/postgresql start

            #Lua Deps
            apt-get -y install liblua5.1-sql-postgres-dev
            #needed by lua-curl
            apt-get -y install libcurl4-openssl-dev

            #Memcached
            apt-get -y install memcached
            #Luarocks
            apt-get -y install luarocks luasocket
            luarocks install luasql-postgres PGSQL_INCDIR=/usr/include/postgresql/

        ;;
        'CENTOS')
            yum -y groupinstall "Development Tools"
            yum -y install git sudo cmake
            yum -y install python-setuptools python-tools python-devel mercurial memcached
            yum -y install mlocate vim git wget
            yum -y install policycoreutils-python
            easy_install pip

            #Install Supervisor
            pip install supervisor

            # install Node & npm
            yum -y --enablerepo=epel install npm


            #Audio File Conversion
            yum -y --enablerepo=rpmforge install sox sox-devel ffmpeg ffmpeg-devel mpg123 mpg123-devel libmad libmad-devel libid3tag libid3tag-devel lame lame-devel flac-devel libvorbis-devel
            cd /usr/src/

            #Install SOX for MP3 support
            SOXVERSION=14.4.1
            rm -rf sox
            wget http://switch.dl.sourceforge.net/project/sox/sox/$SOXVERSION/sox-$SOXVERSION.tar.gz
            tar zxf sox-$SOXVERSION.tar.gz
            rm -rf sox-$SOXVERSION.tar.gz
            mv sox-$SOXVERSION sox
            cd sox
            ./configure --bindir=/usr/bin/
            make -s
            make install
            cd /usr/src

            #Install, configure and start nginx
            yum -y install --enablerepo=epel nginx
            chkconfig --levels 235 nginx on
            service nginx start

            #Install & Start PostgreSQL 9.1
            #CentOs
            rpm -ivh http://yum.pgrpms.org/9.1/redhat/rhel-6-x86_64/pgdg-centos91-9.1-4.noarch.rpm
            #Redhad
            #rpm -ivh http://yum.pgrpms.org/9.1/redhat/rhel-6-x86_64/pgdg-redhat91-9.1-5.noarch.rpm
            yum -y install postgresql91-server postgresql91-devel
            chkconfig --levels 235 postgresql-9.1 on
            service postgresql-9.1 initdb
            ln -s /usr/pgsql-9.1/bin/pg_config /usr/bin
            ln -s /var/lib/pgsql/9.1/data /var/lib/pgsql
            ln -s /var/lib/pgsql/9.1/backups /var/lib/pgsql
            sed -i "s/ident/md5/g" /var/lib/pgsql/data/pg_hba.conf
            sed -i "s/ident/md5/g" /var/lib/pgsql/9.1/data/pg_hba.conf
            service postgresql-9.1 restart

            # Install Lua & luarocks
            cd /usr/src
            yum -y install readline-devel
            LUAVERSION=lua-5.1.5
            rm -rf lua
            wget http://www.lua.org/ftp/$LUAVERSION.tar.gz
            tar zxf $LUAVERSION.tar.gz
            rm -rf $LUAVERSION.tar.gz
            mv $LUAVERSION lua
            cd lua
            make linux
            make install
            cd /usr/src

            #Install Luarocks
            cd /usr/src
            LUAROCKSVERSION=luarocks-2.0.12
            rm -rf luarocks
            wget http://luarocks.org/releases/$LUAROCKSVERSION.tar.gz
            tar zxf $LUAROCKSVERSION.tar.gz
            rm -rf $LUAROCKSVERSION.tar.gz
            mv $LUAROCKSVERSION luarocks
            cd luarocks
            ./configure
            make
            make install
            cd /usr/src

            luarocks install luasql-postgres PGSQL_DIR=/usr/pgsql-9.1/
        ;;
    esac

    # install Bower
    npm install -g bower

    #Install Lua dependencies
    luarocks install luasocket
    luarocks install lualogging
    luarocks install loop
    luarocks install md5
    luarocks install luafilesystem
    luarocks install luajson 1.3.2-1
    luarocks install inspect
    luarocks install redis-lua
    luarocks install lua-cmsgpack
    #Issue with last version of lpeg - lua libs/tag_replace.lua will seg fault
    #Pin the version 0.10.2-1
    luarocks remove lpeg --force
    luarocks install http://luarocks.org/repositories/rocks/lpeg-0.10.2-1.rockspec

    #Lua curl
    cd /usr/src/
    rm -rf lua-curl-master
    wget https://github.com/msva/lua-curl/archive/master.zip -O lua-curl.zip
    unzip lua-curl.zip
    cd lua-curl-master
    cmake . && make install
    #add cURL.so to lua libs
    cp cURL.so /usr/local/lib/lua/5.1/

    #Create Newfies User
    echo ""
    echo "Create Newfies-Dialer User/Group : $NEWFIES_USER"
    useradd $NEWFIES_USER --user-group --system --no-create-home
}


#Function to install Python dependencies
func_install_pip_deps(){

    #Install Newfies-Dialer depencencies
    easy_install -U distribute
    #pip now only installs stable versions by default, so we need to use --pre option
    pip install --pre pytz
    #For python 2.6 only
    pip install importlib

    echo "Install basic requirements..."
    for line in $(cat /usr/src/newfies-dialer/install/requirements/basic-requirements.txt | grep -v \#)
    do
        pip install $line
    done
    echo "Install Django requirements..."
    for line in $(cat /usr/src/newfies-dialer/install/requirements/django-requirements.txt | grep -v \#)
    do
        pip install $line
    done

    #Install Python ESL / this needs to be done within the virtualenv
    cd /usr/src/freeswitch/libs/esl
    make pymod-install

    #Check Python dependencies
    func_check_dependencies

    echo "**********"
    echo "PIP Freeze"
    echo "**********"
    pip freeze
}


#Function to prepare settings_local.py
func_prepare_settings(){

    #Copy settings_local.py into newfies dir
    cp /usr/src/newfies-dialer/install/conf/settings_local.py $CONFIG_DIR

    #Update Secret Key
    echo "Update Secret Key..."
    RANDPASSW=`</dev/urandom tr -dc A-Za-z0-9| (head -c $1 > /dev/null 2>&1 || head -c 50)`
    sed -i "s/^SECRET_KEY.*/SECRET_KEY = \'$RANDPASSW\'/g"  $CONFIG_DIR/settings.py
    echo ""

    #Disable Debug
    sed -i "s/DEBUG = True/DEBUG = False/g"  $CONFIG_DIR/settings_local.py
    sed -i "s/TEMPLATE_DEBUG = DEBUG/TEMPLATE_DEBUG = False/g"  $CONFIG_DIR/settings_local.py

    #Setup settings_local.py for POSTGRESQL
    sed -i "s/DATABASENAME/$DATABASENAME/"  $CONFIG_DIR/settings_local.py
    sed -i "s/DB_USERNAME/$DB_USERNAME/" $CONFIG_DIR/settings_local.py
    sed -i "s/DB_PASSWORD/$DB_PASSWORD/" $CONFIG_DIR/settings_local.py
    sed -i "s/DB_HOSTNAME/$DB_HOSTNAME/" $CONFIG_DIR/settings_local.py
    sed -i "s/DB_PORT/$DB_PORT/" $CONFIG_DIR/settings_local.py

    #Setup settings_local.py for POSTGRESQL
    sed -i "s/newfiesdb/$DATABASENAME/"  $LUA_DIR/libs/settings.lua
    sed -i "s/newfiesuser/$DB_USERNAME/" $LUA_DIR/libs/settings.lua
    sed -i "s/password/$DB_PASSWORD/" $LUA_DIR/libs/settings.lua
    sed -i "s/127.0.0.1/$DB_HOSTNAME/" $LUA_DIR/libs/settings.lua
    sed -i "s/5432/$DB_PORT/" $LUA_DIR/libs/settings.lua

    #ODBC
    cp /usr/src/newfies-dialer/install/odbc/odbc.ini /etc/odbc.ini
    #Setup odbc.ini for POSTGRESQL
    sed -i "s/DATABASENAME/$DATABASENAME/" /etc/odbc.ini
    sed -i "s/DB_USERNAME/$DB_USERNAME/" /etc/odbc.ini
    sed -i "s/DB_PASSWORD/$DB_PASSWORD/" /etc/odbc.ini
    sed -i "s/DB_HOSTNAME/$DB_HOSTNAME/" /etc/odbc.ini
    sed -i "s/DB_PORT/$DB_PORT/" /etc/odbc.ini

    IFCONFIG=`which ifconfig 2>/dev/null||echo /sbin/ifconfig`
    IPADDR=`$IFCONFIG eth0|gawk '/inet addr/{print $2}'|gawk -F: '{print $2}'`
    if [ -z "$IPADDR" ]; then
        clear
        echo "We have not detected your IP address automatically, please enter it manually"
        read IPADDR
    fi

    ##Update Freeswitch XML CDR
    #NEWFIES_CDR_API='api\/v1\/store_cdr\/'
    #CDR_API_URL="http:\/\/$IPADDR:$HTTP_PORT\/$NEWFIES_CDR_API"
    #cd "$FS_INSTALLED_PATH/conf/autoload_configs/"
    #sed -i "s/NEWFIES_API_STORE_CDR/$CDR_API_URL/g" xml_cdr.conf.xml
    #
    ##Update API username and password
    #sed -i "s/APIUSERNAME/$APIUSERNAME/g" xml_cdr.conf.xml
    #sed -i "s/APIPASSWORD/$APIPASSWORD/g" xml_cdr.conf.xml

    #Update Authorize local IP
    sed -i "s/SERVER_IP_PORT/$IPADDR:$HTTP_PORT/g" $CONFIG_DIR/settings_local.py
    sed -i "s/#'SERVER_IP',/'$IPADDR',/g" $CONFIG_DIR/settings_local.py
    sed -i "s/SERVER_IP/$IPADDR/g" $CONFIG_DIR/settings_local.py

    case $DIST in
        'DEBIAN')
            #Get TZ
            ZONE=$(head -1 /etc/timezone)
        ;;
        'CENTOS')
            #Get TZ
            . /etc/sysconfig/clock
            echo ""
            echo "We will now add port $HTTP_PORT  and port 80 to your Firewall"
            echo "Press Enter to continue or CTRL-C to exit"
            read TEMP

            func_iptables_configuration

            #Selinux to allow apache to access this directory
            chcon -Rv --type=httpd_sys_content_t /usr/share/virtualenvs/newfies-dialer/
            chcon -Rv --type=httpd_sys_content_t /usr/share/newfies/usermedia
            semanage port -a -t http_port_t -p tcp $HTTP_PORT
            #Allowing Apache to access Redis port
            semanage port -a -t http_port_t -p tcp 6379
        ;;
    esac

    #Set Timezone in settings_local.py
    sed -i "s@Europe/Madrid@$ZONE@g" $CONFIG_DIR/settings_local.py
}


#Configure Logs files and logrotate
func_prepare_logger() {

    #Following lines is for apache logs
    touch /var/log/newfies/newfies-django.log
    touch /var/log/newfies/newfies-django-db.log
    touch /var/log/newfies/gunicorn_newfies_dialer.log
    chown -R $NEWFIES_USER:$NEWFIES_USER /var/log/newfies

    echo "Install Logrotate..."
    # First delete to avoid error when running the script several times.
    rm /etc/logrotate.d/newfies_dialer
    touch /etc/logrotate.d/newfies_dialer
    echo '
    /var/log/newfies/*.log {
        daily
        rotate 10
        size = 50M
        missingok
        compress
    }
    '  >> /etc/logrotate.d/newfies_dialer

    logrotate /etc/logrotate.d/newfies_dialer
}

#function to get the source of Newfies
func_install_source(){

    #get Newfies-Dialer
    echo "Install Newfies-Dialer..."
    cd /usr/src/
    rm -rf newfies-dialer
    mkdir /var/log/newfies

    git clone git://github.com/Star2Billing/newfies-dialer.git
    cd newfies-dialer

    #Install branch develop / callcenter
    if echo $BRANCH | grep -i "^develop" > /dev/null ; then
        git checkout -b develop --track origin/develop
    fi
    if echo $BRANCH | grep -i "^appointment" > /dev/null ; then
        git checkout -b appointment --track origin/appointment
    fi

    #Copy files
    cp -r /usr/src/newfies-dialer/newfies $INSTALL_DIR
    cp -r /usr/src/newfies-dialer/lua $LUA_DIR
    cd $LUA_DIR/libs/
    wget --no-check-certificate https://raw.github.com/areski/lua-acapela/$BRANCH/acapela.lua

    #Upload audio files
    mkdir -p /usr/share/newfies/usermedia/upload/audiofiles
    chown -R $NEWFIES_USER:$NEWFIES_USER /usr/share/newfies/usermedia
}

#Create PGSQL
func_create_pgsql_database(){

    # Create the Database
    echo "We will remove existing Database"
    echo "Press Enter to continue"
    read TEMP
    echo "sudo -u postgres dropdb $DATABASENAME"
    sudo -u postgres dropdb $DATABASENAME
    # echo "Remove Existing Database if exists..."
    #if [ `sudo -u postgres psql -qAt --list | egrep $DATABASENAME | wc -l` -eq 1 ]; then
    #     echo "sudo -u postgres dropdb $DATABASENAME"
    #     sudo -u postgres dropdb $DATABASENAME
    # fi
    echo "Create Database..."
    echo "sudo -u postgres createdb $DATABASENAME"
    sudo -u postgres createdb $DATABASENAME

    #CREATE ROLE / USER
    echo "Create Postgresql user $DB_USERNAME"
    #echo "sudo -u postgres createuser --no-createdb --no-createrole --no-superuser $DB_USERNAME"
    #sudo -u postgres createuser --no-createdb --no-createrole --no-superuser $DB_USERNAME
    echo "sudo -u postgres psql --command=\"create user $DB_USERNAME with password 'XXXXXXXXXXXX';\""
    sudo -u postgres psql --command="CREATE USER $DB_USERNAME with password '$DB_PASSWORD';"

    echo "Grant all privileges to user..."
    sudo -u postgres psql --command="GRANT ALL PRIVILEGES on database $DATABASENAME to $DB_USERNAME;"
}

#NGINX / SUPERVISOR
func_nginx_supervisor(){
    #Configure and Start supervisor
    case $DIST in
        'DEBIAN')
            cp /usr/src/newfies-dialer/install/supervisor/gunicorn_newfies_dialer.conf /etc/supervisor/conf.d/
        ;;
        'CENTOS')
            cp /usr/src/newfies-dialer/install/supervisor/supervisord /etc/init.d/supervisor
            chmod +x /etc/rc.d/init.d/supervisor
            chkconfig --levels 235 supervisor on
            echo_supervisord_conf > /etc/supervisord.conf
            cat /usr/src/newfies-dialer/install/supervisor/gunicorn_newfies_dialer.conf >> /etc/supervisord.conf
            mkdir /var/log/supervisor/
        ;;
    esac
    /etc/init.d/supervisor force-stop
    /etc/init.d/supervisor start
}

#CELERY SUPERVISOR
func_celery_supervisor(){
    #Configure and Start supervisor
    case $DIST in
        'DEBIAN')
            cp /usr/src/newfies-dialer/install/supervisor/celery_newfies_dialer.conf /etc/supervisor/conf.d/
        ;;
        'CENTOS')
            cp /usr/src/newfies-dialer/install/supervisor/supervisord /etc/init.d/supervisor
            chmod +x /etc/rc.d/init.d/supervisor
            chkconfig --levels 235 supervisor on
            echo_supervisord_conf > /etc/supervisord.conf
            cat /usr/src/newfies-dialer/install/supervisor/celery_newfies_dialer.conf >> /etc/supervisord.conf
            mkdir /var/log/supervisor/
        ;;
    esac
    /etc/init.d/supervisor force-stop
    /etc/init.d/supervisor start
}

#Function to install Frontend
func_install_frontend(){

    echo ""
    echo ""
    echo "This script will install Newfies-Dialer"
    echo "======================================="
    echo ""

    if [ -d "$INSTALL_DIR" ]; then
        # Newfies-Dialer is already installed
        clear
        echo ""
        echo "We detect an existing Newfies-Dialer Installation"
        echo "if you continue the existing installation will be removed!"
        echo ""
        echo "Press Enter to continue or CTRL-C to exit"
        read TEMP

        mkdir /tmp/old-newfies-dialer_$DATETIME
        mv $INSTALL_DIR /tmp/old-newfies-dialer_$DATETIME
        mkdir /tmp/old-lua-newfies-dialer_$DATETIME
        mv $LUA_DIR /tmp/old-lua-newfies-dialer_$DATETIME
        echo "Files from $INSTALL_DIR has been moved to /tmp/old-newfies-dialer_$DATETIME and /tmp/old-lua-newfies-dialer_$DATETIME"

        if [ `sudo -u postgres psql -qAt --list | egrep '^$DATABASENAME\|' | wc -l` -eq 1 ]; then
            echo ""
            echo "Run backup with postgresql..."
            sudo -u postgres pg_dump $DATABASENAME > /tmp/old-newfies-dialer_$DATETIME.pgsqldump.sql
            echo "PostgreSQL Dump of database $DATABASENAME added in /tmp/old-newfies-dialer_$DATETIME.pgsqldump.sql"
            echo "Press Enter to continue"
            read TEMP
        fi
    fi

    #Install Depedencies
    func_install_dependencies

    #Install Celery & redis-server
    func_install_redis_server

    #Create and enable virtualenv
    func_setup_virtualenv

    #Install Code Source
    func_install_source

    #Install PIP dependencies
    func_install_pip_deps

    #Prepare the settings
    func_prepare_settings

    func_create_pgsql_database

    #Prepare Django DB / Migrate / Create User ...
    cd $INSTALL_DIR/
    python manage.py syncdb --noinput
    python manage.py migrate dialer_settings
    python manage.py migrate dialer_contact
    python manage.py migrate sms
    python manage.py migrate dialer_campaign
    python manage.py migrate

    #Load Countries Dialcode
    #python manage.py load_country_dialcode
    wget https://raw.github.com/areski/django-sms-gateway/master/sms/fixtures/example_gateways.json
    python manage.py loaddata example_gateways.json
    rm example_gateways.json

    clear
    echo ""
    echo "Create a super admin user..."
    python manage.py createsuperuser

    echo "Install Bower deps"
    python manage.py bower_install -- --allow-root

    echo "Collects the static files"
    python manage.py collectstatic --noinput

    #NGINX / SUPERVISOR
    func_nginx_supervisor

    # * * LOGROTATE * *
    func_prepare_logger

    echo ""
    echo "*****************************************************************"
    echo "Congratulations, Newfies-Dialer Web Application is now installed!"
    echo "*****************************************************************"
    echo ""
    echo "Please log on to Newfies-Dialer at "
    echo "http://$IPADDR:$HTTP_PORT"
    echo "the username and password are the ones you entered during this installation."
    echo ""
    echo "Thank you for installing Newfies-Dialer"
    echo "Yours"
    echo "The Star2Billing Team"
    echo "http://www.star2billing.com and http://www.newfies-dialer.org/"
    echo ""
    echo "**************************************************************"
    echo ""
}


#Function to install backend
func_install_backend() {
    echo ""
    echo ""
    echo "This will install Newfies-Dialer Backend, Celery & Redis on your server"
    echo "Press Enter to continue or CTRL-C to exit"
    read TEMP

    IFCONFIG=`which ifconfig 2>/dev/null||echo /sbin/ifconfig`
    IPADDR=`$IFCONFIG eth0|gawk '/inet addr/{print $2}'|gawk -F: '{print $2}'`
    if [ -z "$IPADDR" ]; then
        clear
        echo "we have not detected your IP address automatically, please enter it manually"
        read IPADDR
    fi

    #Create directory for pid file
    mkdir -p /var/run/celery

    #Install Celery & redis-server
    func_install_redis_server

    #Memcache installation
    #pip install python-memcached

    echo "Install Celery via supervisor..."
    func_celery_supervisor

    case $DIST in
        'DEBIAN')
            #Check permissions on /dev/shm to ensure that celery can start and run for openVZ.
            DIR="/dev/shm"
            echo "Checking the permissions for $dir"
            stat $DIR
            if [ `stat -c "%a" $DIR` -ge 777 ] ; then
                echo "$DIR has Read Write permissions."
            else
                echo "$DIR has no read write permissions."
                chmod -R 777 /dev/shm
                if [ `grep -i /dev/shm /etc/fstab | wc -l` -eq 0 ]; then
                    echo "Adding fstab entry to set permissions /dev/shm"
                    echo "none /dev/shm tmpfs rw,nosuid,nodev,noexec 0 0" >> /etc/fstab
                fi
            fi
        ;;
    esac

    #Install Python ESL / those lines doesn't work in install-freeswitch.sh
    cd /usr/src/freeswitch/libs/esl
    make pymod-install

    #Restart FreeSWITCH to find the startup-script
    /etc/init.d/freeswitch restart

    echo ""
    echo "**************************************************************"
    echo "Congratulations, Newfies-Dialer Backend is now installed!"
    echo "**************************************************************"
    echo ""
    echo "Thank you for installing Newfies-Dialer"
    echo "Yours"
    echo "The Star2Billing Team"
    echo "http://www.star2billing.com and http://www.newfies-dialer.org/"
    echo ""
    echo "**************************************************************"
    echo ""
}


#Install recent version of redis-server
func_install_redis_server() {
    echo "Install Redis-server ..."
    case $DIST in
        'DEBIAN')
            apt-get -y install redis-server
            /etc/init.d/redis-server restart
        ;;
        'CENTOS')
            yum -y --enablerepo=epel install redis
            chkconfig --add redis
            chkconfig --level 2345 redis on
            /etc/init.d/redis start
        ;;
    esac
}
