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
#
# >> Install with Master script :
# cd /usr/src/ ; rm install-newfies.sh ; wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-newfies.sh ; chmod +x install-newfies.sh ; ./install-newfies.sh
#
# >> Install with develop script :
# cd /usr/src/ ; rm install-newfies.sh ; wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/develop/install/install-newfies.sh ; chmod +x install-newfies.sh ; ./install-newfies.sh
#


#Set branch to install DEVEL/STABLE
BRANCH=DEVEL
#TODO: update before release

#Install mode can me either CLONE or DOWNLOAD
INSTALL_MODE='CLONE'
DB_BACKEND=PostgreSQL
DATETIME=$(date +"%Y%m%d%H%M%S")
KERNELARCH=$(uname -p)
INSTALL_DIR='/usr/share/newfies'
INSTALL_DIR_WELCOME='/var/www/newfies'
DATABASENAME=$INSTALL_DIR'/database/newfies.db'
DB_USERNAME=
DB_PASSWORD=
DB_HOSTNAME=
DB_PORT=
#Freeswitch update vars
FS_INSTALLED_PATH=/usr/local/freeswitch
CELERYD_USER="celery"
CELERYD_GROUP="celery"
INSTALL_USER="newfies"
NEWFIES_ENV="newfies-dialer"
HTTP_PORT="8008"


#Django bug https://code.djangoproject.com/ticket/16017
export LANG="en_US.UTF-8"

