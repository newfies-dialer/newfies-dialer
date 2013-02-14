.. _testing:

Test Case Descriptions
======================

-----------
Requirement
-----------

**Run/Start Celery**::

    $ /etc/init.d/celery start

or::

    $ python manage.py celeryd -l info

**Run/Start Redis**::

    $ /etc/init.d/redis-server start

---------------
How to run test
---------------

**1. Run Full Test Suit**::

    $ python manage.py test

**2. Run Individual Test**::

    $ python manage.py test api

    $ python manage.py test dialer_campaign

    $ python manage.py test dialer_cdr

    $ python manage.py test dialer_audio

    $ python manage.py test dialer_gateway

    $ python manage.py test dialer_settings

    $ python manage.py test frontend

    $ python manage.py test survey

    $ python manage.py test user_profile

    $ python manage.py test voice_app



.. toctree::
    :maxdepth: 2

    ./testcases/api-testcases
    ./testcases/admin-testcases
    ./testcases/customer-testcases
    ./testcases/model-testcases


.. automodule:: frontend.tests

-----------------------------------
Customer Interface Forgot Test Case
-----------------------------------

.. _FrontendForgotPassword:

.. autoclass:: FrontendForgotPassword
    :members:
