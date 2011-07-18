.. _install-configure-plivo:

Plivo Installation and configuration
====================================

When `Freeswitch`_ is installed, the next task is to install `Plivo`_. Plivo is an open source communications framework to rapidly deploy voice based applications used in conjunction with Newfies-Dialer.

Run the following commands::

    wget https://raw.github.com/plivo/plivo/master/scripts/plivo_install_beta.sh

then::

    bash plivo_install_beta.sh /usr/share/plivo

This will download and install Plivo and all its dependencies.
We need to have Plivo start on boot, so run the following command to make it automatically start.

ln -s /usr/share/plivo/bin/plivo /etc/rc2.d/S99plivo

Please note that the Plivo script makes alterations to the Freeswitch dial-plan, so it should not be blindly run on an existing working Freeswitch installation, as it will change your current configuration. If you wish to install Plivo on an existing version of Freeswitch, use the script as a guide, or edit it to suit your requirements.

.. _`Freeswitch`: http://www.freeswitch.org/
.. _`Plivo`: http://www.plivo.org/
