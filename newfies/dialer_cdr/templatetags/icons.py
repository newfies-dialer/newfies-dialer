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

from django import template
from django.conf import settings

register = template.Library()


def icon(icon_name):
    """
    template tag to display icon

    >>> icon('test')
    'class="icon" style="text-decoration:none;background-image:url(/static/newfies/icons/test.png);"'
    """
    return 'class="icon" style="text-decoration:none;background-image:url(%snewfies/icons/%s.png);"' \
           % (settings.STATIC_URL, icon_name)
register.simple_tag(icon)


def listicon(icon_name):
    """
    template tag to display list style icon

    >>> listicon('test')
    'style="text-decoration:none;list-style-image:url(/static/newfies/icons/test.png);"'
    """
    return 'style="text-decoration:none;list-style-image:url(%snewfies/icons/%s.png);"' \
           % (settings.STATIC_URL, icon_name)
register.simple_tag(listicon)


def icon_style(icon_name):
    """
    template tag to display style icon

    >>> icon_style('test')
    'style="text-decoration:none;background-image:url(/static/newfies/icons/test.png);"'
    """
    return 'style="text-decoration:none;background-image:url(%snewfies/icons/%s.png);"' \
           % (settings.STATIC_URL, icon_name)
register.simple_tag(icon_style)
