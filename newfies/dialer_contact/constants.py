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

from django.utils.translation import ugettext_lazy as _
from common.utils import Choice


class CONTACT_STATUS(Choice):
    ACTIVE = 1, _('active').upper()
    INACTIVE = 0, _('inactive').upper()


class CHOICE_TYPE(Choice):
    CONTAINS = 1, _('contains').capitalize()
    EQUALS = 2, _('equals').capitalize()
    BEGINS_WITH = 3, _('begins with').capitalize()
    ENDS_WITH = 4, _('ends with').capitalize()


class STATUS_CHOICE(Choice):
    INACTIVE = 0, _('inactive').upper()
    ACTIVE = 1, _('active').upper()
    ALL = 2, _('all').upper()


class PHONEBOOK_COLUMN_NAME(Choice):
    id = _('ID')
    name = _('name')
    description = _('description')
    date = _('date')
    contacts = _('contacts')


class CONTACT_COLUMN_NAME(Choice):
    id = _('ID')
    phonebook = _('phonebook')
    contact = _('contact')
    last_name = _('last name')
    first_name = _('first name')
    email = _('email')
    status = _('status')
    date = _('date')
