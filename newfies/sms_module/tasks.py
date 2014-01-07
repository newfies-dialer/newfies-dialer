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

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from celery.task import PeriodicTask
from celery.task import Task
from celery.decorators import task
from common.only_one_task import only_one
from celery.utils.log import get_task_logger
from sms.tasks import SendMessage
from models import SMSCampaign, SMSCampaignSubscriber, SMSMessage
from constants import SMS_SUBSCRIBER_STATUS, SMS_CAMPAIGN_STATUS
from dialer_campaign.function_def import user_dialer_setting
from datetime import datetime, timedelta
from django.utils.timezone import utc
from math import ceil

logger = get_task_logger(__name__)
LOCK_EXPIRE = 60 * 10 * 1  # Lock expires in 10 minutes
DIV_MIN = 10  # This will divide the minutes by that value and allow to not wait too long for the calls


def get_sms_maxretry(sms_campaign):
    """ If SMS Campaign's maxretry is 0 then
        we should use SMS Dialer Setting sms_maxretry
    """
    if sms_campaign.maxretry is None or not sms_campaign.maxretry >= 0:
        sms_dialer_set = user_dialer_setting(sms_campaign.user)
        maxretry = int(sms_dialer_set.sms_maxretry)
    else:
        maxretry = int(sms_campaign.maxretry)
    return maxretry


@task()
def init_smsrequest(obj_subscriber, obj_sms_campaign):
    """This task outbounds the call

    **Attributes**:

        * ``obj_subscriber`` - SMSCampaignSubscriber object
        * ``user`` - User object
    """
    logger.warning("init_smsrequest contact:%s" % obj_subscriber.contact.contact)

    maxretry = get_sms_maxretry(obj_sms_campaign)

    # Update SMSCampaignSubscriber
    if obj_subscriber.count_attempt <= maxretry:
        if obj_subscriber.count_attempt is None or not obj_subscriber.count_attempt >= 0:
            obj_subscriber.count_attempt = 1
        else:
            obj_subscriber.count_attempt += 1

        text_message = obj_subscriber.contact.replace_tag(obj_subscriber.sms_campaign.text_message)

        # Create Message object
        msg_obj = SMSMessage.objects.create(
            content=text_message,
            recipient_number=obj_subscriber.contact.contact,
            sender=obj_subscriber.sms_campaign.user,
            sender_number=obj_subscriber.sms_campaign.callerid,
            status='Unsent',
            content_type=ContentType.objects.get(model='smscampaignsubscriber'),
            object_id=obj_subscriber.id,
            sms_campaign=obj_sms_campaign,
        )

        obj_subscriber.message = msg_obj
        obj_subscriber.last_attempt = datetime.utcnow().replace(tzinfo=utc)
        obj_subscriber.save()

        # Send sms
        logger.warning("Call SendMessage id:%d" % msg_obj.id)
        SendMessage.delay(msg_obj.id, obj_subscriber.sms_campaign.sms_gateway_id)
    else:
        logger.error("Max retry exceeded, sub_id:%s" % obj_subscriber.id)

    return True


