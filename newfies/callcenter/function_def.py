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
from callcenter.models import Queue


def queue_list(manager_id):
    """Return all agents of the system"""
    queue_list = []
    list = Queue.objects.values_list('id', 'name')\
        .filter(manager_id=manager_id).order_by('id')

    for l in list:
        queue_list.append((l[0], l[1]))
    return queue_list
