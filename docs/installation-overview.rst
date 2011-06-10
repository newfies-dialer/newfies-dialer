.. _installation-overview:

=====================
Installation overview
=====================

.. _install-requirement:

Install requirement
===================

Requirement file gives you a way to create an environment where you can put
all optional dependencies which are needed for your Project/Application.

- python >= 2.4 (programming language)
- Apache / http server with WSGI modules
- Django Framework >= 1.3 (Python based Web framework)
- Celery >= 2.2 (Asynchronous task queue/job queue based on distributed message passing)
- MySQL-python >= 1.2.3 (MySQL for python language)
- Werkzeug >= 0.6.2 (Collection of various utilities for WSGI applications)
- amqplib >= 0.6.1 (Client library for AMQP)
- anyjson >= 0.3 (Loads the fastest JSON module)
- django-celery >= 2.2.4 (Celery integration for Django)
- django-extensions >= 0.6 (Collection of global custom management extensions for Django)
- django-jsonfield >= 0.6 (Reusable django field that can use inside models)
- django-pagination >= 1.0.7 (Utilities for creating robust pagination tools throughout a django application)
- django-picklefield >= 0.1.9 (Implementation of a pickled object field)
- django-threaded-multihost >= 1.4-0 (Provides multi-host utilities to Django projects)
- django-urlauth = 0.1.1 (Allows to build links with authentication effect )
- django-uuidfield >= 0.2 (Provides a UUIDField for your Django models)
- django-reusableapps >= 0.1.1 (Python module to enable Django to load reusable, pluggable and egg-based applications)
- docutils >= 0.7 (Text processing system for processing plaintext documentation into useful formats)
- importlib >= 1.0.2 (Implementation of the `import` statement)
- kombu >= 1.0.2 (An AMQP - Advanced Message Queuing Protocol messaging framework for Python)
- pyparsing >= 1.5.5 (A general parsing module for Python)
- python-dateutil >= 1.5 (Extensions to the standard datetime module)
- redis >= 2.2.2 (Redis Python Client)
- simplejson >= 2.1.3 (Simple, fast, complete, correct and extensible JSON)
- uuid >= 1.30 (UUID object and generation functions )
- wsgiref >= 0.1.2 (Validation support for WSGI )
- switch2bill-common (Common library that are reused by Star2Billing)
- simu-prefix-country (Provide Prefix and Country information)
- django-piston (Django application that create APIs for your sites.)
- BeautifulSoup >= 3.2.0 (HTML parser optimized for screen-scraping)
- Pygments >= 1.4 (A generic syntax highlighter)
- django-admin-tools (Collection of tools for the django administration)
- python-memcached >= 1.47 (Python based API for communicating with the memcached distributed memory object cache daemon)
- django-memcache-status >= 1.0.1 (Displays statistics about memcached instances)


Use PIP to install all the requirements,::

    $ pip install -r requirements.txt


.. _installation-script:

Installation Script
===================

You can install Newfies manually or using the shell script provided.

To install Newfies using the script,::

    $ chmod +x script/install-newfies.sh

    $ ./script/install-newfies.sh


.. _caching-system:

Caching System
==============

User requests a page, the Web server makes all sorts of calculations
for business logic and to create the page that your site’s visitor sees.
It creates processing-overhead perspective, than your standard
read-a-file-off-the-filesystem server arrangement.

That’s where caching comes in.

To cache something is to save the result of an expensive calculation so that
you don’t have to perform the calculation next time.

::
    
    $ mkdir /usr/share/django_cache

