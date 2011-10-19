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

    $ python manage.py test --verbosity=2

**2. Run NewfiesApiTestCase**::

    $ python manage.py test dialer_cdr.NewfiesApiTestCase --verbosity=2

**3. Run NewfiesAdminInterfaceTestCase**::

    $ python manage.py test dialer_cdr.NewfiesAdminInterfaceTestCase --verbosity=2

**4. Run NewfiesCustomerInterfaceTestCase**::

    $ python manage.py test dialer_cdr.NewfiesCustomerInterfaceTestCase --verbosity=2

**5. Run NewfiesTastypieApiTestCase**::

    $ python manage.py test dialer_cdr.NewfiesTastypieApiTestCase --verbosity=2


.. automodule:: dialer_cdr.tests

----------------------
Tastypie API Test Case
----------------------
.. _NewfiesTastypieApiTestCase-model:

.. autoclass:: NewfiesTastypieApiTestCase
    :members:

-------------
API Test Case
-------------
.. _NewfiesApiTestCase-model:

.. autoclass:: NewfiesApiTestCase
    :members:


-------------------------
API-CallRequest Test Case
-------------------------

.. _NewfiesApiCallRequestUpdateTestCase-model:

.. autoclass:: NewfiesApiTestCase
    :members:


-------------------------
Admin Interface Test Case
-------------------------

.. _NewfiesAdminInterfaceTestCase-model:

.. autoclass:: NewfiesAdminInterfaceTestCase
    :members:


----------------------------
Customer Interface Test Case
----------------------------

.. _NewfiesCustomerInterfaceTestCase-model:

.. autoclass:: NewfiesCustomerInterfaceTestCase
    :members:

-----------------------------------
Customer Interface Forgot Test Case
-----------------------------------

.. _NewfiesCustomerInterfaceForgotPassTestCase-model:

.. autoclass:: NewfiesCustomerInterfaceForgotPassTestCase
    :members:
