.. _beginners-guide:

================
Beginner’s Guide
================

.. contents::
    :local:
    :depth: 2

.. _beginners-guide-introduction:

Introduction
============

This is a simple step-by-step guide for installation of the necessary components to install Newfies-Dialer. It covers the installation of the operating system, Freeswitch and Newfies-Dialer along with all the dependencies, followed by setting off the first Newfies-Dialer campaign, and can be achieved in under one hour, given suitably quick broadband.

.. raw:: html

    <iframe width="640" height="480" src="https://www.youtube.com/embed/MBuy76bsg1Y" frameborder="0" allowfullscreen></iframe>



.. _beginners-guide-server-spec:

Server Specification for Newfies-Dialer
=======================================

As a minimum, we recommend a server with 2Gb of RAM and at least 20Gb of hard drive space with a 64 bit architecture. This will be sufficient to test Newfies-Dialer. However, for best performance a highly specified server would be better with good IO suggesting SSD, RAID 0 or RAID 10, plenty of RAM and multiple processors.

The capacity of the system is not limited by the software, but by the hardware dedicated to Newfies-Dialer, and the way that the software is tuned to take best advantage of the given hardware. We offer a tuning and optimisation service(http://www.newfies-dialer.org/add-ons/acceleration-and-optimisation-service/) which can make some dramatic improvements to performance.

Factors affecting performance include, but are not limited to:

 * Duration of call
 * Number of people who answer
 * RAM
 * Processor
 * IO Speeds
 * Complexity of the survey
 * Answering Machine Detection
 * Beep Detection
 * Other processes in the OS

The capacity of your Newfies-Dialer server can only be determined accurately with benchmarking.

As a rule of thumb, if you are looking for more than 1000 concurrent calls, then we would recommend a multi-server installation consisting of one database and web server and multiple Freeswitch systems to make the calls. See http://www.newfies-dialer.org/pricing/high-capacity-multi-server-system/ for more details.


.. _beginners-guide-operating-system:

Operating System Installation
=============================

We recommend that you use Debian 7.X or 8.x 64 bit server, with only SSH installed; This document is written with this in mind.  It is available at http://www.debian.org/distrib/

*Please note that the Newfies-Dialer install scripts are only designed to work on Debian 7.X and 8.x (64 bit)*

Burn the image to CD, and install onto your hardware. The installation of Debian is straight forward and simple. The only package to install is SSH Server so that you can manage the server from your desktop PC or Mac. All other packages will be installed by Star2Billing’s Newfies-Dialer installation scripts.

When Debian is installed, it maybe worthwhile installing the latest patches and updates. This is achieved with the following commands:
::

    sudo apt-get update
    sudo apt-get upgrade


A reboot after major updates is recommended, type "reboot" at the command line.


.. _beginners-guide-complete-installation:

Complete Installation
=====================

We have provided automated scripts that installs Newfies-Dialer on your Server and includes all the dependencies such as Freeswitch, Celery and Redis.

 * Freeswitch is the telephony engine used by Newfies-Dialer to make calls, as well as play voice applications
 * Celery is the task queuing system.
 * Redis is the task messaging system

Once Debian 7.x is installed, log in as root, then download and run the install-all.sh installation script, by executing the following command:
::

    wget --no-check-certificate http://bit.ly/newfies-dialer-installer -O install-all.sh
    bash install-all.sh


The installation will prompt you to install Freeswitch, press enter. this will download and install Freeswitch with the modules appropriate for Newfies-Dialer. The installation will take some time, but does not require your interaction once started.

Finally, the Newfies-Dialer selection menu will appear.


.. _beginners-guide-installation:

Newfies-Dialer Installation
===========================

Newfies-Dialer is the management and control system providing a web interface for admin and customers alike, to manage the platform, subscribers and voice broadcast campaigns.

The installation script will prompt you as to what you want to install. For this guide, we chose the option to install all.

At points during the installation, you will be prompted to press enter to continue, with a short explanation of what is happening next. Just press enter for the defaults.

You will be prompted to create a superuser. Accept root, enter your email address, and your chosen password, twice. This will be the username and password you use to log on to the Newfies-Dialer web interface.

Once installed, the system will then prompt you to continue with the installation and install the backend processes. Press enter to continue. On completion, the script will return to the original Newfies-Dialer install menu. Exit the menu.

We can now reboot to ensure that, on startup, all required services are running. Type "reboot" at the command line. We don’t need to type "sudo reboot" as mentioned earlier, because we are already logged in as root.

On reboot log into the new system via your web browser to check that everything is working. Type http://<<IP-ADDRESS>>:8008 into your web browser’s address bar where <<IP-ADDRESS>> is the IP address or hostname of your Newfies-Dialer platform. If you have followed the instructions above, you should be able to login using the username and password you created during the installation.

The scripts are well tested, and there is no reason for them to fail provided you have followed the instructions and you have Internet access. If things have not gone well, and you cannot log on, re-read the instructions and check you have internet access and DNS resolution.


.. _beginners-guide-freeswitch-trunk-configuration:

Freeswitch Trunk configuration
==============================

NB: See the video at the top of the page for an overview of the initial configuration of Newfies-Dialer.

In order for Newfies-Dialer to make outbound calls to its subscribers, you will need a SIP trunk. The Freeswitch wiki can provide more information on configuring trunks. However creating a trunk simply for Newfies-Dialer is straightforward.

Trunks or gateways, as they are known in Freeswitch, are configured using XML syntax, so using your favourite text editor, while logged in as root "sudo su -" create an XML file in /etc/freeswitch/sip_profiles/external/ and give it an identifiable name, e.g. call-labs.xml, and place the following lines in the file.
::

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

The lines in bold are almost certainly required by your carrier and Freeswitch, the remaining parameters can be uncommented and used, if required by your carrier. The XML syntax for comments are denoted by lines that begin " <!– " and end in "–> ".

Finally we need to load the new configuration, and check the trunk is registered.
The Freeswitch console is accessed by typing "fs_cli" at the command prompt. The logging level can be increased or decreased from level 0 to level 7. to switch off logging, type /log 0 at the Freeswitch console, followed by enter. For the greatest verbosity, type /log 7 followed by enter.

Type "fs_cli" followed by enter.

You should now see the Freeswitch CLI, so now reload the Freeswitch configuration with the following command: (tip; Tab auto-completes)
::

    sofia profile external restart reloadxml


When complete, check the trunk has registered with the following command.
::

    sofia status


Against the name of the trunk you configured in the XML file, you should see REGED (registered) at the end of the line. Take a note of the trunk name, we are going to need it for telling Newfies-Dialer that it can use this trunk.

To exit the Freeswitch CLI, do CTRL D, or /exit

Freeswitch configuration is now complete.


.. _beginners-guide-newfies-dialer-configuration:

Newfies-Dialer Configuration
============================

For demonstration purposes, we are going to configure one standard voice application supplied with Newfies-Dialer, using the root user, to call only one person.

We are going to use the admin interface to tell Newfies-Dialer about the gateway we have configured in Freeswitch and set the  maximum parameters for a customer such as their allowed dial rate, maximum number of campaigns, etc.


Set Hostname
------------

Some of the features of Newfies-Dialer are dependent on the hostname or IP address, so this has to be set correctly in site address.

In the Admin dashboard, locate the "Sites" link and click change. By default, there will be an entry of "example.com". Edit this setting to reflect the hostname of the server, or if you do not have this set up, the IP address. e.g.  http://www.domain.tld:8008 or in the case of an IP address, something like http://192.168.1.200:8008


Newfies-Dialer’s Gateway
------------------------

Log into the Newfies-Dialer interface using your root username and password previously created in these instructions.

Click Admin, and locate and enter the "Dialer Gateways" panel on the dashboard, then add a dialer gateway. Only the fields in bold need to be filled in. That is to say, the name of gateway, for identification, and the Gateway’s field, e.g.
::

    sofia/gateway/myprovider/


"myprovider" is the name of the gateway which you can take from the gateway name when you typed "sofia status" when configuring the Freeswitch Gateway. Finally, check the status is active, and save. The trunk should now appear in the gateway list.


Dialer Settings
---------------

Each customer, including the root user, needs to have Dialer Settings and trunks associated with their account. These set the limit to which each customer can utilise Newfies-Dialer in terms of trunks, calls per minute, call duration, subscribers and campaigns, as well as blacklisting or whitelisting phone numbers.

In the Admin Dashboard, locate the Dialer Settings, and click Add, in the name, put "DS1" and, for the moment, leave the default settings as they are, then save them.

The Dialer Settings have to be associated with the customer’s account. For the purposes of this demonstration, we are using the root user.  In production, you would apply these settings to the customers.

In the Admin dashboard, click Admins, then root. Scroll to the bottom of the page.

 * Optionally add an accountcode, which can be used for billing in an external billing application to identify the customer from the CDR. The accountcode must be numerical.
 * Select which Dialer Settings apply to this customer, in this case "DS1"
 * Select which gateway(s) this customer is allowed to use.

Finally, click save.

NB: Everything above this is covered at the video at the top of the page, from configuring FreeSWITCH to apply Dialer Settings.


.. _beginners-guide-customer-portal:

Customer Portal
===============

Now we are going to use the customer’s portal to create phonebooks containing subscribers to call, configure a survey, add campaign, and start the outbound voice broadcast. These should always be done from the Customer Portal and not from the Admin Interface. To proceed, click "Customer Panel" at the top of Admin interface.


Create Phonebook
----------------

The phonebook is where lists of subscribers are grouped. Click Customer Panel on the top menu in the Admin Dashboard, then click Phonebook, and add a new phonebook.

Create a new phonebook called, for the purposes of the exercise, PB1, and give it a description.


Add Contacts
------------

Click contact, and add a new contact. As a minimum add a phone number to call in the Contact field, and for the purposes of this demonstration, enter your own telephone number in the format that your carrier expects it. Click Submit.

Repeat as necessary until you have your test numbers added.


Add Survey
----------

Next we are going to configure the survey that will be executed when Newfies-Dialer calls your phone and you answer. Click Modules, Survey, then click add. As is traditional with first steps, we will call this survey "Hello World".

The aim is that Newfies-Dialer will call you, and when you answer, Newfies-Dialer will broadcast "Hello World" to you using the text to speech engine in Freeswitch.

Click "Add Section" and select "Play Message", enter "Hello World" in the section title. This is the speech that will be read out by the TTS engine. It can be edited later. When done, click save.

Best practice is that we should hangup, and mark the survey as complete, so click "Add Section" and select Hangup as the node type. Type "Goodbye" in the section title, and tick "Survey complete"

Next, set up the node branching. On the play message panel, click the branch icon, and select "Goodbye" as the next destination.

Finally, click Close Survey, and move on to configuring the campaign.


Configure Campaign
------------------

We now have all the components to create and run our campaign, so click campaign, and click add.

Give the Campaign a name, say "CPN Hello World", optionally, a description, set a caller ID to pass the called party,  select the A-Leg Gateway you configured earlier, the application, Hello World, and highlight the phonebook PB1, and submit. You will be returned to the list of campaigns.


Start The Campaign
------------------

We are now ready to launch the campaign, simply press the Play button against the CPN Hello World campaign.

In a few seconds, your campaign will launch, your phone will ring, and you will hear "Hello World" followed by "Goodbye" broadcast to you over the phone.


.. _beginners-guide-conclusion:

Conclusion
==========

This is a brief step by step instruction set of installing Newfies-Dialer, and making the first call. Please refer to the advanced documentation on the Newfies-Dialer and Freeswitch websites to cover more advanced topics, and begin implementing your own Voice Broadcast applications.

Star2Billing’s Support Team (newfies-dialer@star2billing.com) are on hand to provide one to one installation, support and tuition where required, and Star2Billing’s Development Team can be commissioned to build voice applications and integrate them with third party software and systems.

.. note:: As with all telephony systems, they are a valuable target on the internet, so before exposing any telephone system to the Internet, do ensure that you have done a security audit. Also note that in some countries, telemarketing, phone polling, and automated dialling is under regulatory control, and advice should be sought as to how best to remain within the limits of the law. First points of reference may be Ofcom in the UK and the Federal Trade Commission (FTC) in the USA.
