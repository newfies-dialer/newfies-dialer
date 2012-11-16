#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.utils.translation import ugettext_lazy as _
from common.utils import Choice


class CONTACT_STATUS(Choice):
    ACTIVE = 1, _('ACTIVE')
    INACTIVE = 0, _('INACTIVE')


class CHOICE_TYPE(Choice):
    CONTAINS = 1, _('Contains')
    EQUALS = 2, _('Equals')
    BEGINS_WITH = 3, _('Begins with')
    ENDS_WITH = 4, _('Ends with')


class STATUS_CHOICE(Choice):
    INACTIVE = 0, _('Inactive')
    ACTIVE = 1, _('Active')
    ALL = 2, _('All')


class PHONEBOOK_COLUMN_NAME(Choice):
    id = _('ID')
    name = _('Name')
    description = _('Description')
    date = _('Date')
    contacts = _('Contacts')