#TODO: Put a priority on this task
@task()
def check_sms_campaign_pendingcall(sms_campaign_id):
    """This will execute the outbound calls in the sms_campaign

    **Attributes**:

        * ``sms_campaign_id`` - SMSCampaign ID

    **Usage**:

        check_sms_campaign_pendingcall.delay(sms_campaign_id)
    """
    logger.info("TASK :: check_sms_campaign_pendingcall = %s" % str(sms_campaign_id))
    try:
        obj_sms_campaign = SMSCampaign.objects.get(id=sms_campaign_id)
    except:
        logger.error('Cannot find this SMS Campaign')
        return False

    #TODO: Control the Speed
    #if there is many task pending we should slow down
    frequency = obj_sms_campaign.frequency  # default 10 calls per minutes

    #Speed
    #check if the other tasks send for this sms_campaign finished to be ran

    #Get the subscriber of this sms_campaign
    # get_pending_subscriber get Max 1000 records
    list_subscriber = obj_sms_campaign.get_pending_subscriber_update(
        frequency, SMS_SUBSCRIBER_STATUS.IN_PROCESS)
    if list_subscriber:
        logger.debug("Number of subscriber found : %d" % len(list_subscriber))

    try:
        no_subscriber = list_subscriber.count()
    except AttributeError:
        no_subscriber = 0

    if no_subscriber == 0:
        logger.info("No Subscriber to proceed on this sms_campaign")
        return False

    #find how to dispatch them in the current minutes
    time_to_wait = int(60 / DIV_MIN) / no_subscriber
    count = 0

    for elem_camp_subscriber in list_subscriber:
        """Loop on Subscriber and start the initcall task"""
        count = count + 1
        logger.info(
            "Add Message for Subscriber (%s) & wait (%s) " % (str(elem_camp_subscriber.id), str(time_to_wait)))

        #Check if the contact is authorized
        if not obj_sms_campaign.is_authorized_contact(elem_camp_subscriber.contact.contact):
            logger.error("Error : Contact not authorized")
            elem_camp_subscriber.status = SMS_SUBSCRIBER_STATUS.NOT_AUTHORIZED  # Update to Not Authorized
            elem_camp_subscriber.save()
            return True

        #Todo Check if it's a good practice / implement a PID algorithm
        second_towait = ceil(count * time_to_wait)
        launch_date = datetime.utcnow().replace(tzinfo=utc) + timedelta(seconds=second_towait)

        logger.warning("Init SMS in %s at %s" % (str(second_towait), launch_date.strftime("%b %d %Y %I:%M:%S")))

        # Send sms through init_smsrequest
        init_smsrequest.apply_async(
            args=[elem_camp_subscriber, obj_sms_campaign],
            countdown=second_towait)


