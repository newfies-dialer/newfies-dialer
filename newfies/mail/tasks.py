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

from celery.decorators import task, periodic_task
from django.conf import settings
from mail.models import MailSpooler, MailTemplate
from user_profile.models import User
from datetime import timedelta
import logging
from mailer.engine import send_all
from mailer.models import Message
from mailer import send_html_mail
from django.core.cache import cache


LOCK_EXPIRE = 60 * 5  # Lock expires in 5 minutes

logger = logging.getLogger('sms.filelog')


# allow a sysadmin to pause the sending of mail temporarily.
PAUSE_SEND = getattr(settings, "MAILER_PAUSE_SEND", False)


@task()
def sendmail_task(current_mail_id):
    """
    Task to send SMS
    """
    logger = sendmail_task.get_logger()
    logger.info("TASK :: sendmail_task")

    current_mailspooler = MailSpooler.objects.get(id=current_mail_id)

    if current_mailspooler.mailspooler_type != 4:  # not in process
        logger.info("ERROR :: Trying to send mail for not spolled MailSpooler")
        return False

    mailtemplate = MailTemplate.objects.get(pk=current_mailspooler.mailtemplate.id)
    c_user = User.objects.get(pk=current_mailspooler.user.id)
    c_user.count_email = c_user.count_email + 1
    c_user.save()

    send_html_mail(
        mailtemplate.subject,
        mailtemplate.message_plaintext,
        mailtemplate.message_html,
        mailtemplate.from_email,
        [c_user.email],
        headers={'From': '%s <%s>' % (mailtemplate.from_name, mailtemplate.from_email)},
    )

    current_mailspooler.mailspooler_type = 2  # Sent
    current_mailspooler.save()

    logger.info(u"Mail Sent - ID:%d" % current_mailspooler.id)


@periodic_task(run_every=timedelta(seconds=10))  # every 10 seconds
def mailspooler_pending(*args, **kwargs):
    """A periodic task that check for spooled mail

    **Usage**:

        mailspooler_pending.delay()
    """
    logger = mailspooler_pending.get_logger()
    logger.info("TASK :: mailspooler_pending_pending")

    lock_id = "%s-lock" % ('mailspooler_pending')

    # cache.add fails if if the key already exists
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    # memcache delete is very slow, but we have to use it to take
    # advantage of using add() for atomic locking
    release_lock = lambda: cache.delete(lock_id)

    #Acquire lock
    if acquire_lock():
        try:
            list_pending_mail = MailSpooler.objects.filter(mailspooler_type=1)[:50]
            logger.info("Check for pending Mail...")
        except MailSpooler.DoesNotExist:
            logger.info("MailSpooler doesn't exist!")
            return False

        for current_mailspooler in list_pending_mail:
            #To avoid duplicate sending
            current_mailspooler.mailspooler_type = 4  # In Process
            current_mailspooler.save()
            logger.info("Calling Task to send MAIL!")
            sendmail_task.delay(current_mailspooler.id)

        #Release lock
        release_lock()
    else:
        logger.error("ERROR :: mailspooler_pending is already being imported by another worker")


@periodic_task(run_every=timedelta(seconds=10))  # every 10 seconds
def sendmail_pending(*args, **kwargs):
    """A periodic task that send pending mail

    **Usage**:

        sendmail_pending.delay()
    """
    logger = sendmail_pending.get_logger()
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
    logger = sendmail_retry_deferred.get_logger()
    logger.info("TASK :: sendmail_retry_deferred")
    count = Message.objects.retry_deferred()  # @@@ new_priority not yet supported
    if count and count > 0:
        logger.info("%s message(s) retried" % count)
