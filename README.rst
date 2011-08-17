.. image:: https://github.com/Star2Billing/newfies-dialer/raw/master/newfies/resources/images/newfies.png


Newfies-Dialer is a free and open source voice broadcast application, which
can fulfil a variety of roles for a range of industries and organisations who
wish to contact large numbers of people by phone in a short space of time.

The Newfies-Dialer aplication has been built using a messaging system so that
it can support distributed processing on cloud servers. The platform is
focused on real-time operations and task call distributions to clustered 
brokers and workers meaning that many millions of calls can be processed daily.

Newfies-Dialer can be installed on a standalone server for smaller deployments. 
It currently utilises the Freeswitch Telephony engine 
(http://www.freeswitch.org) to process the the outbound calls. However support
for other telephony engines, such as Asterisk may be added in the future.

Newfies-Dialer is written in Python using the Django Framework, and operates with
message brokers such as RabbitMQ and Redis using the emerging open standard
for messaging middleware, AMPQ (Advance Messaging Queuing Processing). 
Beanstalk, MongoDB, CouchDB and DBMS can also be supported.

In order to communicate with external systems, Newfies-Dialer has been 
released with a substantial set of API's to easily integrate the platform 
with third-party applications.

Newfies-Dialer is supplied with a comprehensive administrative and user 
interface which allows you and your customers to create outbound call 
campaigns, add phonebooks, subscribers, as well as record audio messages
and design more complex IVR (Interactive Voice Response) applications.
When ready and tested, the campaign can be launched from the interface.

History
-------
Newfies-Dialer was commissioned by a charity named Kubatana 
(http://www.kubatana.net) based in Zimbabwe, which sponsors the Freedomfone 
project (http://www.freedomfone.org/) dedicated to providing information via 
phone technology.

In less economically developed countries, Internet is often limited and 
illiteracy rates may be high, but there is usually comprehensive mobile 
phone coverage. Freedomfone will use Newfies-Dialer to dial up people’s 
phones and offer health information on Cholera, Malaria and so many 
other avoidable health issues in the third world, which may be 
alleviated simply by education. 

Newfies-Dialer was so named after the Newfoundland Dog nicknamed Newfies and
used by sea rescue services around the world.

The Newfies-Dialer project is supported by Star2billing S.L. 
For more information, see http://www.star2billing.com


Who is it for ?
---------------

NGOs :

    - The platform can be used to offer complex data collection, voting 
      applications, notification for availability of supplies and 
      dissemination of health information.

Marketing :

    - Newfies-Dialer is a telephony based marketing tool to deliver 
      advertising to company contacts.

Emergency :

    - Provide a message delivery platform to quickly and efficiently send 
      messages to communities.

Finance :    

    - Debt Recovery and Reminders, this can be easily integrated with call 
      centre software and processes. 

Health & Welfare :
    
    - Deliver appointment reminders to patients of dentists, doctors and 
      other organisations.


Terminology
-----------

**User :** The Person configuring the campaigns and wishing to deliver 
messages.

**Subscriber :** Person who will receive the message.

**Administrator :** Person administering the platform, usually with root 
permissions.

**Gateway :** Peer which will outbound a call and deliver the message to 
the subscriber.

**Phonebook :** Group of subscribers, this is used to define the subset of 
subscribers that will receive the message.

**CDR :** Call Detail Record, keep track of the calls performed by the 
system, eventually can be used for monitoring and billing purposes.

**Call Request :** Describes the request to the system to run a call to a 
subscriber.

**Audio Application :** This can be a simple audio delivery, a routing to 
another gateway, forwarded to a Call-Centre, in fact, any to any 
application that can be built on Freeswitch.


Installation
------------

Newfies is a django based application, so the major requirements are :

    - python >= 2.4
    - Apache / http server with WSGI modules
    - Django Framework >= 1.3
    - Celery >= 2.2
    
The rest of the requirements can easily be installed with PIP 
(http://pypi.python.org/pypi/pip) :

    - https://github.com/Star2Billing/newfies-dialer/blob/master/install/conf/requirements.txt


Newfies-Dialer takes advantage of messaging systems such as RabbitMQ or Redis. Other 
alternatives provided by Celery (http://celeryproject.org) are also supported.

    - Install RabbitMQ or Redis : https://github.com/Star2Billing/newfies-dialer/blob/master/docs/source/broker/broker-installation.rst


Installation Script
~~~~~~~~~~~~~~~~~~~

Installation scripts are provided to install Newfies-Dialer 

    - https://github.com/Star2Billing/newfies-dialer/tree/master/install
   

Documentation
-------------

Complete documentation :

    - http://newfies-dialer.readthedocs.org/

Beginner's Guide :

    - http://www.newfies-dialer.org/documentation/beginners-guide/


Applications
------------

* User Interface :
    http://localhost:9080/
    This application provides a User interface for restricted management of 
    the User's Campaign, Phonebook, Subscriber. It also provides detailed 
    Reporting of calls and message delivery.

* Admin Interface :
    http://localhost:9080/admin/
    This interface provides user (ACL) management, a full control of all 
    Campaigns, Phonebooks, Subscribers, Gateway, configuration of the 
    Audio Application.


Screenshot
----------


.. image:: https://github.com/Star2Billing/newfies-dialer/raw/master/docs/source/_static/images/admin_screenshot.png



Coding Conventions
------------------

This project is PEP8 compilant and please refer to these sources for the Coding 
Conventions :

    - http://docs.djangoproject.com/en/dev/internals/contributing/#coding-style

    - http://www.python.org/dev/peps/pep-0008/
    

Additional information
-----------------------

Fork the project on GitHub : https://github.com/Star2Billing/newfies

License : AGPL (https://raw.github.com/Star2Billing/newfies-dialer/master/COPYING)

Website : http://www.newfies-dialer.org


Support 
-------

Star2Billing S.L. (http://www.star2billing.com) offers consultancy including 
installation, training and customization 

Please email us at sales@star2billing.com for more information

