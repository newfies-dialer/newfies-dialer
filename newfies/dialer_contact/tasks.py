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
from celery.decorators import task
# from celery.task import Task
from celery.utils.log import get_task_logger
from dialer_campaign.models import Campaign, Subscriber
from user_profile.models import UserProfile
# from common.only_one_task import only_one

logger = get_task_logger(__name__)


@task()
def collect_subscriber(campaign_id):
    """
    This task will collect all the contact and create the Subscriber
    if the phonebook_id is no in the list of imported_phonebook IDs.

    **Attributes**:

        * ``campaign_id`` - Campaign ID
    """
    logger.debug("Collect subscribers for the campaign = %s" % str(campaign_id))

    #Retrieve the list of active contact
    obj_campaign = Campaign.objects.get(id=campaign_id)
    list_phonebook = obj_campaign.phonebook.all()

    for item_phonebook in list_phonebook:
        phonebook_id = item_phonebook.id

        # check if phonebook_id is missing in imported_phonebook list
        if not str(phonebook_id) in obj_campaign.imported_phonebook.split(','):
            #Run import
            logger.info("ImportPhonebook %d for campaign = %d" % (phonebook_id, campaign_id))

            #Faster method, ask the Database to do the job
            importcontact_custom_sql(campaign_id, phonebook_id)

            #Add the phonebook id to the imported list
            if obj_campaign.imported_phonebook == '':
                sep = ''
            else:
                sep = ','
            obj_campaign.imported_phonebook = obj_campaign.imported_phonebook + \
                '%s%d' % (sep, phonebook_id)
            obj_campaign.save()

    #Count contact imported
    count_contact = Subscriber.objects.filter(campaign=campaign_id).count()
    obj_campaign.totalcontact = count_contact
    obj_campaign.save()

    return True


def importcontact_custom_sql(campaign_id, phonebook_id):
    # Call PL-SQL stored procedure
    #Subscriber.importcontact_pl_sql(campaign_id, phonebook_id)

    # max_subr_cpg = max number of subscriber per campaign,
    # That is going to be checked when a contact is going to be imported
    # to the subscriber list

    #TODO: to review first... accr max_subr_cpn/max_subr_cpg
    campaign_obj = Campaign.objects.get(pk=campaign_id)
    max_subr_cpg = UserProfile.objects.get(user=campaign_obj.user).dialersetting.max_subr_cpg

    if max_subr_cpg > 0:
        #Check how many we are going to import and how many exist for that campaign already
        imported_subscriber_count = Subscriber.objects.filter(campaign_id=campaign_id).count()
        allowed_import = max_subr_cpg - imported_subscriber_count
        if allowed_import > 0:
            #handle negative value for to_import
            limit_import = 'LIMIT %d' % allowed_import
        else:
            limit_import = 'LIMIT 0'
    else:
        limit_import = ''

    from django.db import connection, transaction
    cursor = connection.cursor()
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        # Data insert operation - http://stackoverflow.com/questions/12451053/django-bulk-create-with-ignore-rows-that-cause-integrityerror
        sqlimport = "LOCK TABLE dialer_subscriber IN EXCLUSIVE MODE;" \
            "INSERT INTO dialer_subscriber (contact_id, "\
            "campaign_id, duplicate_contact, status, created_date, updated_date) "\
            "SELECT id, %d, contact, 1, NOW(), NOW() FROM dialer_contact "\
            "WHERE phonebook_id=%d AND dialer_contact.status=1 AND NOT EXISTS (" \
            "SELECT 1 FROM dialer_subscriber WHERE "\
            "dialer_subscriber.campaign_id=%d "\
            "AND dialer_contact.id = dialer_subscriber.contact_id ) %s;" % \
            (campaign_id, phonebook_id, campaign_id, limit_import)
    else:
        # MYSQL Support removed
        logger.error("Database not supported (%s)" % settings.DATABASES['default']['ENGINE'])
        return False

    cursor.execute(sqlimport)
    transaction.commit_unless_managed()

    return True
