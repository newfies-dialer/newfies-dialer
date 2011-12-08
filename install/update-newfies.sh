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


#Install mode can me either CLONE or DOWNLOAD
INSTALL_MODE='CLONE'
DATETIME=$(date +"%Y%m%d%H%M%S")
KERNELARCH=$(uname -p)
INSTALL_DIR='/usr/share/newfies'
DATABASENAME=$INSTALL_DIR'/database/newfies.db'
FS_INSTALLED_PATH=/usr/local/freeswitch
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


case $DIST in
    'DEBIAN')
        SCRIPT_VIRTUALENVWRAPPER="/usr/local/bin/virtualenvwrapper.sh"
        APACHE_USER="www-data"
        WSGI_ADDITIONAL=""
    ;;
    'CENTOS')
        SCRIPT_VIRTUALENVWRAPPER="/usr/bin/virtualenvwrapper.sh"
        APACHE_USER="apache"
        WSGI_ADDITIONAL="WSGISocketPrefix run/wsgi"
    ;;
esac


#Function to install Frontend
func_update_frontend(){

    echo ""
    echo ""
    echo "This script will update Newfies-Dialer on your server"
	echo "====================================================="
    echo ""
    
    if [ -d "$INSTALL_DIR" ]; then
        # Newfies is already installed
        echo ""
        echo ""
        echo "We detect an existing Newfies Installation"
        echo "We will now proceed on the upgrade"
        echo ""
        echo "Press Enter to continue or CTRL-C to exit"
        read TEMP
        
        echo "Update Newfies..."
        cd /usr/src/newfies-dialer/newfies
        git pull
        #Copy config and SQLite database
        cp $INSTALL_DIR/settings_local.py .
        cp -rf $INSTALL_DIR/database .

        #Backup files just in case
        mkdir /tmp/old-newfies-dialer_$DATETIME
        mv $INSTALL_DIR /tmp/old-newfies-dialer_$DATETIME
        echo "Files from $INSTALL_DIR has been moved to /tmp/old-newfies-dialer_$DATETIME"
        echo "Press Enter to continue"
        read TEMP
        
    else
        echo ""
        echo ""
        echo "We detect that Newfies-Dialer is not installed on your server at the standard path"
        echo "Sorry but we cannot continue with the upgrade!"
        echo ""
        exit 0
    fi
    
    # Install new copy of the files
    cp -r /usr/src/newfies-dialer/newfies $INSTALL_DIR
    
    # Activate virtualenv
    export WORKON_HOME=/usr/share/virtualenvs
    source $SCRIPT_VIRTUALENVWRAPPER
    workon $NEWFIES_ENV
    echo "Virtualenv $NEWFIES_ENV activated"
    
    
    echo "Update basic requirements..."
    for line in $(cat /usr/src/newfies-dialer/install/requirements/basic-requirements.txt)
    do
        pip install $line
    done
    echo "Update Django requirements..."
    for line in $(cat /usr/src/newfies-dialer/install/requirements/django-requirements.txt)
    do
        pip install $line
    done
    pip install plivohelper
    
    # Disable Debug
    sed -i "s/DEBUG = True/DEBUG = False/g"  $INSTALL_DIR/settings_local.py
    sed -i "s/TEMPLATE_DEBUG = DEBUG/TEMPLATE_DEBUG = False/g"  $INSTALL_DIR/settings_local.py
    
    
    cd $INSTALL_DIR/
    
    #Fix permission on python-egg
    mkdir /usr/share/newfies/.python-eggs
    chown $APACHE_USER:$APACHE_USER /usr/share/newfies/.python-eggs
    mkdir database
    
    python manage.py syncdb --noinput
    python manage.py migrate --all
    
    #Collect static files from apps and other locations in a single location.
    python manage.py collectstatic -l --noinput
    
    #Permission on database folder if we use SQLite    
    chown -R $APACHE_USER:$APACHE_USER $INSTALL_DIR/database/
    
    case $DIST in
        'DEBIAN')
            service apache2 restart
        ;;
        'CENTOS')
            service httpd restart
        ;;
    esac

    echo ""
    echo ""
    echo ""
    echo "**************************************************************"
    echo "Congratulations, Newfies Web Application is now updated!"
    echo "**************************************************************"
    echo ""
    echo "Please log on to Newfies at "
    echo "http://$IPADDR:$HTTP_PORT"
    echo "the username and password are the ones you entered during the first installation."
    echo ""
    echo "Thank you for updating Newfies"
    echo "Yours"
    echo "The Star2Billing Team"
    echo "http://www.star2billing.com and http://www.newfies-dialer.org/"
    echo
    echo "**************************************************************"
    echo ""
    echo ""
}


