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

    |-- addons             - This area is used to hold sample data files
    |-- locale             - This area is used to hold language files
    |-- resources          - This area is used to hold media files
    |-- custom_admin_tools - The code for admin dashboard/menu
    |-- dialer_campaign    - The code for dialer campaign
    |   `-- api
    |-- dialer_cdr         - This defines the call request & its information
    |   |-- api
    |   `-- fixtures
    |-- dialer_gateway     - This defines the trunk to deliver the VoIP Calls
    |   `-- fixtures
    |-- dialer_settings    - This defines sets of settings to apply on user
    |-- voip_server        - This defines the Voip Server & its group used by the Dialer
    |-- voip_app           - This defines application that are defined on the platform
    |-- static
    |   |-- newfies
    |   |    |-- css
    |   |    |-- js
    |   |    `-- images
    |-- user_profile       - The code for user profile to extend auth model of Django
    `-- templates          - This area is used to override templates
        |-- admin
        |   |-- dialer_campaign
        |   `-- dialer_cdr
        |-- admin_tools
        |-- registration
        |-- memcache_status
        `-- dialer_campaign
