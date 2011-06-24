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
#wget --no-check-certificate https://github.com/Star2Billing/newfies/raw/master/scripts/install-celery.sh


#Variables
#comment out the appropriate line below to install the desired version
VERSION=master
#VERSION=v0.1.0
DATETIME=$(date +"%Y%m%d%H%M%S")
KERNELARCH=$(uname -p)
DISTRO='UBUNTU'


clear
echo ""
echo ""
echo "This will install Celery & Redis on your server"
echo "press any key to continue or CTRL-C to exit"
read TEMP

# APACHE CONF
APACHE_CONF_DIR="/etc/apache2/sites-enabled/"
#APACHE_CONF_DIR="/etc/httpd/conf.d/"

IFCONFIG=`which ifconfig 2>/dev/null||echo /sbin/ifconfig`
IPADDR=`$IFCONFIG eth0|gawk '/inet addr/{print $2}'|gawk -F: '{print $2}'`


#python setup tools
echo "Install Celery & redis-server..."
case $DISTRO in
        'UBUNTU')
            apt-get -y install redis-server
            pip install Celery
        ;;
        'CENTOS')
            yum -y install redis-server
            pip install Celery
        ;;
esac


#get redis
echo "Configure redis..."

#ln -s /usr/src/newfies/newfies /usr/share/django_app/newfies

CARROT_BACKEND = "ghettoq.taproot.Redis" # "redis"
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_VHOST = "0"
CELERY_RESULT_BACKEND = "redis"

# Redis Settings
sed -i "s/CARROT_BACKEND = 'ghettoq.taproot.Redis'/CARROT_BACKEND = \'$CARROT_BACKEND\'/g"  /usr/share/django_app/newfies/settings.py
sed -i "s/BROKER_HOST = 'localhost'/BROKER_HOST = \'$REDIS_HOST\'/g"  /usr/share/django_app/newfies/settings.py
sed -i "s/BROKER_PORT = 6379/BROKER_PORT = \'$REDIS_PORT\'/g"  /usr/share/django_app/newfies/settings.py
sed -i "s/BROKER_VHOST = 0/BROKER_VHOST = \'$REDIS_VHOST\'/g"  /usr/share/django_app/newfies/settings.py
sed -i "s/CELERY_RESULT_BACKEND = 'redis'/CELERY_RESULT_BACKEND = \'$CELERY_RESULT_BACKEND\'/g"  /usr/share/django_app/newfies/settings.py

sed -i "s/REDIS_HOST = 'localhost'/REDIS_HOST = \'$REDIS_HOST\'/g"  /usr/share/django_app/newfies/settings.py
sed -i "s/REDIS_PORT = 6379/REDIS_PORT = \'$REDIS_PORT\'/g"  /usr/share/django_app/newfies/settings.py
sed -i "s/REDIS_VHOST = 0/REDIS_VHOST = \'$REDIS_VHOST\'/g"  /usr/share/django_app/newfies/settings.py








