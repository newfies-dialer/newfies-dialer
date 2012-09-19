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

from celery.task import PeriodicTask
from dialer_campaign.models import Campaign
from celery.decorators import task
from django.conf import settings


@task()
def collect_subscriber_optimized(campaign_id):
    """This task will collect all the subscribers

    **Attributes**:

        * ``campaign_id`` - Campaign ID
    """
    logger = collect_subscriber_optimized.get_logger()
    logger.debug("Collect subscribers for the campaign = %s" % \
                str(campaign_id))

    #Retrieve the list of active contact
    obj_campaign = Campaign.objects.get(id=campaign_id)

    list_phonebook = obj_campaign.phonebook.all()

    for item_phonebook in list_phonebook:
        phonebook_id = item_phonebook.id

        # check if phonebook_id is missing in imported_phonebook list
        if not str(phonebook_id) in obj_campaign.imported_phonebook.split(','):
            #Run import
            import_phonebook.delay(obj_campaign.id, phonebook_id)

    return True


def importcontact_custom_sql(logger, campaign_id, phonebook_id):
    # Call PL-SQL stored procedure
    #CampaignSubscriber.importcontact_pl_sql(campaign_id, phonebook_id)

    #TODO Support PostgreSQL
    if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.mysql':
        logger.info("Mysql is only supported at the moment")
        return True

    from django.db import connection, transaction
    cursor = connection.cursor()

    # Data insert operation - commit required
    sqlimport = "INSERT IGNORE INTO dialer_campaign_subscriber (contact_id, "\
        "campaign_id, duplicate_contact, status, created_date, updated_date) "\
        "SELECT id, %d, contact, 1, NOW(), NOW() FROM dialer_contact "\
        "WHERE phonebook_id=%d AND dialer_contact.status=1" % \
        (campaign_id, phonebook_id)

    cursor.execute(sqlimport)
    transaction.commit_unless_managed()

    return True


@task()
def import_phonebook(campaign_id, phonebook_id):
    """
    Read all the contact from phonebook_id and insert into campaignsubscriber
    """
    logger = import_phonebook.get_logger()
    logger.info("\nTASK :: import_phonebook")

    #TODO: Add a semafore

    obj_campaign = Campaign.objects.get(id=campaign_id)

    #Faster method, ask the Database to do the job
    importcontact_custom_sql(logger, campaign_id, phonebook_id)

    #Add the phonebook id to the imported list
    if obj_campaign.imported_phonebook == '':
        sep = ''
    else:
        sep = ','
    obj_campaign.imported_phonebook = obj_campaign.imported_phonebook + \
            '%s%d' % (sep, phonebook_id)
    obj_campaign.save()

    return True
