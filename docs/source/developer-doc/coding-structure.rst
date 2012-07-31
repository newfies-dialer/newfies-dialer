.. _coding-structure:


Coding Style & Structure
========================

-----
Style
-----

Coding follows the `PEP 8 Style Guide for Python Code <http://www.python.org/dev/peps/pep-0008/>`_.

---------
Structure
---------

The newfies directory::
    
    |-- custom_admin_tools - The code for admin dashboard/menu
    |-- api                - The code for APIs
    |-- dialer_contact     - The code for phonebook, contact
    |   `-- fixtures
    |-- dialer_campaign    - The code for dialer campaign
    |   `-- fixtures
    |-- dialer_cdr         - This defines the call request & its information
    |   `-- fixtures
    |-- dialer_gateway     - This defines the trunk to deliver the VoIP Calls
    |   `-- fixtures
    |-- dialer_settings    - This defines sets of settings to apply on user
    |-- voice_app          - This defines application that are defined on the platform
    |   `-- fixtures
    |-- survey             - The code for survey module
    |   `-- fixtures
    |-- frontend           - The code for dashboard, forgot password
    |-- static
    |   |-- newfies
    |   |    |-- css
    |   |    |-- js
    |   |    |-- icons
    |   |    `-- images
    |-- user_profile       - The code for user profile to extend auth model of Django
    |-- resources          - This area is used to hold media files
    |-- usermedia          - This folder is used to upload audio files
    `-- templates          - This area is used to override templates
        |-- admin
        |   |-- dialer_contact
        |   `-- dialer_cdr
        |-- admin_tools
        |-- registration
        |-- memcache_status
        `-- frontend
