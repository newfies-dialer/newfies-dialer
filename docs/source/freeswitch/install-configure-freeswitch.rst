
.. _freeswitch:

==========
FreeSwitch
==========


.. _install-configure-freeswitch:

Installation and configuration
==============================

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


.. _trunk-configuration:

Trunk configuration
===================


In order for Newfies-Dialer to make outbound calls to its subscribers, you will need a SIP trunk. The Freeswitch wiki can provide more information on configuring trunks. However creating a trunk simply for Newfies-Dialer is straightforward.

Trunks or gateways, as they are known in Freeswitch, are configured using XML syntax, so using your favourite text editor, while logged in as root “sudo su -” create an XML file in /usr/local/freeswitch/conf/sip_profiles/external/ and give it an identifiable name, e.g. call-labs.xml, and place the following lines in the file::

    <include>
    <gateway name="ip address or hostname of carrier">
    <!--/// account username *required* ///-->
    <param name="username" value="your username provided by carrier"/>
    <!--/// auth realm: *optional* same as gateway name, if blank ///-->
    <!--<param name="realm" value="asterlink.com"/>-->
    <!--/// username to use in from: *optional* same as username, if blank ///-->
    <param name="from-user" value="your username provided by carrier"/>
    <!--/// domain to use in from: *optional* same as realm, if blank ///-->
    <!--param name="from-domain" value=""/-->
    <!--/// account password *required* ///-->
    <param name="password" value="your password supplied by carrier"/>
    <!--/// extension for inbound calls: *optional* same as username, if blank ///-->
    <!--<param name="extension" value="cluecon"/>-->
    <!--/// proxy host: *optional* same as realm, if blank ///-->
    <!--<param name="proxy" value="asterlink.com"/>-->
    <!--/// send register to this proxy: *optional* same as proxy, if blank ///-->
    <!--<param name="register-proxy" value="mysbc.com"/>-->
    <!--/// expire in seconds: *optional* 3600, if blank ///-->
    <!--<param name="expire-seconds" value="60"/>-->
    <!--/// do not register ///-->
    <param name="register" value="true"/>
    <!-- which transport to use for register -->
    <!--<param name="register-transport" value="udp"/>-->
    <!--How many seconds before a retry when a failure or timeout occurs -->
    <!--<param name="retry-seconds" value="30"/>-->
    <!--Use the callerid of an inbound call in the from field on outbound calls via this gateway -->
    <!--<param name="caller-id-in-from" value="false"/>-->
    <!--extra sip params to send in the contact-->
    <!--<param name="contact-params" value="tport=tcp"/>-->
    <!--send an options ping every x seconds, failure will unregister and/or mark it down-->
    <!--<param name="ping" value="25"/>-->
    </gateway>
    </include>


The uncommented lines are almost certainly required by your carrier and Freeswitch, the remaining parameters can be uncommented and used, if required by your carrier. The XML syntax for comments are denoted by lines that begin “ <!-- “ and end in “--> “.

Finally we need to load the new configuration, and check the trunk is registered.
Enter the Freeswitch CLI (Command Line Interface) from the console::

    /usr/local/freeswitch/bin/fs_cli


You should now see the Freeswitch CLI, so now reload the Freeswitch configuration with the following command: (tip; Tab auto-completes)::

    sofia profile external restart reloadxml


When complete, check the trunk has registered with the command::

    sofia status


Against the name of the trunk you configured in the XML file, you should see REGED (registered) at the end of the line. Take a note of the trunk name, we are going to need it for telling Newfies-Dialer that it can use this trunk.

To exit the Freeswitch CLI, do CTRL D, or /exit

Freeswitch configuration is now complete.
