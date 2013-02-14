.. _install-configure-freeswitch:

Freeswitch Installation and configuration
=========================================

Freeswitch is the telephony engine used by Newfies-Dialer to make calls, as well as broadcast voice applications

Newfies-Dialer communicates with Freeswitch though the Event-Socket. Communication is made via the Event Socket Library `ESL`_.
We have some Freeswitch dependencies, therefore the following modules will need to be installed ::

    mod_curl, asr_tts, mod_flite, asr_tts, mod_shout, mod_dingaling, mod_shell_stream, mod_xml_cdr


A script for Freeswitch Installation which will install Freeswitch with the required modules and configure it for you is available.

Download and run the Freeswitch installation script.

Once logged in as root, execute the following command::

    wget https://raw.github.com/Star2Billing/newfies-dialer/master/install/install-freeswitch.sh


The above commmand download the installation script. We can then execute the script with the following command::

    bash install-freeswitch.sh

This will download and install Freeswitch with the modules appropriate for Newfies-Dialer. The installation will take some time, but does not require your interaction once started.


.. _`Freeswitch`: http://www.freeswitch.org/
.. _`ESL`: http://wiki.freeswitch.org/wiki/Event_Socket_Library
