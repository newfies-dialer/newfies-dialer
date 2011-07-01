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
#wget --no-check-certificate https://github.com/Star2Billing/newfies/raw/master/scripts/install-newfies.sh


#Variables
#comment out the appropriate line below to install the desired version
VERSION=master
#VERSION=v0.1.0
DATETIME=$(date +"%Y%m%d%H%M%S")
KERNELARCH=$(uname -p)
DISTRO='UBUNTU'
INSTALL_DIR='/usr/share/django_app/newfies'

MYSQLUSER=root
MYSQLPASSWORD=passw0rd

clear
echo ""
echo ""
echo "This will install Newfies on your server"
echo "press any key to continue or CTRL-C to exit"
read TEMP

# APACHE CONF
APACHE_CONF_DIR="/etc/apache2/sites-enabled/"
#APACHE_CONF_DIR="/etc/httpd/conf.d/"

IFCONFIG=`which ifconfig 2>/dev/null||echo /sbin/ifconfig`
IPADDR=`$IFCONFIG eth0|gawk '/inet addr/{print $2}'|gawk -F: '{print $2}'`


#python setup tools
echo "Install Dependencies and python modules..."
case $DISTRO in
    'UBUNTU')
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
        yum -y install python-setuptools python-tools python-devel mod_python
        #Install PIP
        rpm -ivh http://download.fedora.redhat.com/pub/epel/5/i386/epel-release-5-4.noarch.rpm 
        # disable epel repository since by default it is enabled. It is not recommended to keep 
        # non standard repositories activated. Use it just in case you need.
        sed -i "s/enabled=1/enable=0/" /etc/yum.repos.d/epel.repo 
        yum --enablerepo=epel install python-pip
    ;;
esac


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
pip install -r /usr/src/newfies-dialer/newfies/install/conf/requirements.txt

# copy settings_local.py into newfies dir
cp /usr/src/newfies-dialer/newfies/install/conf/settings_local.py $INSTALL_DIR

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
sed -i "s/.*'NAME'/       'NAME': 'newfies',#/"  $INSTALL_DIR/settings_local.py
sed -i "/'USER'/s/''/'$MYSQLUSER'/" $INSTALL_DIR/settings_local.py
sed -i "/'PASSWORD'/s/''/'$MYSQLPASSWORD'/" $INSTALL_DIR/settings_local.py
sed -i "/'HOST'/s/''/'localhost'/" $INSTALL_DIR/settings_local.py
sed -i "/'PORT'/s/''/'3306'/" $INSTALL_DIR/settings_local.py


# Create the Database
echo "Database Creation..."
cd $INSTALL_DIR/
mkdir database
chmod -R 777 database
python manage.py syncdb
#python manage.py migrate
python manage.py createsuperuser


#Collect static files from apps and other locations in a single location.
python manage.py collectstatic -l


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


clear
echo "Installation Complete"
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

