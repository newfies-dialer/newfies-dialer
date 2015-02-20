#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.utils.translation import ugettext_lazy as _
from django_lets_go.utils import Choice


class CONTACT_STATUS(Choice):
    ACTIVE = 1, _('active')
    INACTIVE = 0, _('inactive')


class CHOICE_TYPE(Choice):
    CONTAINS = 1, _('contains')
    EQUALS = 2, _('equals')
    BEGINS_WITH = 3, _('begins with')
    ENDS_WITH = 4, _('ends with')


class STATUS_CHOICE(Choice):
    INACTIVE = 0, _('inactive')
    ACTIVE = 1, _('active')
    ALL = 2, _('all')


PHONEBOOK_COLUMN_NAME = {
    'id': _('ID'),
    'name': _('name'),
    'description': _('description'),
    'date': _('date'),
    'contacts': _('contacts')
}

CONTACT_COLUMN_NAME = {
    'id': _('ID'),
    'phonebook': _('phonebook'),
    'contact': _('contact'),
    'last_name': _('last name'),
    'first_name': _('first name'),
    'email': _('email'),
    'status': _('status'),
    'date': _('date')
}
