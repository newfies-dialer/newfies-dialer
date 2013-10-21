#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from celery.task import PeriodicTask
from celery.task import Task
from celery.utils.log import get_task_logger
from dialer_contact.tasks import collect_subscriber
from common.only_one_task import only_one
from datetime import datetime, timedelta
from math import floor
from common_functions import debug_query
# from celery.task.http import HttpDispatchTask
# from common_functions import isint


LOCK_EXPIRE = 60 * 10 * 1  # Lock expires in 10 minutes

logger = get_task_logger(__name__)


class event_process(PeriodicTask):
    """A periodic task that checks the the event
    for each event it will check if it's necessary to ...

    **Usage**:

        event_process.delay()
    """
    # The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    run_every = timedelta(seconds=60)

    def run(self, **kwargs):
        logger.info("TASK :: event_process")


class repeat_event(Task):
    @only_one(ikey="repeat_event", timeout=LOCK_EXPIRE)
    def run(self, event_id):
        """
        This will check the repeat rules of an event

        **Attributes**:

            * ``event_id`` - Event ID
        """
        logger = self.get_logger()
        logger.info("TASK :: repeat_event = %d" % event_id)