#Function to install backend
func_update_backend() {
    echo ""
    echo ""
    echo "This will update Newfies Backend, Celery & Redis on your server"
    echo "Press Enter to continue or CTRL-C to exit"
    read TEMP

    
    echo ""
    echo "Configure Celery..."

    
    case $DIST in
        'DEBIAN')
            # Add init-scripts
            cp /usr/src/newfies-dialer/install/celery-init/debian/etc/default/newfies-celeryd /etc/default/
            cp /usr/src/newfies-dialer/install/celery-init/debian/etc/init.d/newfies-celeryd /etc/init.d/
            #celerybeat script disabled
            #cp /usr/src/newfies-dialer/install/celery-init/debian/etc/init.d/newfies-celerybeat /etc/init.d/

            # Configure init-scripts
            sed -i "s/CELERYD_USER='celery'/CELERYD_USER='$CELERYD_USER'/g"  /etc/default/newfies-celeryd
            sed -i "s/CELERYD_GROUP='celery'/CELERYD_GROUP='$CELERYD_GROUP'/g"  /etc/default/newfies-celeryd

            chmod +x /etc/default/newfies-celeryd
            chmod +x /etc/init.d/newfies-celeryd
            #celerybeat script disabled
            #chmod +x /etc/init.d/newfies-celerybeat

            #Debug
            #python $INSTALL_DIR/manage.py celeryd -E -B -l debug

            /etc/init.d/newfies-celeryd restart
            #celerybeat script disabled
            #/etc/init.d/newfies-celerybeat restart
            
            cd /etc/init.d; update-rc.d newfies-celeryd defaults 99
            #celerybeat script disabled
            #cd /etc/init.d; update-rc.d newfies-celerybeat defaults 99
        ;;
        'CENTOS')
            # Add init-scripts
            cp /usr/src/newfies-dialer/install/celery-init/centos/etc/default/newfies-celeryd /etc/default/
            cp /usr/src/newfies-dialer/install/celery-init/centos/etc/init.d/newfies-celeryd /etc/init.d/
            #celerybeat script disabled
            #cp /usr/src/newfies-dialer/install/celery-init/centos/etc/init.d/newfies-celerybeat /etc/init.d/

            # Configure init-scripts
            sed -i "s/CELERYD_USER='celery'/CELERYD_USER='$CELERYD_USER'/g"  /etc/default/newfies-celeryd
            sed -i "s/CELERYD_GROUP='celery'/CELERYD_GROUP='$CELERYD_GROUP'/g"  /etc/default/newfies-celeryd

            chmod +x /etc/init.d/newfies-celeryd
            #celerybeat script disabled
            #chmod +x /etc/init.d/newfies-celerybeat

            #Debug
            #python $INSTALL_DIR/manage.py celeryd -E -B -l debug

            /etc/init.d/newfies-celeryd restart
            #celerybeat script disabled
            #/etc/init.d/newfies-celerybeat restart
            
            chkconfig --add newfies-celeryd
            chkconfig --level 2345 newfies-celeryd on
            
            #celerybeat script disabled
            #chkconfig --add newfies-celerybeat
            #chkconfig --level 2345 newfies-celerybeat on
        ;;
    esac

    echo ""
    echo ""
    echo ""
    echo "**************************************************************"
    echo "Congratulations, Newfies Backend is now updated!"
    echo "**************************************************************"
    echo ""
    echo ""
    echo "Thank you for updating Newfies"
    echo "Yours"
    echo "The Star2Billing Team"
    echo "http://www.star2billing.com and http://www.newfies-dialer.org/"
    echo
    echo "**************************************************************"
    echo ""
    echo ""
}



#Menu Section for Script
show_menu_newfies() {
	clear
	echo " > Newfies-Dialer Update Menu"
	echo "==============================="
	echo "	1)  Update All"
	echo "	2)  Update Newfies-Dialer Web Frontend"
	echo "	3)  Update Newfies-Dialer Backend / Newfies-Celery"
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
			func_update_frontend
			func_update_backend
			echo done
		;;
		2) 
			func_update_frontend
		;;
		3) 
			func_update_backend
		;;
		0)
		ExitFinish=1
		;;
		*)
	esac	
	
done



