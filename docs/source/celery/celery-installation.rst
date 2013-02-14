.. _celery-installation:

Celery Installation
===================

------
Celery
------

Celery is an asynchronous task queue/job queue based on distributed message
passing. It is focused on real-time operation, but supports scheduling as well.

Celery communicates via messages using a broker to mediate between clients
and workers. To initiate a task a client puts a message on the queue, the
broker then delivers the message to a worker.

You can visit Celery Project webpage to find further information :
http://celeryproject.org/

You can install Celery either via the Python Package Index (PyPI) or from source.

To install using pip
--------------------
::

    $ pip install Celery


.. _celery-installing-from-source:

Downloading and installing from source
--------------------------------------

To Download the latest version `click here`_.

.. _click here: http://pypi.python.org/pypi/celery/


You can install it by doing the following::

    $ tar xvfz celery-*****.tar.gz

    $ cd celery-*****

    $ python setup.py build

    $ python setup.py install

