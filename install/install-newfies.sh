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

# To download this script directly to your server :
# wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-newfies.sh
# For Development : wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/develop/install/install-newfies.sh
# then type,
# chmod +x install-newfies.sh
# ./install-newfies.sh
#
#
#TODO:
# - Memcached

#Install mode can me either CLONE or DOWNLOAD
INSTALL_MODE='CLONE'
DATETIME=$(date +"%Y%m%d%H%M%S")
KERNELARCH=$(uname -p)
INSTALL_DIR='/usr/share/newfies'
DATABASENAME=$INSTALL_DIR'/database/newfies.db'
MYSQLUSER=
MYSQLPASSWORD=
MYHOST=
MYHOSTPORT=
#Freeswitch update vars
FS_INSTALLED_PATH=/usr/local/freeswitch
NEWFIES_CDR_API='api\/v1\/store_cdr\/'

CELERYD_USER="celery"
CELERYD_GROUP="celery"

NEWFIES_ENV="newfies-dialer"
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

#Function mysql db setting
func_mysql_database_setting() {
    echo ""
    
    echo "Configure Mysql Settings..."
    echo ""
    echo "Enter Mysql hostname (default:localhost)"
    read MYHOST
    if [ -z "$MYHOST" ]; then
        MYHOST="localhost"
    fi
    echo "Enter Mysql port (default:3306)"
    read MYHOSTPORT
    if [ -z "$MYHOSTPORT" ]; then
        MYHOSTPORT="3306"
    fi
    echo "Enter Mysql Username (default:root)"
    read MYSQLUSER
    if [ -z "$MYSQLUSER" ]; then
        MYSQLUSER="root"
    fi
    echo "Enter Mysql Password (default:password)"
    read MYSQLPASSWORD
    if [ -z "$MYSQLPASSWORD" ]; then
        MYSQLPASSWORD="password"
    fi
    echo "Enter Database name (default:newfies)"
    read DATABASENAME
    if [ -z "$DATABASENAME" ]; then
        DATABASENAME="newfies"
    fi
}

#Fuction to create the virtual env
func_setup_virtualenv() {

    echo ""
    echo ""
    echo "This will install virtualenv & virtualenvwrapper"
    echo "and create a new virtualenv : $NEWFIES_ENV"
    
    easy_install virtualenv
    easy_install virtualenvwrapper
    
    # Enable virtualenvwrapper
    chk=`grep "virtualenvwrapper" ~/.bashrc|wc -l`
    if [ $chk -lt 1 ] ; then
        echo "Set Virtualenvwrapper into bash"
        echo "export WORKON_HOME=\/usr\/share\/virtualenvs" >> ~/.bashrc
        echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
    fi
    
    # Setup virtualenv
    export WORKON_HOME=/usr/share/virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh

    mkvirtualenv --no-site-packages $NEWFIES_ENV
    workon $NEWFIES_ENV
    
    echo "Virtualenv $NEWFIES_ENV created and activated"
}

#Function to install Frontend
func_install_frontend(){

    echo ""
    echo ""
    echo "This will install Web Newfies on your server"
    echo "Press Enter to continue or CTRL-C to exit"
    read TEMP

    db_backend=MySQL
    echo "Do you want to install Newfies with SQLite or MySQL? [SQLite/MySQL] (default:MySQL)"
    read db_backend
    
    branch=STABLE
    echo "Do you want to install Newfies DEVEL or STABLE? [DEVEL/STABLE] (default:STABLE)"
    read branch

    #python setup tools
    echo "Install Dependencies and python modules..."
    case $DIST in
        'DEBIAN')
            # SET APACHE CONF
            APACHE_CONF_DIR="/etc/apache2/sites-enabled/"

            apt-get -y install python-setuptools python-dev build-essential 
            apt-get -y install libapache2-mod-python libapache2-mod-wsgi
            easy_install pip
            #|FIXME: Strangely South need to be installed outside the Virtualenv
            pip install -e hg+http://bitbucket.org/andrewgodwin/south/@ecaafda23e600e510e252734d67bf8f9f2362dc9#egg=South-dev

            #ln -s /usr/local/bin/pip /usr/bin/pip
            
            #Install Extra dependencies on New OS        
            apt-get -y install git-core
            apt-get -y install mercurial
            apt-get -y install gawk
            #apt-get -y install python-importlib - does not exist in repository
                    
            if echo $db_backend | grep -i "^SQLITE" > /dev/null ; then
                 apt-get install sqlite3 libsqlite3-dev
            else
                 apt-get -y install mysql-server libmysqlclient-dev
                 func_mysql_database_setting
            fi
        ;;
        'CENTOS')
            # SET APACHE CONF
            APACHE_CONF_DIR="/etc/httpd/conf.d/"
            
            yum -y install python-setuptools python-tools python-devel mod_python
            #Install PIP
            rpm -ivh http://download.fedora.redhat.com/pub/epel/5/i386/epel-release-5-4.noarch.rpm 
            # disable epel repository since by default it is enabled. It is not recommended to keep 
            # non standard repositories activated. Use it just in case you need.
            sed -i "s/enabled=1/enable=0/" /etc/yum.repos.d/epel.repo 
            
            yum --enablerepo=epel install python-pip

            if echo $db_backend | grep -i "^SQLITE" > /dev/null ; then
                 yum -y install sqlite
            else
                 yum -y install mysql-server
                 func_mysql_database_setting
            fi
        ;;
    esac

    if [ -d "$INSTALL_DIR" ]; then
        # Newfies is already installed
        echo ""
        echo ""
        echo "We detect an existing Newfies Installation"
        echo "if you continue the existing installation will be removed!"
        echo ""
        echo "Press Enter to continue or CTRL-C to exit"
        read TEMP

        mkdir /tmp/old-newfies-dialer_$DATETIME
        mv $INSTALL_DIR /tmp/old-newfies-dialer_$DATETIME
        echo "Files from $INSTALL_DIR has been moved to /tmp/old-newfies-dialer_$DATETIME"
        echo "Press Enter to continue"
        read TEMP
    fi

    #Create and enable virtualenv
    func_setup_virtualenv
    
    #get Newfies
    echo "Install Newfies..."
    mkdir /usr/share/
    cd /usr/src/
    rm -rf newfies-dialer
    mkdir /var/log/newfies

    case $INSTALL_MODE in
        'CLONE')
            git clone git://github.com/Star2Billing/newfies-dialer.git
            
            #Install Develop / Master
            if echo $branch | grep -i "^DEVEL" > /dev/null ; then
                cd newfies-dialer
                git checkout -b develop --track origin/develop
            fi
        ;;
        # 'DOWNLOAD')
        #    VERSION=master
        #    wget --no-check-certificate https://github.com/Star2Billing/newfies-dialer/tarball/$VERSION
        #    mv master Star2Billing-newfies-dialer-$VERSION.tar.gz
        #    tar xvzf Star2Billing-newfies-dialer-*.tar.gz
        #    rm -rf Star2Billing-newfies-*.tar.gz
        #    mv newfies-dialer newfies-dialer_$DATETIME
        #    mv Star2Billing-newfies-* newfies-dialer        
        #;;
    esac

    # Copy files
    cp -r /usr/src/newfies-dialer/newfies $INSTALL_DIR

    #Install Newfies depencencies
    easy_install -U distribute
    pip install -r /usr/src/newfies-dialer/install/conf/requirements.txt
    pip install plivohelper
    
    # copy settings_local.py into newfies dir
    cp /usr/src/newfies-dialer/install/conf/settings_local.py $INSTALL_DIR

    # Update Secret Key
    echo "Update Secret Key..."
    RANDPASSW=`</dev/urandom tr -dc A-Za-z0-9| (head -c $1 > /dev/null 2>&1 || head -c 50)`
    sed -i "s/^SECRET_KEY.*/SECRET_KEY = \'$RANDPASSW\'/g"  $INSTALL_DIR/settings.py
    echo ""


    # Disable Debug
    sed -i "s/DEBUG = True/DEBUG = False/g"  $INSTALL_DIR/settings_local.py
    sed -i "s/TEMPLATE_DEBUG = DEBUG/TEMPLATE_DEBUG = False/g"  $INSTALL_DIR/settings_local.py

    if echo $db_backend | grep -i "^SQLITE" > /dev/null ; then
        # Setup settings_local.py for SQLite
        # Nothing to do
        echo ""
    else
        #Backup Mysql Database
        echo "Run backup with mysqldump..."
        mysqldump -u $MYSQLUSER --password=$MYSQLPASSWORD $DATABASENAME > /tmp/old-newfies-dialer_$DATETIME.mysqldump.sql
        echo "Mysql Dump of database $DATABASENAME added in /tmp/old-newfies-dialer_$DATETIME.mysqldump.sql"
        echo "Press Enter to continue"
        read TEMP
            
        # Setup settings_local.py for MySQL
        sed -i "s/'django.db.backends.sqlite3'/'django.db.backends.mysql'/"  $INSTALL_DIR/settings_local.py
        sed -i "s/.*'NAME'/       'NAME': '$DATABASENAME',#/"  $INSTALL_DIR/settings_local.py
        sed -i "/'USER'/s/''/'$MYSQLUSER'/" $INSTALL_DIR/settings_local.py
        sed -i "/'PASSWORD'/s/''/'$MYSQLPASSWORD'/" $INSTALL_DIR/settings_local.py
        sed -i "/'HOST'/s/''/'$MYHOST'/" $INSTALL_DIR/settings_local.py
        sed -i "/'PORT'/s/''/'$MYHOSTPORT'/" $INSTALL_DIR/settings_local.py
    
        # Create the Database
        echo "Remove Existing Database if exists..."
        echo "mysql --user=$MYSQLUSER --password=$MYSQLPASSWORD -e 'DROP DATABASE $DATABASENAME;'"
        mysql --user=$MYSQLUSER --password=$MYSQLPASSWORD -e "DROP DATABASE $DATABASENAME;"

        echo "Create Database..."
        echo "mysql --user=$MYSQLUSER --password=$MYSQLPASSWORD -e 'CREATE DATABASE $DATABASENAME CHARACTER SET UTF8;'"
        mysql --user=$MYSQLUSER --password=$MYSQLPASSWORD -e "CREATE DATABASE $DATABASENAME CHARACTER SET UTF8;"
    fi
    
    #Fix permission on python-egg
    mkdir $INSTALL_DIR/.python-eggs
    chmod 777 $INSTALL_DIR/.python-eggs

    case $DIST in
        'DEBIAN')
            chown -R www-data.www-data $INSTALL_DIR/database/
            touch /var/log/newfies/newfies-django.log
            chown www-data:www-data /var/log/newfies/newfies-django.log
            touch /var/log/newfies/newfies-django-db.log
            chown www-data:www-data /var/log/newfies/newfies-django-db.log
            touch /var/log/newfies/err-apache-newfies.log
            chown www-data:www-data /var/log/newfies/err-apache-newfies.log
        ;;
        'CENTOS')
            echo "Check what to do for CentOS..."
        ;;
    esac


    cd $INSTALL_DIR/
    #following line is for SQLite
    mkdir database
    python manage.py syncdb --noinput
    python manage.py migrate
    echo ""
    echo ""
    echo "Create a super admin user..."
    python manage.py createsuperuser
    
    #echo ""
    #echo "Create a super user for API, use a different username..."
    #python manage.py createsuperuser
    #echo ""
    #echo "Enter the Username you enteded for the API"
    #read APIUSERNAME
    #echo ""
    #echo "Enter the Password for the API "
    #read APIPASSWORD

    #Collect static files from apps and other locations in a single location.
    python manage.py collectstatic -l --noinput


    # prepare Apache
    echo "Prepare Apache configuration..."
    echo '
    Listen *:9080
    
    <VirtualHost *:9080>
        DocumentRoot '$INSTALL_DIR'/
        ErrorLog /var/log/newfies/err-apache-newfies.log
        LogLevel warn

        Alias /static/ "'$INSTALL_DIR'/static/"

        <Location "/static/">
            SetHandler None
        </Location>

        WSGIPassAuthorization On
        WSGIDaemonProcess newfies user=www-data user=www-data threads=25
        WSGIProcessGroup newfies
        WSGIScriptAlias / '$INSTALL_DIR'/django.wsgi

        <Directory '$INSTALL_DIR'>
            AllowOverride all
            Order deny,allow
            Allow from all
        </Directory>

    </VirtualHost>
    
    ' > $APACHE_CONF_DIR/newfies.conf
    #correct the above file
    sed -i "s/@/'/g"  $APACHE_CONF_DIR/newfies.conf
    
    case $DIST in
        'DEBIAN')
            service apache2 restart
        ;;
        'CENTOS')
            service httpd restart
        ;;
    esac

    IFCONFIG=`which ifconfig 2>/dev/null||echo /sbin/ifconfig`
    IPADDR=`$IFCONFIG eth0|gawk '/inet addr/{print $2}'|gawk -F: '{print $2}'`
    
    #Update Freeswitch XML CDR
    CDR_API_URL="http:\/\/$IPADDR:9080\/$NEWFIES_CDR_API"
    cd "$FS_INSTALLED_PATH/conf/autoload_configs/"
    sed -i "s/NEWFIES_API_STORE_CDR/$CDR_API_URL/g" xml_cdr.conf.xml
    
    #Update API username and password
    #sed -i "s/APIUSERNAME/$APIUSERNAME/g" xml_cdr.conf.xml
    #sed -i "s/APIPASSWORD/$APIPASSWORD/g" xml_cdr.conf.xml
    
    #Update for Plivo URL & Authorize local IP
    sed -i "s/SERVER_IP_PORT/$IPADDR:9080/g" $INSTALL_DIR/settings_local.py
    sed -i "s/#'SERVER_IP',/'$IPADDR',/g" $INSTALL_DIR/settings_local.py
    sed -i "s/dummy/plivo/g" $INSTALL_DIR/settings_local.py
    

    echo ""
    echo ""
    echo ""
    echo "**************************************************************"
    echo "Congratulations, Newfies Web Application is now installed!"
    echo "**************************************************************"
    echo ""
    echo "Please log on to Newfies at "
    echo "http://$IPADDR:9080"
    echo "the username and password are the ones you entered during this installation."
    echo ""
    echo "Thank you for installing Newfies"
    echo "Yours"
    echo "The Star2Billing Team"
    echo "http://www.star2billing.com and http://www.newfies-dialer.org/"
    echo
    echo "**************************************************************"
    echo ""
    echo ""
}


#Function to install backend
func_install_backend() {
    echo ""
    echo ""
    echo "This will install Newfies Backend, Celery & Redis on your server"
    echo "Press Enter to continue or CTRL-C to exit"
    read TEMP

    IFCONFIG=`which ifconfig 2>/dev/null||echo /sbin/ifconfig`
    IPADDR=`$IFCONFIG eth0|gawk '/inet addr/{print $2}'|gawk -F: '{print $2}'`


    #Install Celery & redis-server
    echo "Install Redis-server ..."
    func_install_redis_server

    #Install Celery
    pip install Celery

    #Memcache installation
    #pip install python-memcached


    echo ""
    echo "Configure Celery..."

    # Add init-scripts
    cp /usr/src/newfies-dialer/install/celery-init/etc/default/newfies-celeryd /etc/default/
    cp /usr/src/newfies-dialer/install/celery-init/etc/init.d/newfies-celeryd /etc/init.d/
    cp /usr/src/newfies-dialer/install/celery-init/etc/init.d/newfies-celerybeat /etc/init.d/

    # Configure init-scripts
    sed -i "s/CELERYD_USER='celery'/CELERYD_USER='$CELERYD_USER'/g"  /etc/default/newfies-celeryd
    sed -i "s/CELERYD_GROUP='celery'/CELERYD_GROUP='$CELERYD_GROUP'/g"  /etc/default/newfies-celeryd

    chmod +x /etc/default/newfies-celeryd
    chmod +x /etc/init.d/newfies-celeryd
    chmod +x /etc/init.d/newfies-celerybeat

    #Debug
    #python $INSTALL_DIR/manage.py celeryd -E -B -l debug

    /etc/init.d/newfies-celeryd restart
    /etc/init.d/newfies-celerybeat restart
    
    cd /etc/init.d; update-rc.d newfies-celeryd defaults 99
    cd /etc/init.d; update-rc.d newfies-celerybeat defaults 99

    echo ""
    echo ""
    echo ""
    echo "**************************************************************"
    echo "Congratulations, Newfies Backend is now installed!"
    echo "**************************************************************"
    echo ""
    echo ""
    echo "Thank you for installing Newfies"
    echo "Yours"
    echo "The Star2Billing Team"
    echo "http://www.star2billing.com and http://www.newfies-dialer.org/"
    echo
    echo "**************************************************************"
    echo ""
    echo ""
}


