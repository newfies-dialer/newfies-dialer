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

from django.conf import settings
from celery.decorators import task, periodic_task
from celery.task import PeriodicTask
from celery.utils.log import get_task_logger
from common.only_one_task import only_one
from mod_mailer.models import MailSpooler, MailTemplate
from mod_mailer.constants import MAILSPOOLER_TYPE
from mailer.engine import send_all
from mailer.models import Message
from mailer import send_html_mail
from datetime import timedelta


LOCK_EXPIRE = 60 * 5  # Lock expires in 5 minutes

logger = get_task_logger(__name__)


# allow a sysadmin to pause the sending of mail temporarily.
PAUSE_SEND = getattr(settings, "MAILER_PAUSE_SEND", False)


@task()
def sendmail_task(current_mail_id):
    """
    Task to send Mail
    """
    logger.info("TASK :: sendmail_task")

    current_mailspooler = MailSpooler.objects.get(id=current_mail_id)

    if current_mailspooler.mailspooler_type != MAILSPOOLER_TYPE.IN_PROCESS:
        logger.info("ERROR :: Trying to send mail which is not set as IN_PROCESS")
        return False

    mailtemplate = MailTemplate.objects.get(pk=current_mailspooler.mailtemplate.id)
    #contact_email = current_mailspooler.contact.email

    send_html_mail(
        mailtemplate.subject,
        mailtemplate.message_plaintext,
        mailtemplate.message_html,
        mailtemplate.from_email,
        [current_mailspooler.contact_email],
    )

    current_mailspooler.mailspooler_type = MAILSPOOLER_TYPE.SENT
    current_mailspooler.save()

    logger.info("Mail Sent - ID:%d" % current_mailspooler.id)


class mailspooler_pending(PeriodicTask):
    """A periodic task that spool mail that needs to be sent

    **Usage**:

        mailspooler_pending.delay()
    """
    run_every = timedelta(seconds=10)

    @only_one(ikey="mailspooler_pending", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger.info("TASK :: mailspooler_pending")

        try:
            list_pending_mail = MailSpooler.objects.filter(mailspooler_type=MAILSPOOLER_TYPE.PENDING)[:50]
            logger.info("Check for pending Mail...")
        except MailSpooler.DoesNotExist:
            logger.info("MailSpooler doesn't exist!")
            return False

        for current_mailspooler in list_pending_mail:
            #To avoid duplicate sending
            current_mailspooler.mailspooler_type = MAILSPOOLER_TYPE.IN_PROCESS  # In Process
            current_mailspooler.save()
            logger.info("Calling Task to send MAIL!")
            sendmail_task.delay(current_mailspooler.id)


@periodic_task(run_every=timedelta(seconds=60))  # every 10 seconds
def sendmail_pending(*args, **kwargs):
    """A periodic task that send pending mail

    **Usage**:

        sendmail_pending.delay()
    """
    logger.info("TASK :: sendmail_pending")
    if not PAUSE_SEND:
        send_all()
    else:
        logger.info("Sending mail is paused.")


@periodic_task(run_every=timedelta(days=1))  # every 1 day
def sendmail_retry_deferred(*args, **kwargs):
    """A periodic task that send deferred mail

    **Usage**:

        sendmail_retry_deferred.delay()
    """
    logger.info("TASK :: sendmail_retry_deferred")
    count = Message.objects.retry_deferred()  # @@@ new_priority not yet supported
    if count and count > 0:
        logger.info("%s message(s) retried" % count)
