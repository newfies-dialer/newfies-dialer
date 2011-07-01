#!/bin/sh
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

# To download this script direct to your server type
#wget --no-check-certificate https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-newfies.sh
#
#TODO: 
# - Support Virtualenv
# - Memcache installation
# - Input mysql username / password when running script
# - Option to install with SQLite
# - Copy files, do not link to source


#Variables
VERSION=master
DATETIME=$(date +"%Y%m%d%H%M%S")
KERNELARCH=$(uname -p)
DISTRO='UBUNTU'
INSTALL_DIR='/usr/share/django_app/newfies'
DATABASENAME=newfies
MYSQLUSER=root
MYSQLPASSWORD=passw0rd

CELERYD_USER="celery"
CELERYD_GROUP="celery"
#------------------------------------------------------------------------------------


#Function to install Frontend
func_install_frontend(){

echo ""
echo ""
echo "This will install Web Newfies on your server"
echo "press any key to continue or CTRL-C to exit"
read TEMP


IFCONFIG=`which ifconfig 2>/dev/null||echo /sbin/ifconfig`
IPADDR=`$IFCONFIG eth0|gawk '/inet addr/{print $2}'|gawk -F: '{print $2}'`


#python setup tools
echo "Install Dependencies and python modules..."
case $DISTRO in
    'UBUNTU')
        # SET APACHE CONF
        APACHE_CONF_DIR="/etc/apache2/sites-enabled/"

        apt-get -y install python-setuptools python-dev build-essential 
        apt-get -y install libapache2-mod-python libapache2-mod-wsgi
        easy_install pip
        easy_install virtualenv
        #ln -s /usr/local/bin/pip /usr/bin/pip
        
        #Install Extra dependencies on New OS
        apt-get -y install mysql-server libmysqlclient-dev
        apt-get -y install git-core
        apt-get -y install mercurial
        #apt-get -y install python-importlib - does not exist in repository
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
    ;;
esac


if [ -d "$INSTALL_DIR" ]; then
    # Newfies is already installed
    echo ""
    echo ""
    echo "We detect an existing Newfies Installation"
    echo "if you continue the existing installation will be removed!"
    echo ""
    echo "press any key to continue or CTRL-C to exit"
    read TEMP

    mkdir /tmp/old-newfies-dialer_$DATETIME
    mv $INSTALL_DIR /tmp/old-newfies-dialer_$DATETIME
    
    mysqldump -u $MYSQLUSER --password=$MYSQLPASSWORD $DATABASENAME > /tmp/old-newfies-dialer_$DATETIME.mysqldump.sql
    
    echo "Files from $INSTALL_DIR has been moved to /tmp/old-newfies-dialer_$DATETIME"
    echo "Mysql Dump of database $DATABASENAME added in /tmp/old-newfies-dialer_$DATETIME.mysqldump.sql"
    echo "press any key to continue"
    read TEMP
fi


#get Newfies
echo "Install Newfies..."
mkdir /usr/share/django_app/
cd /usr/src/
wget --no-check-certificate https://github.com/Star2Billing/newfies-dialer/tarball/$VERSION
mv master Star2Billing-newfies-dialer-$VERSION.tar.gz
tar xvzf Star2Billing-newfies-dialer-*.tar.gz
rm -rf Star2Billing-newfies-*.tar.gz
mv newfies-dialer newfies-dialer_$DATETIME
mv Star2Billing-newfies-* newfies-dialer
ln -s /usr/src/newfies-dialer/newfies $INSTALL_DIR


#Install Newfies depencencies
pip install -r /usr/src/newfies-dialer/install/conf/requirements.txt

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


# Setup settings.py
sed -i "s/'django.db.backends.sqlite3'/'django.db.backends.mysql'/"  $INSTALL_DIR/settings_local.py
sed -i "s/.*'NAME'/       'NAME': '$DATABASENAME',#/"  $INSTALL_DIR/settings_local.py
sed -i "/'USER'/s/''/'$MYSQLUSER'/" $INSTALL_DIR/settings_local.py
sed -i "/'PASSWORD'/s/''/'$MYSQLPASSWORD'/" $INSTALL_DIR/settings_local.py
sed -i "/'HOST'/s/''/'localhost'/" $INSTALL_DIR/settings_local.py
sed -i "/'PORT'/s/''/'3306'/" $INSTALL_DIR/settings_local.py


# Create the Database
echo "Remove Existing Database if exists..."
echo "mysql --user=$MYSQLUSER --password=$MYSQLPASSWORD -e 'DROP DATABASE $DATABASENAME;'"
mysql --user=$MYSQLUSER --password=$MYSQLPASSWORD -e "DROP DATABASE $DATABASENAME;"

