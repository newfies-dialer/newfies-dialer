#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

"""This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'menu.CustomMenu'"""
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from admin_tools.menu import items, Menu
import newfies_dialer


class CustomMenu(Menu):
    """Custom Menu for admin site."""

    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(_('Newfies-Dialer' + ' V' + newfies_dialer.__version__), reverse('admin:index')),
            items.Bookmarks(),
            items.AppList(
                _('applications').capitalize(),
                exclude=('django.contrib.*', )
            ),
            items.AppList(
                _('administration').capitalize(),
                models=('django.contrib.*', )
            ),
            items.MenuItem(_('API Explorer'), reverse('admin:index') + '../rest-api/'),
            items.MenuItem(_('customer panel').title(), reverse('admin:index') + '../'),
        ]

    def init_with_context(self, context):
        """Use this method if you need to access the request context."""
        return super(CustomMenu, self).init_with_context(context)
