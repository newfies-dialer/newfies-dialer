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


# from celery.task import PeriodicTask
# from celery.decorators import task
# from common.only_one_task import only_one
# from datetime import datetime, timedelta
# from math import ceil
# from time import sleep

# LOCK_EXPIRE = 60 * 60 * 1  # Lock expires in 1 hours


# @task()
# def mylittletask_adder(id):
#     """This will execute the outbound calls in the campaign

#     **Attributes**:

#         * ``campaign_id`` - Campaign ID
#     """
#     logger = mylittletask_adder.get_logger()
#     logger.info("\nTASK :: mylittletask_adder %s" % str(id))
#     sleep(10)
#     logger.info("END TASK :: mylittletask_adder %s" % str(id))


# class task_runner(PeriodicTask):
#     """A periodic task that launch other tasks

#     **Usage**:

#         task_runner.delay()
#     """
#     run_every = timedelta(seconds=30)

#     @only_one(key="task_runner", timeout=LOCK_EXPIRE)
#     def run(self, **kwargs):
#         logger = self.get_logger(**kwargs)
#         logger.warning("TASK :: task_runner")

#         for time_to_wait in range(0, 30):
#             second_towait = ceil(time_to_wait)
#             launch_date = datetime.now() + timedelta(seconds=second_towait)

#             logger.info("Will launch mylittletask_adder  at %s" % \
#                             (launch_date.strftime("%b %d %Y %I:%M:%S")))
#             mylittletask_adder.apply_async(
#                         args=[second_towait],
#                         eta=launch_date)
