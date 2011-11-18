.. _how-to-use-it:

=========================
How to use Newfies-Dialer
=========================

Freeswitch Set-Up
-----------------
Configure trunks and gateways in Freeswitch by creating an XML file in 
/usr/local/freeswitch/conf/sip_profiles/external/ and give it an identifiable name, 
e.g. call-labs.xml, and place the following lines in the file, edited to suit your provider.

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

Then in the Freeswitch CLI (fs_cli) “sofia profile external restart reloadxml”. When the command is 
complete, check the gateway has registered with the command “sofia status”.

Create Gateway
-----------------
Having created the gateway in Freeswitch, Newfies-Dialer has to be told that it can use it. In 
admin,  add a new dialer gateway, e.g. sofia/gateway/myprovider/ (The final / is important) where 
“myprovider” is the gateway name setting used in above xml file in Freeswitch.

Only the fields in bold are compulsory.

.. _apply-dialer-settings:

Dialer Settings
---------------

Dialer settings are mapped with system users who are going to create campaigns & contacts. If dialer 
settings are not mapped to users, notifications & emails are sent to super admin user.

To create restrictions (like the Max. no of campaign, Max no of contacts etc.) for
system User, Click on ``Add dialer settings``. Add numeric values for the limit.

To apply the dialer settings limit on a system user, click on ``Customers`` or ``Admins`` 
in admin UI, select the user to update, & apply the settings from the dialer settings list.


.. _Voice App:

Create Voice Application
----------------------------

A number of voice applications are provided with Newfies-Dialer. Click ``Add VoIP App`` give the  
voice application a name, select the type of  application from the dropdown, select the gateway 
to use if the call is to be redirected, and provide the data to be used, e.g. in the case of “Speak” 
this would be the words to convert to text to speech.


.. _call-list:

Create call list
----------------

To create a call list, click on ``Add Phonebook``, add name of phonebook & its
description. Click on ``Contacts`` and add phone numbers in the contact list.
You can also import your call list from csv files, via clicking on
``Import contact``.


.. _campaign:

Create campaign
---------------

To create a campaign, click on ``Add campaign``, add details for the campaign.
Important: Add the campaign's start and end dates with times & week-day
exceptions. Select the gateway through which calls will be routed & the phonebook(s)
linked with the contacts.


.. _reach-to-contact:

Reach to contacts/subscribers
-----------------------------

A call-request will spool a call directly from the platform using a dialer gateway
and update the call-request status after receiving a response from the gateway.


.. _call-report:

VoIP Call Report
----------------

As per the status of a call-request, it will be stored in the VoIP call records.
This gives information of all the calls & call statistics made with the call-request
and also you can search for records on the basis of date range. You can export the VoIP
call report into a csv file.