echo "Create Database..."
echo "mysql --user=$MYSQLUSER --password=$MYSQLPASSWORD -e 'CREATE DATABASE $DATABASENAME CHARACTER SET UTF8;'"
mysql --user=$MYSQLUSER --password=$MYSQLPASSWORD -e "CREATE DATABASE $DATABASENAME CHARACTER SET UTF8;"

cd $INSTALL_DIR/
#following line is for SQLite
mkdir database
python manage.py syncdb --noinput
#python manage.py migrate
echo ""
echo ""
echo "Create a super admin user..."
python manage.py createsuperuser


#Collect static files from apps and other locations in a single location.
python manage.py collectstatic -l --noinput


# prepare Apache
echo "Prepare Apache configuration..."
echo '
Listen *:9080

<VirtualHost *:9080>
    DocumentRoot '$INSTALL_DIR'/
    ErrorLog /var/log/err-apache-newfies.log
    LogLevel warn

    WSGIPassAuthorization On
    WSGIDaemonProcess newfies user=www-data user=www-data threads=25
    WSGIProcessGroup newfies
    WSGIScriptAlias / '$INSTALL_DIR'/django.wsgi

    <Directory '$INSTALL_DIR'>
        Order deny,allow
        Allow from all
    </Directory>

</VirtualHost>


' > $APACHE_CONF_DIR/newfies.conf
#correct the above file
sed -i "s/@/'/g"  $APACHE_CONF_DIR/newfies.conf


#Fix permission on python-egg
mkdir $INSTALL_DIR/.python-eggs
chmod 777 $INSTALL_DIR/.python-eggs

case $DISTRO in
    'UBUNTU')
        chown -R www-data.www-data $INSTALL_DIR/database/
        service apache2 restart
    ;;
    'CENTOS')
        service httpd restart
    ;;
esac


echo ""
echo ""
echo "Installation Web Newfies Completed"
echo ""
echo ""
echo "Please log on to Newfies at "
echo "http://$IPADDR:9080"
echo "the username and password are the ones you entered during this installation."
echo ""
echo "Thank you for installing Newfies"
echo "Yours"
echo "The Star2Billing Team"
echo "http://www.star2billing.com and http://www.newfies-dialer.org/"
}


#Function to install backend
func_install_backend() {

echo ""
echo ""
echo "This will install Newfies Backend, Celery & Redis on your server"
echo "press any key to continue or CTRL-C to exit"
read TEMP

IFCONFIG=`which ifconfig 2>/dev/null||echo /sbin/ifconfig`
IPADDR=`$IFCONFIG eth0|gawk '/inet addr/{print $2}'|gawk -F: '{print $2}'`


#Install Celery & redis-server
echo "Install Redis-server ..."
func_install_redis_server

#Install Celery
pip install Celery


echo ""
echo "Configure Celery..."

# Add init-scripts
cp /usr/src/newfies-dialer/install/celery-init/etc/default/celeryd /etc/default/
cp /usr/src/newfies-dialer/install/celery-init/etc/init.d/celeryd /etc/init.d/
cp /usr/src/newfies-dialer/install/celery-init/etc/init.d/celerybeat /etc/init.d/

# Configure init-scripts
sed -i "s/CELERYD_USER='celery'/CELERYD_USER='$CELERYD_USER'/g"  /etc/default/celeryd
sed -i "s/CELERYD_GROUP='celery'/CELERYD_GROUP='$CELERYD_GROUP'/g"  /etc/default/celeryd

chmod +x /etc/default/celeryd
chmod +x /etc/init.d/celeryd
chmod +x /etc/init.d/celerybeat

#Debug
#python $INSTALL_DIR/manage.py celeryd -E -B -l debug

/etc/init.d/celeryd start

/etc/init.d/celerybeat start

echo ""
echo ""
echo "Installation Newfies Backend Complete"
echo ""
echo ""
echo "Thank you for installing Newfies"
echo "Yours"
echo "The Star2Billing Team"
echo "http://www.star2billing.com and http://www.newfies-dialer.org/"
}


#Install recent version of redis-server
func_install_redis_server() {
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

#Start redis-server
/etc/init.d/redis-server start
}


#Menu Section for Script
show_menu_newfies() {
	clear
	echo " > Newfies Installation Menu (Ubuntu)"
	echo "====================================="
	echo "	1)  All"
	echo "	2)  Newfies Web Frontend"
	echo "	3)  Newfies Backend / Celery"
	echo "	0)  Quit"
	echo -n "(0-3) : "
	read OPTION < /dev/tty
	echo $OPTION
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
			func_install_web
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
