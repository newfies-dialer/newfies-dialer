.. _SMS:

=================
SMS Configuration
=================

Configuration
=============

SMS braodcasting is supported as standard by Newfies-Dialer, allowing Newfies-Dialer to send out thousands or millions of SMS messages to  contacts.

The SMS gateway supports the following gateways, Clickatell (http://www.clickatell.com/) and SMS Global (http://www.smsglobal.com). Additionally, Khomp hardware is suuported to allow the use of SIM cards in house. See http://www.khomp.com.br/ for more details.


Go to the Admin interface and identify the SMS Gateway section, and click on Gateways. Listed by default are three gateways, Clickatell, SMS Global and Khomp. Those that you don't want to be configured can be deleted.

Click the gateway to be configured and edit the pre-filled settings and populate the fields with the credentials supplied by your SMS provider:

Clickatell
----------

Clickatell settings

{
  "api_id": "_API_ID_", 
  "password": "_PASSWORD_",
  "from": "_SENDER_ID_", 
  "user": "_USERNAME_", 
  "concat": "3"
}

Edit _API_ID_, _Sender_ID_, _USERNAME_ and _PASSWORD_  to the credentials provided by Clickatell and leave everything else as it is, and click save.

SMS Global
----------

The default settings are as follows:

{
  "from": "_SENDER_ID_", 
  "maxsplit": "3", 
  "api": 1, 
  "user": "_USERNAME_", 
  "action": "sendsms", 
  "password": "_PASSWORD_"
}

Edit _Sender_ID_, _USERNAME_ and _PASSWORD_ to match the credetials issued by SMS Global, leave everything else unchanged and save.

Khomp
-----

Documentation to follow.


Messages
========

The messages section in the admin screens shows the status of the messages, e.g. success or failure as well as the status message.

Providers
=========

Documentation to follow.

Replies
=======

Documentation to follow.





