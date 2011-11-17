.. _troubleshooting:

===============
Troubleshooting
===============

.. contents::
    :local:
    :depth: 1


.. _find-help:

Where to find help
==================

Documentation:
~~~~~~~~~~~~~~
http://www.newfies-dialer.org/documentation/


Mailing list:
~~~~~~~~~~~~~
We have set up a mailing list at http://groups.google.com/group/newfies-dialer


Forum:
~~~~~~
We have a forum at http://forum.newfies-dialer.org/


Support:
~~~~~~~~
Star2Billing S.L. offers consultancy including installation, training and customisation



.. _find-log-files:

Where to find the log files
===========================

All the logs are centralized into one single directory **/var/log/newfies/**


**newfies-django-db.log** : This contains all the Database queries performed by the UI
    
    
**newfies-django.log** : All the logger events from Django


**err-apache-newfies.log** : Any apache errors pertaining to Newfies-Dialer


**celery-newfies-node1.log** : This contains celery activity



.. _run-quick-test-call:

How to run a quick test call
============================

Go on the admin panel and check if there is any call request that has been spooled.

    * http://your-ip:8008/admin/dialer_cdr/callrequest/


If there are no calls queued, this means that the campaign is not properly configured.

You should:

    1. Check if the campaign is started that the "Start time", "Finish Time" and server time are correct.
    
    2. Make sure that you configured a Dialer Setting for the user running the campaign, although there will be a warning for this on the Customer UI : http://your-ip:8008/admin/dialer_settings/dialersetting/

If there is an existing Call Request, check the status, and check the Celery log stored in /var/log/newfies



.. _run-debug-mode:

Run in debug mode
=================

Make sure you stop the services first::

    $ /etc/init.d/newfies-celeryd stop


Then run in debug mode::

    $ workon newfies-dialer
    $ cd /usr/share/newfies/
    $ python manage.py celeryd -EB --loglevel=DEBUG



.. _celerymon:

Celerymon
=========

* https://github.com/ask/celerymon

Running the monitor :

Start celery with the --events option on, so celery sends events for celerymon to capture::
    $ workon newfies-dialer
    $ cd /usr/share/newfies/
    $ python manage.py celeryd -E
    
    
Run the monitor server::

    $ workon newfies-dialer
    $ cd /usr/share/newfies/
    $ python manage.py celerymon
    
    
However, in production you probably want to run the monitor in the background, as a daemon::

    $ workon newfies-dialer
    $ cd /usr/share/newfies/
    $ python manage.py celerymon --detach
    
    
For a complete listing of the command line arguments available, with a short description, you can use the help command::

    $ workon newfies-dialer
    $ cd /usr/share/newfies/
    $ python manage.py help celerymon


Now you can visit the webserver celerymon starts by going to: http://localhost:8989




.. _discard-pending-tasks:

How to discard all pending tasks
================================

http://docs.celeryproject.org/en/latest/faq.html?highlight=purge#how-do-i-discard-all-waiting-tasks



.. _checking-plivo-running:

Checking Plivo is running
=========================

At the command line, type::

    $ ps aux | grep plivo


This should tell you that Plivo-rest, Plivo-Outbound and Plivo-cache are all running. If they are not, these services can be restarted with the following commands::

    $ /etc/init.d/plivo stop
    $ /etc/init.d/plivocache stop
    $ /etc/init.d/plivo start
    $ /etc/init.d/plivocache start


If there are still issues with Plivo, then check the logs for clues at **/usr/share/plivo/tmp/**


.. _checking-freeswitch:

Checking Freeswitch
===================

Entering the Freeswitch CLI shold indicate whether it is running by typing fs_cli at the console. Once logged in, you can check the trunk registration by typing sofia status at the Freeswitch CLI. CTRL-D exits the Freeswitch CLI.

If the Freeswitch CLI cannot be launched, then the status of freeswitch can be checked with::

    $ ps aux | grep freeswitch
    or 
    $ /etc/init.d/freeswitch status


If Freeswitch is not running, then it can be started with ::

    $ /etc/init.d/freeswitch start



.. _step-by-step-checklist:

Step By Step Checklist
======================

The step by step checklist below should be used to validate that all components of the platform are running.

User interface :

    * 1. Dialer Gateway matching a configured trunk is set up in the UI
    
    * 2. Dialer Settings configured and attached to the appropriate user
    
    * 3. Phonebook Created with contacts attached to the phonebook
    
    * 4. Configured voice application
    
    * 5. Campaign created, and started, with a phone book attached, and the campaign schedule current


Backend :

    * 1. Celery Monitor Running
    
    * 2. Plivo Running
    
    * 3. Freeswitch running


If there are still problems, then raise a support question on the mailing-list http://groups.google.com/group/newfies-dialer or our forum, http://forum.newfies-dialer.org/, alternatively, contact newfies-dialer@star2billing.com for commercial support.






