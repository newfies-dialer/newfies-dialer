


#Menu Section for Script
show_menu_newfies() {
    clear
    echo " > Newfies-Dialer Installation Menu"
    echo "====================================="
    echo "  1)  Install All"
    echo "  2)  Install Newfies-Dialer Web Frontend"
    echo "  3)  Install Newfies-Dialer Backend / Celery"
    echo "  0)  Quit"
    echo -n "(0-3) : "
    read OPTION < /dev/tty
}


# * * * * * * * * * * * * Start Script * * * * * * * * * * * *

#Identify the OS
func_identify_os

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