.. _customer-panel:

==============
Customer Panel
==============

User Interface :

http://localhost:8000/
This application provides a user interface for restricted management of
the User's Campaigns, Phonebooks and Subscribers. It also provides detailed
reporting of calls and message delivery.

.. contents::
    :local:
    :depth: 1

.. _customer-screenshot-features:

Screenshot with Features
========================

Index
~~~~~

Index page for the customer interface after successful login with user credentials 

.. image:: ../_static/images/customer_screenshot.png


.. _customer-phonebook-access:

Phonebook
~~~~~~~~~

The phonebook list will be displayed from the following URL. You can add a new
phonebook by clicking ``Add phonebook`` and add the name of a phonebook and its
description. Also from the phonebook list, click on the phonebook to update.

**URL**:

    * http://localhost:8000/dialer_campaign/phonebook/

.. image:: ../_static/images/customer/phonebook_list.png

To Add/Update a Phonebook for a logged in user

**URL**:

    * http://localhost:8000/dialer_campaign/phonebook/add/
    * http://localhost:8000/dialer_campaign/phonebook/1/

.. image:: ../_static/images/customer/update_phonebook.png

.. _customer-contact-access:

Contact
~~~~~~~

The contact list will be displayed from following the URL. You can add a new contact
by clicking ``Add contact`` & adding the contact details (i.e. phone number, name,
description about contact, contact status) under the logged in user's phonebook from
the phonebook list. On the contact list, click on the contact to update.


**URL**:

    * http://localhost:8000/dialer_campaign/contact/

.. image:: ../_static/images/customer/contact_list.png

To Add/Update a contact in a phonebook

**URL**:

    * http://localhost:8000/dialer_campaign/contact/add/
    * http://localhost:8000/dialer_campaign/contact/1/

.. image:: ../_static/images/customer/update_contact.png
    :width: 1000

To import bulk contacts into a phonebook, click on ``Import``.
where you can upload contacts via a CSV file under a logged in 
user's phonebook.

**URL**:

    * http://localhost:8000/dialer_campaign/contact/import/

.. image:: ../_static/images/customer/import_contact.png
    :width: 1000


.. _customer-campaign-access:

Campaign
~~~~~~~~

The campaign list will be displayed from the following URL. You can add a new campaign for
the logged in user by clicking ``Add campaign``. When adding a campaign, it is important
to add the campaign's start and end dates with time & week-day exceptions. Select 
the gateway through which calls will be routed & phonebook(s) that are
linked with contacts from the campaign list, click on campaign to update.

**URL**:

    * http://localhost:8000/dialer_campaign/campaign/

.. image:: ../_static/images/customer/campaign_list.png

To Add/Update a Campaign for a logged in user

**URL**:

    * http://localhost:8000/dialer_campaign/campaign/add/
    * http://localhost:8000/dialer_campaign/campaign/1/

.. image:: ../_static/images/customer/update_campaign.png
    :width: 1000


.. _customer-dashboard-access:

Dashboard
~~~~~~~~~

Dashboard gives the information anbout campaign & its related call records

.. image:: ../_static/images/customer/customer_dashboard.png