# Identify Linux Distribution type
func_identify_os() {

    if [ -f /etc/debian_version ] ; then
        DIST='DEBIAN'
        if [ "$(lsb_release -cs)" != "lucid" ] && [ "$(lsb_release -cs)" != "precise" ]; then
		    echo "This script is only intended to run on Ubuntu 12.04 TLS or CentOS 6.2 / 6.3"
		    exit 255
	    fi
    elif [ -f /etc/redhat-release ] ; then
        DIST='CENTOS'
        if [ "$(awk '{print $3}' /etc/redhat-release)" != "6.2" ] && [ "$(awk '{print $3}' /etc/redhat-release)" != "6.3" ] ; then
        	echo "This script is only intended to run on Ubuntu 12.04 TLS or CentOS 6.2 / 6.3"
        	exit 255
        fi
    else
        echo ""
        echo "This script is only intended to run on Ubuntu 12.04 TLS or CentOS 6.2 / 6.3"
        echo ""
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
    echo "Copyright (C) 2011-2012 Star2Billing S.L."
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
    mkdir -p $INSTALL_DIR_WELCOME
    # Copy files
    cp -r /usr/src/newfies-dialer/install/landing-page/* $INSTALL_DIR_WELCOME
    echo ""
    echo "Add Nginx configuration for Welcome page..."
    cp -rf /usr/src/newfies-dialer/install/nginx/global /etc/nginx/
    cp /usr/src/newfies-dialer/install/nginx/sites-available/newfies_dialer /etc/nginx/sites-available/
    #Restart Nginx
    service nginx restart

    #Update Welcome page IP
    sed -i "s/LOCALHOST/$IPADDR:$HTTP_PORT/g" $INSTALL_DIR_WELCOME/index.html
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

    #Check django-tastypie
    grep_pip=`pip freeze| grep django-tastypie`
    if echo $grep_pip | grep -i "django-tastypie" > /dev/null ; then
        echo "OK : django-tastypie installed..."
    else
        echo "Error : django-tastypie not installed..."
        exit 1
    fi

    echo ""
    echo "Python dependencies successfully installed!"
    echo ""
}

#Function database setting
func_database_setting() {
    echo ""
    echo "Configure Database Settings..."
    echo ""

    echo "Enter Database hostname (default:localhost)"
    read DB_HOSTNAME
    if [ -z "$DB_HOSTNAME" ]; then
        DB_HOSTNAME="localhost"
    fi
    echo "Enter Database port (default:5432)"
    read DB_PORT
    if [ -z "$DB_PORT" ]; then
        DB_PORT="5432"
    fi
    echo "Enter Database Username (default:root)"
    read DB_USERNAME
    if [ -z "$DB_USERNAME" ]; then
        DB_USERNAME="root"
    fi
    echo "Enter Database Password (default:password)"
    read DB_PASSWORD
    if [ -z "$DB_PASSWORD" ]; then
        DB_PASSWORD="password"
    fi
    echo "Enter Database Name (default:newfies)"
    read DATABASENAME
    if [ -z "$DATABASENAME" ]; then
        DATABASENAME="newfies"
    fi
}

func_iptables_configuration() {
    #add http port
    iptables -I INPUT 2 -p tcp -m state --state NEW -m tcp --dport $HTTP_PORT -j ACCEPT
    iptables -I INPUT 3 -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT

    service iptables save
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

#Function to install Frontend
func_install_frontend(){

    echo ""
    echo ""
    echo "This script will install Newfies-Dialer on your server"
	echo "======================================================"
    echo ""
    #echo "Which version do you want to install ? DEVEL or STABLE [] (default:STABLE)"
    #read BRANCH

    #python setup tools
    echo "Install Dependencies and python modules..."
    case $DIST in
        'DEBIAN')
            apt-get -y install python-setuptools python-dev build-essential
            apt-get -y install nginx supervisor
            apt-get -y install git-core mercurial gawk
            easy_install pip

            #PostgreSQL
            apt-get -y install postgresql libpq-dev
            #Start PostgreSQL
            /etc/init.d/postgresql start

            #the following doesn't work with postgresql unless you create a local file
            #or set to "trust" in pg_hba.conf
            #until psql -h $DB_HOSTNAME -p $DB_PORT $DB_USERNAME $DB_USERNAME -c ";" ; do
            clear
            echo "Enter correct database settings"
            func_database_setting

            #for audiofile convertion
            apt-get -y install libsox-fmt-mp3 libsox-fmt-all mpg321 ffmpeg
        ;;
        'CENTOS')
			if [ ! -f /etc/yum.repos.d/rpmforge.repo ];
            	then
                	# Install RPMFORGE Repo
                	#Check architecture
        			KERNELARCH=$(uname -p)
        			if [ $KERNELARCH = "x86_64" ]; then
						rpm -ivh http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm
					else
						rpm -ivh http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.2-2.el6.rf.i686.rpm
					fi
        	fi

            #Install epel repo for pip and mod_python
            if [ $KERNELARCH = "x86_64" ]; then
				rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-7.noarch.rpm
			else
				rpm -ivh http://dl.fedoraproject.org/pub/epel/6/i386/epel-release-6-7.noarch.rpm
			fi

            # disable epel repository since by default it is enabled.
            sed -i "s/enabled=1/enable=0/" /etc/yum.repos.d/epel.repo
            yum -y --enablerepo=epel install python-pip mod_python python-setuptools python-tools python-devel mercurial mod_wsgi
            #start http after reboot
            chkconfig --levels 235 httpd on

            #Install & Start PostgreSQL
            yum install postgresql-server
            chkconfig --levels 235 postgresq on
            /etc/init.d/postgresql start

            #the following doesn't work with postgresql unless you create a local file
            #or set to "trust" in pg_hba.conf
            #until psql -h $DB_HOSTNAME -p $DB_PORT $DB_USERNAME $DB_USERNAME -c ";" ; do
            clear
            echo "Enter correct database settings"
            func_database_setting
        ;;
    esac

    if [ -d "$INSTALL_DIR" ]; then
        # Newfies-Dialer is already installed
        echo ""
        echo ""
        echo "We detect an existing Newfies-Dialer Installation"
        echo "if you continue the existing installation will be removed!"
        echo ""
        echo "Press Enter to continue or CTRL-C to exit"
        read TEMP

        mkdir /tmp/old-newfies-dialer_$DATETIME
        mv $INSTALL_DIR /tmp/old-newfies-dialer_$DATETIME
        echo "Files from $INSTALL_DIR has been moved to /tmp/old-newfies-dialer_$DATETIME"

        echo "Run backup with postgresql..."
        sudo -u postgres pg_dump $DATABASENAME > /tmp/old-newfies-dialer_$DATETIME.pgsqldump.sql
        echo "PostgreSQL Dump of database $DATABASENAME added in /tmp/old-newfies-dialer_$DATETIME.pgsqldump.sql"
        echo "Press Enter to continue"
        read TEMP
    fi

    #Create and enable virtualenv
    func_setup_virtualenv

    #get Newfies-Dialer
    echo "Install Newfies-Dialer..."
    cd /usr/src/
    rm -rf newfies-dialer
    mkdir /var/log/newfies

    case $INSTALL_MODE in
        'CLONE')
            git clone git://github.com/Star2Billing/newfies-dialer.git
            #Install Develop / Master
            if echo $BRANCH | grep -i "^DEVEL" > /dev/null ; then
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

    #Install Newfies-Dialer depencencies
    easy_install -U distribute
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
    pip install plivohelper

    #Check Python dependencies
    func_check_dependencies

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

    # Setup settings_local.py for POSTGRESQL
    sed -i "s/.*'NAME'/       'NAME': '$DATABASENAME',#/"  $INSTALL_DIR/settings_local.py
    sed -i "/'USER'/s/''/'$DB_USERNAME'/" $INSTALL_DIR/settings_local.py
    sed -i "/'PASSWORD'/s/''/'$DB_PASSWORD'/" $INSTALL_DIR/settings_local.py
    sed -i "/'HOST'/s/''/'$DB_HOSTNAME'/" $INSTALL_DIR/settings_local.py
    sed -i "/'PORT'/s/''/'$DB_PORT'/" $INSTALL_DIR/settings_local.py

    # Create the Database
    echo "Remove Existing Database if exists..."
    if [ `sudo -u postgres psql -qAt --list | egrep '^$DATABASENAME\|' | wc -l` -eq 1 ]; then
        echo "sudo -u postgres dropdb $DATABASENAME"
        sudo -u postgres dropdb $DATABASENAME
    fi
    echo "Create Database..."
    echo "sudo -u postgres createdb $DATABASENAME"
    sudo -u postgres createdb $DATABASENAME

    #CREATE ROLE / USER
    echo "Create Postgresql user $DB_USERNAME, you will be prompted for password..."
    echo "sudo -u postgres createuser --no-createdb --no-createrole --no-superuser --pwprompt $DB_USERNAME"
    sudo -u postgres createuser --no-createdb --no-createrole --no-superuser --pwprompt $DB_USERNAME
    echo "Grant all privileges to user..."
    sudo -u postgres psql --command="grant all privileges on database $DATABASENAME to $DB_USERNAME;"

    cd $INSTALL_DIR/

    #Fix permission on python-egg
    mkdir /usr/share/newfies/.python-eggs
    chown $INSTALL_USER:$INSTALL_USER /usr/share/newfies/.python-eggs
    mkdir database

    #upload audio files
    mkdir -p /usr/share/newfies/usermedia/upload/audiofiles
    chown -R $INSTALL_USER:$INSTALL_USER /usr/share/newfies/usermedia

    #following lines is for apache logs
    touch /var/log/newfies/newfies-django.log
    touch /var/log/newfies/newfies-django-db.log
    touch /var/log/newfies/err-apache-newfies.log
    chown -R $INSTALL_USER:$INSTALL_USER /var/log/newfies

    python manage.py syncdb --noinput
    python manage.py migrate
    echo ""
    echo ""
    echo "Create a super admin user..."
    python manage.py createsuperuser

    #Collect static files from apps and other locations in a single location.
    python manage.py collectstatic -l --noinput

    #Load Countries Dialcode
    #python manage.py load_country_dialcode

    # prepare Nginx
    echo "Prepare Nginx configuration..."
    cp -rf /usr/src/newfies-dialer/install/nginx/global /etc/nginx/
    cp /usr/src/newfies-dialer/install/nginx/sites-available/newfies_dialer /etc/nginx/sites-available/
    #Restart Nginx
    service nginx restart

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

    #Update for Plivo URL & Authorize local IP
    sed -i "s/SERVER_IP_PORT/$IPADDR:$HTTP_PORT/g" $INSTALL_DIR/settings_local.py
    sed -i "s/#'SERVER_IP',/'$IPADDR',/g" $INSTALL_DIR/settings_local.py
    sed -i "s/dummy/plivo/g" $INSTALL_DIR/settings_local.py

    case $DIST in
        'DEBIAN')
            service apache2 restart
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

            service httpd restart
        ;;
    esac

    #Set Timezone in settings_local.py
    sed -i "s@Europe/Madrid@$ZONE@g" $INSTALL_DIR/settings_local.py

    echo "Install Logrotate..."
    #Setup log rotation
    touch /etc/logrotate.d/newfies_dialer
    echo '
    /var/log/newfies/*.log {
        daily
        rotate 10
        size = 20M
        missingok
        compress
    }
    '  >> /etc/logrotate.d/newfies_dialer


    echo ""
    echo ""
    echo "**************************************************************"
    echo "Congratulations, Newfies-Dialer Web Application is now installed!"
    echo "**************************************************************"
    echo ""
    echo "Please log on to Newfies-Dialer at "
    echo "http://$IPADDR:$HTTP_PORT"
    echo "the username and password are the ones you entered during this installation."
    echo ""
    echo "Thank you for installing Newfies-Dialer"
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

    echo "Configure Celery..."
    case $DIST in
        'DEBIAN')
            # Add init-scripts
            cp /usr/src/newfies-dialer/install/celery-init/debian/etc/default/newfies-celeryd /etc/default/
            cp /usr/src/newfies-dialer/install/celery-init/debian/etc/init.d/newfies-celeryd /etc/init.d/
            # Configure init-scripts
            sed -i "s/CELERYD_USER='celery'/CELERYD_USER='$CELERYD_USER'/g"  /etc/default/newfies-celeryd
            sed -i "s/CELERYD_GROUP='celery'/CELERYD_GROUP='$CELERYD_GROUP'/g"  /etc/default/newfies-celeryd
            chmod +x /etc/default/newfies-celeryd
            chmod +x /etc/init.d/newfies-celeryd

            /etc/init.d/newfies-celeryd restart
            cd /etc/init.d; update-rc.d newfies-celeryd defaults 99

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
        'CENTOS')
            # Add init-scripts
            cp /usr/src/newfies-dialer/install/celery-init/centos/etc/default/newfies-celeryd /etc/default/
            cp /usr/src/newfies-dialer/install/celery-init/centos/etc/init.d/newfies-celeryd /etc/init.d/
            # Configure init-scripts
            sed -i "s/CELERYD_USER='celery'/CELERYD_USER='$CELERYD_USER'/g"  /etc/default/newfies-celeryd
            sed -i "s/CELERYD_GROUP='celery'/CELERYD_GROUP='$CELERYD_GROUP'/g"  /etc/default/newfies-celeryd

            chmod +x /etc/init.d/newfies-celeryd
            /etc/init.d/newfies-celeryd restart

            chkconfig --add newfies-celeryd
            chkconfig --level 2345 newfies-celeryd on
        ;;
    esac

    echo ""
    echo ""
    echo "**************************************************************"
    echo "Congratulations, Newfies-Dialer Backend is now installed!"
    echo "**************************************************************"
    echo ""
    echo "Thank you for installing Newfies-Dialer"
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

#Menu Section for Script
show_menu_newfies() {
	clear
	echo " > Newfies-Dialer Installation Menu"
	echo "====================================="
	echo "	1)  Install All"
	echo "	2)  Install Newfies-Dialer Web Frontend"
	echo "	3)  Install Newfies-Dialer Backend / Celery"
	echo "	0)  Quit"
	echo -n "(0-3) : "
	read OPTION < /dev/tty
}


# * * * * * * * * * * * * Start Script * * * * * * * * * * * *

#Identify the OS
func_identify_os

#Prepare settings for installation
case $DIST in
    'DEBIAN')
        SCRIPT_VIRTUALENVWRAPPER="/usr/local/bin/virtualenvwrapper.sh"
    ;;
    'CENTOS')
        SCRIPT_VIRTUALENVWRAPPER="/usr/bin/virtualenvwrapper.sh"
    ;;
esac

#Request the user to accept the license
func_accept_license

ExitFinish=0

while [ $ExitFinish -eq 0 ]; do

	# Show menu with Installation items
	show_menu_newfies

	case $OPTION in
		1)
			func_install_frontend
			func_install_landing_page
			func_install_backend
			echo done
		;;
		2)
			func_install_frontend
			func_install_landing_page
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

# Clean the system
#=================
# deactivate ; rm -rf /usr/share/newfies ; rm -rf /var/log/newfies ; rmvirtualenv newfies-dialer ; rm -rf /etc/init.d/newfies-celer* ; rm -rf /etc/default/newfies-celeryd ; rm /etc/apache2/sites-enabled/newfies.conf