#Install recent version of redis-server
func_install_redis_server() {
    #TODO : Verify this work on CentOS
    cd /usr/src
    wget http://redis.googlecode.com/files/redis-2.2.11.tar.gz
    tar -zxf redis-2.2.11.tar.gz
    cd redis-2.2.11
    make
    make install

    cp /usr/src/newfies-dialer/install/redis/etc/redis.conf /etc/redis.conf
    cp /usr/src/newfies-dialer/install/redis/etc/init.d/redis-server /etc/init.d/redis-server
    chmod +x /etc/init.d/redis-server

    useradd redis
    mkdir -p /var/lib/redis
    mkdir -p /var/log/redis
    chown redis.redis /var/lib/redis
    chown redis.redis /var/log/redis
    
    case $DIST in
        'DEBIAN')
            cd /etc/init.d/
            update-rc.d -f redis-server defaults
        ;;
        'CENTOS')    
            chkconfig --add redis-server
	        chkconfig --level 2345 redis-server on
        ;;
    esac

    #Start redis-server
    /etc/init.d/redis-server start
}


#Menu Section for Script
show_menu_newfies() {
	clear
	echo " > Newfies Installation Menu (DEBIAN)"
	echo "====================================="
	echo "	1)  All"
	echo "	2)  Newfies Web Frontend"
	echo "	3)  Newfies Backend / Newfies-Celery"
	echo "	0)  Quit"
	echo -n "(0-3) : "
	read OPTION < /dev/tty
}



ExitFinish=0

while [ $ExitFinish -eq 0 ]; do

	# Show menu with Installation items
	show_menu_newfies

	case $OPTION in
		1) 
			func_install_frontend
			func_install_backend
			echo done
#			exit
		;;
		2) 
			func_install_frontend
		;;
		3) 
			func_install_backend
		;;
		0)
		ExitFinish=1
		;;
		*)
	esac	
	
done
