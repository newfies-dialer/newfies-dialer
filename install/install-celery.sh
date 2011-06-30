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
#wget --no-check-certificate https://github.com/Star2Billing/newfies-dialer/raw/master/scripts/install-celery.sh


#Variables
#comment out the appropriate line below to install the desired version
#VERSION=master
#VERSION=v0.1.0
#DATETIME=$(date +"%Y%m%d%H%M%S")
#KERNELARCH=$(uname -p)
DISTRO='UBUNTU'


clear
echo ""
echo ""
echo "This will install Celery & Redis on your server"
echo "press any key to continue or CTRL-C to exit"
read TEMP

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

# copy settings_local.py into newfies dir
cp /usr/share/django_app/newfies-dialer/install/conf/settings_local.py /usr/share/django_app/newfies-dialer/newfies/

#get redis
echo "Configure redis..."

CARROT_BACKEND='ghettoq.taproot.Redis'
REDIS_HOST='localhost'
REDIS_PORT=6379
REDIS_VHOST=0
CELERY_RESULT_BACKEND="redis"

# Redis Settings
sed -i "s/CARROT_BACKEND = 'redis'/CARROT_BACKEND = \'$CARROT_BACKEND\'/g"  /usr/share/django_app/newfies-dialer/newfies/settings_local.py
sed -i "s/BROKER_HOST = 'localhost'/BROKER_HOST = \'$REDIS_HOST\'/g"  /usr/share/django_app/newfies-dialer/newfies/settings_local.py
sed -i "s/BROKER_PORT = 6379/BROKER_PORT = \$REDIS_PORT\/g" /usr/share/django_app/newfies-dialer/newfies/settings_local.py
sed -i "s/BROKER_VHOST = 0/BROKER_VHOST = \$REDIS_VHOST\/g"  /usr/share/django_app/newfies-dialer/newfies/settings_local.py
sed -i "s/CELERY_RESULT_BACKEND = 'redis'/CELERY_RESULT_BACKEND = \'$CELERY_RESULT_BACKEND\'/g"  /usr/share/django_app/newfies-dialer/newfies/settings_local.py

sed -i "s/REDIS_HOST = 'localhost'/REDIS_HOST = \'$REDIS_HOST\'/g"  /usr/share/django_app/newfies-dialer/newfies/settings_local.py
sed -i "s/REDIS_PORT = 6379/REDIS_PORT = \$REDIS_PORT\/g"  /usr/share/django_app/newfies-dialer/newfies/settings_local.py
sed -i "s/REDIS_VHOST = 0/REDIS_VHOST = \'$REDIS_VHOST\'/g"  /usr/share/django_app/newfies-dialer/newfies/settings_local.py


cp /usr/share/django_app/newfies-dialer/install/celery-init/etc/default/celeryd /etc/default/
cp /usr/share/django_app/newfies-dialer/install/celery-init/etc/init.d/celeryd /etc/init.d/
cp /usr/share/django_app/newfies-dialer/install/celery-init/etc/init.d/celerybeat /etc/init.d/


CELERYD_CHDIR="/usr/share/django_app/newfies-dialer/newfies/"
CELERYD="/usr/share/django_app/newfies-dialer/newfies/manage.py celeryd"
CELERYD_OPTS="--time-limit=300"
CELERY_CONFIG_MODULE="celeryconfig"
CELERYD_USER="celery"
CELERYD_GROUP="celery"

sed -i "s/CELERYD_CHDIR='/path/to/newfies/'/CELERYD_CHDIR=\'$CELERYD_CHDIR\'/g"  /etc/default/celeryd
sed -i "s/CELERYD='/path/to/newfies/manage.py celeryd'/CELERYD=\'$CELERYD\'/g"  /etc/default/celeryd
sed -i "s/CELERYD_OPTS='--time-limit=300'/CELERYD_OPTS=\'$CELERYD_OPTS\'/g"  /etc/default/celeryd
sed -i "s/CELERY_CONFIG_MODULE='celeryconfig'/CELERY_CONFIG_MODULE=\'$CELERY_CONFIG_MODULE\'/g"  /etc/default/celeryd
sed -i "s/CELERYD_USER='celery'/CELERYD_USER=\'$CELERYD_USER\'/g"  /etc/default/celeryd
sed -i "s/CELERYD_GROUP='celery'/CELERYD_GROUP=\'$CELERYD_GROUP\'/g"  /etc/default/celeryd


# Path to celerybeat
CELERYBEAT="/usr/share/django_app/newfies-dialer/newfies/manage.py celerybeat"
CELERYBEAT_OPTS="--schedule=/var/run/celerybeat-schedule"

sed -i "s/CELERYBEAT='/path/to/newfies/manage.py celerybeat'/CELERYBEAT=\'$CELERYBEAT\'/g"  /etc/default/celeryd
sed -i "s/CELERYBEAT_OPTS='--schedule=/var/run/celerybeat-schedule'/CELERYBEAT_OPTS=\'$CELERYBEAT_OPTS\'/g"  /etc/default/celeryd

chmod 777 /etc/default/celeryd
chmod 777 /etc/init.d/celeryd
chmod 777 /etc/init.d/celerybeat

python manage.py celeryd -E -B -l debug

/etc/init.d/celeryd start

/etc/init.d/celerybeat start

clear
echo "Installation Complete"
echo ""
echo ""
echo "Thank you for installing Newfies"
echo "Yours"
echo "The Star2Billing Team"
echo "http://www.star2billing.com and http://www.newfies.org/"