class spool_sms_nocampaign(PeriodicTask):
    """A periodic task that checks the sms not assigned to a campaign, create and tasks the calls

    **Usage**:

        spool_sms_nocampaign.delay()
    """
    run_every = timedelta(seconds=int(60 / DIV_MIN))
    #NOTE : until we implement a PID Controller :
    #http://en.wikipedia.org/wiki/PID_controller

    #The sms_campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    #run_every = timedelta(seconds=60)

    @only_one(ikey="spool_sms_nocampaign", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.warning("TASK :: Check spool_sms_nocampaign")

        #start_from = datetime.utcnow().replace(tzinfo=utc)
        #list_sms = SMSMessage.objects.filter(delivery_date__lte=start_from, status='Unsent', sms_campaign__isnull=True)
        list_sms = SMSMessage.objects.filter(status='Unsent', sms_campaign__isnull=True)
        logger.warning("TASK :: Check spool_sms_nocampaign -> COUNT SMS (%d)" % list_sms.count())

        for sms in list_sms:
            logger.debug("=> SMS Message (id:%d - phonenumber:%s)" % (sms.id, sms.sender_number))
            # Send SMS
            SendMessage.delay(sms.id, sms.sms_gateway_id)


class sms_campaign_running(PeriodicTask):
    """A periodic task that checks the sms_campaign, create and tasks the calls

    **Usage**:

        sms_campaign_running.delay()
    """
    run_every = timedelta(seconds=int(60 / DIV_MIN))
    #NOTE : until we implement a PID Controller :
    #http://en.wikipedia.org/wiki/PID_controller

    #The sms_campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    #run_every = timedelta(seconds=60)

    @only_one(ikey="sms_campaign_running", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.warning("TASK :: Check if there is sms_campaign_running")

        for sms_campaign in SMSCampaign.objects.get_running_sms_campaign():
            logger.debug("=> SMS Campaign name %s (id:%s)" % (sms_campaign.name,
                                                              sms_campaign.id))
            check_sms_campaign_pendingcall.delay(sms_campaign.id)


#!!! USED
class SMSImportPhonebook(Task):
    """
    ImportPhonebook class call the import for a specific campaign_id and phonebook_id

    **Usage**:

        SMSImportPhonebook.delay(campaign_id, phonebook_id)
    """
    @only_one(ikey="import_phonebook", timeout=LOCK_EXPIRE)
    def run(self, campaign_id, phonebook_id):
        """
        Read all the contact from phonebook_id and insert into subscriber
        """
        logger = self.get_logger()
        logger.info("TASK :: import_phonebook")
        obj_campaign = SMSCampaign.objects.get(id=campaign_id)

        #Faster method, ask the Database to do the job
        importcontact_custom_sql(campaign_id, phonebook_id)

        #Count contact imported
        count_contact = SMSCampaignSubscriber.objects.filter(sms_campaign=campaign_id).count()

        #Add the phonebook id to the imported list
        if obj_campaign.imported_phonebook == '':
            sep = ''
        else:
            sep = ','
        obj_campaign.imported_phonebook = obj_campaign.imported_phonebook + \
            '%s%d' % (sep, phonebook_id)
        obj_campaign.totalcontact = count_contact
        obj_campaign.save()
        return True


#!!! USED
# OPTIMIZATION - FINE
class sms_campaign_spool_contact(PeriodicTask):
    """A periodic task that checks the the running campaign
    for each running campaign it will check if it's necessary to import
    the contact from the phonebook to the subscriber list

    **Usage**:

        sms_campaign_spool_contact.delay()
    """
    # The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    run_every = timedelta(seconds=60)

    def run(self, **kwargs):
        logger.info("TASK :: sms_campaign_spool_contact")

        for campaign in SMSCampaign.objects.get_running_sms_campaign():
            logger.debug("=> Spool Contact : SMSCampaign name %s (id:%s)" %
                        (campaign.name, str(campaign.id)))
            # Start collecting the contacts for this campaign
            sms_collect_subscriber.delay(campaign.id)


#!!! USED
@task()
def sms_collect_subscriber(campaign_id):
    """
    This task will collect all the contact and create the Subscriber
    if the phonebook_id is no in the list of imported_phonebook IDs.

    **Attributes**:

        * ``campaign_id`` - Campaign ID

    **Usage**:

        sms_collect_subscriber.delay(campaign_id)
    """
    logger.debug("Collect subscribers for the campaign = %s" % str(campaign_id))

    #Retrieve the list of active contact
    obj_campaign = SMSCampaign.objects.get(id=campaign_id)
    list_phonebook = obj_campaign.phonebook.all()

    for item_phonebook in list_phonebook:
        phonebook_id = item_phonebook.id

        # check if phonebook_id is missing in imported_phonebook list
        if not str(phonebook_id) in obj_campaign.imported_phonebook.split(','):
            #Run import
            logger.info("SMS ImportPhonebook %d for campaign = %d" % (phonebook_id, campaign_id))
            keytask = 'sms_import_phonebook-%d-%d' % (campaign_id, phonebook_id)
            SMSImportPhonebook().delay(obj_campaign.id, phonebook_id, keytask=keytask)

    return True


def importcontact_custom_sql(sms_campaign_id, phonebook_id):
    from django.db import connection, transaction
    cursor = connection.cursor()

    # Call PL-SQL stored procedure
    #CampaignSubscriber.importcontact_pl_sql(sms_campaign_id, phonebook_id)

    # Data insert operation - commit required
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        # Data insert operation - commit required
        sqlimport = "INSERT IGNORE INTO sms_campaign_subscriber (contact_id, "\
            "sms_campaign_id, duplicate_contact, status, created_date, updated_date) "\
            "SELECT id, %d, contact, 1, NOW(), NOW() FROM dialer_contact "\
            "WHERE phonebook_id=%d AND dialer_contact.status=1" % \
            (sms_campaign_id, phonebook_id)

    elif settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        # Data insert operation - http://stackoverflow.com/questions/12451053/django-bulk-create-with-ignore-rows-that-cause-integrityerror
        sqlimport = "LOCK TABLE sms_campaign_subscriber IN EXCLUSIVE MODE;" \
            "INSERT INTO sms_campaign_subscriber (contact_id, "\
            "sms_campaign_id, duplicate_contact, status, created_date, updated_date) "\
            "SELECT id, %d, contact, 1, NOW(), NOW() FROM dialer_contact "\
            "WHERE phonebook_id=%d AND dialer_contact.status=1 AND NOT EXISTS (" \
            "SELECT 1 FROM sms_campaign_subscriber WHERE "\
            "sms_campaign_subscriber.sms_campaign_id=%d "\
            "AND dialer_contact.id = sms_campaign_subscriber.contact_id );" % \
            (sms_campaign_id, phonebook_id, sms_campaign_id)
    else:
        # Other DB
        logger.error("Database not supported (%s)" %
                     settings.DATABASES['default']['ENGINE'])
        return False

    cursor.execute(sqlimport)
    transaction.commit_unless_managed()

    return True


#Expire check
class sms_campaign_expire_check(PeriodicTask):
    """A periodic task that checks the SMS campaign expiration

    **Usage**:

        sms_campaign_expire_check.delay()
    """
    #The sms_campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    run_every = timedelta(seconds=60)

    @only_one(ikey="sms_campaign_expire_check", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info("TASK :: sms_campaign_expire_check")
        from sms_module.views import common_sms_campaign_status
        for sms_campaign in SMSCampaign.objects.get_expired_sms_campaign():
            logger.debug("=> SMS Campaign name %s (id:%s)" % (sms_campaign.name,
                                                              sms_campaign.id))
            common_sms_campaign_status(sms_campaign.id, SMS_CAMPAIGN_STATUS.END)


class resend_sms_update_smscampaignsubscriber(PeriodicTask):
    """A periodic task that resend the failed sms,

    **Usage**:

        resend_sms_update_smscampaignsubscriber.delay()
    """
    run_every = timedelta(seconds=60)

    @only_one(ikey="resend_sms_update_smscampaignsubscriber", timeout=LOCK_EXPIRE)
    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.warning("TASK :: RESEND sms")

        for sms_campaign in SMSCampaign.objects.get_running_sms_campaign():
            logger.info("=> SMS Campaign name %s (id:%s)" % (sms_campaign.name, sms_campaign.id))
            sms_maxretry = get_sms_maxretry(sms_campaign)
            limit = 1000
            list_subscriber = SMSCampaignSubscriber.objects.filter(
                sms_campaign=sms_campaign,
                status=SMS_SUBSCRIBER_STATUS.IN_PROCESS)[:limit]

            if not list_subscriber:
                #Go to the next campaign
                logger.info("No subscribers in this campaign (id:%s)" % (sms_campaign.id))
                continue

            for subscriber in list_subscriber:
                if not subscriber.message:
                    logger.error("=> SMS with No Message")
                    subscriber.status = SMS_SUBSCRIBER_STATUS.FAIL  # 'FAIL'
                    subscriber.save()
                    continue

                logger.warning("=> SMS Message Status = %s" % subscriber.message.status)
                if subscriber.message.status == 'Failed':
                    # check sms_maxretry
                    if subscriber.count_attempt >= sms_maxretry:
                        subscriber.status = SMS_SUBSCRIBER_STATUS.FAIL  # 'FAIL'
                        subscriber.save()
                    else:

                        text_message = subscriber.contact.replace_tag(subscriber.sms_campaign.text_message)
                        logger.info("SendMessage text_message:%s" % text_message)

                        # Create Message object
                        msg_obj = SMSMessage.objects.create(
                            content=text_message,
                            recipient_number=subscriber.contact.contact,
                            sender=subscriber.sms_campaign.user,
                            sender_number=subscriber.sms_campaign.callerid,
                            status='Unsent',
                            content_type=ContentType.objects.get(model='smscampaignsubscriber'),
                            object_id=subscriber.id,
                            sms_campaign=sms_campaign,
                        )

                        # Send sms
                        SendMessage.delay(msg_obj.id, subscriber.sms_campaign.sms_gateway_id)

                        subscriber.message = msg_obj
                        subscriber.last_attempt = datetime.utcnow().replace(tzinfo=utc)
                        subscriber.count_attempt += 1
                        subscriber.save()

                if subscriber.message.status == 'Sent' or subscriber.message.status == 'Delivered':
                    subscriber.status = SMS_SUBSCRIBER_STATUS.COMPLETE  # 'COMPLETE'
                    subscriber.save()
