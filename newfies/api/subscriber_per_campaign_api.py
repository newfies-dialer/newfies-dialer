# -*- coding: utf-8 -*-

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

from django.conf.urls import url
from django.db import connection
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.throttle import BaseThrottle
from tastypie.exceptions import BadRequest
from dialer_contact.models import Contact
from dialer_campaign.models import Campaign
import logging

logger = logging.getLogger('newfies.filelog')


def get_contact(id):
    """
    >>> get_contact(0)
    ''
    """
    try:
        con_obj = Contact.objects.get(pk=id)
        return con_obj.contact
    except:
        return ''


class SubscriberPerCampaignResource(ModelResource):
    """
    **Attributes Details**:

        * ``contact_id`` - contact id
        * ``count_attempt`` - no of call attempt
        * ``completion_count_attempt`` - no of call attempt for completion
        * ``last_attempt`` - last call attempt
        * ``status`` - call status

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/subscriber_per_campaign/%campaign_id%/?format=json

                or

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/subscriber_per_campaign/%campaign_id%/%contact%/?format=json

        Response::

            [
               {
                  "contact_id":1,
                  "count_attempt":1,
                  "completion_count_attempt":1,
                  "last_attempt":"2012-01-17T15:28:37",
                  "status":2,
                  "subscriber_id": 1,
                  "contact": "640234123"
               },
               {
                  "contact_id":2,
                  "count_attempt":1,
                  "completion_count_attempt":1,
                  "last_attempt":"2012-02-06T17:00:38",
                  "status":1,
                  "subscriber_id": 2,
                  "contact": "640234000"
               }
            ]

    """
    class Meta:
        resource_name = 'subscriber_per_campaign'
        authorization = Authorization()
        authentication = BasicAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        # default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)

    def prepend_urls(self):
        """Prepend urls"""
        return [
            url(r'^(?P<resource_name>%s)/(.+)/$' % self._meta.resource_name, self.wrap_view('read')),
        ]

    def read(self, request=None, **kwargs):
        """GET method of Subscriber API"""
        logger.debug('Subscriber GET API get called')

        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        logger.debug('Subscriber GET API authorization called!')

        temp_url = request.META['PATH_INFO']
        temp_id = temp_url.split('/api/v1/subscriber_per_campaign/')[1]
        camp_id = temp_id.split('/')[0]
        try:
            contact = temp_id.split('/')[1]
        except:
            contact = False

        cursor = connection.cursor()

        try:
            campaign_id = int(camp_id)
        except:
            error_msg = "No value for Campaign ID !"
            logger.error(error_msg)
            raise BadRequest(error_msg)

        try:
            Campaign.objects.get(id=campaign_id)
        except:
            error_msg = "Campaign ID does not exists!"
            logger.error(error_msg)
            raise BadRequest(error_msg)

        if contact:
            try:
                int(contact)
            except ValueError:
                error_msg = "Wrong value for contact !"
                logger.error(error_msg)
                raise BadRequest(error_msg)

            sql_statement = "SELECT DISTINCT contact_id, last_attempt, "\
                "count_attempt, completion_count_attempt, dialer_subscriber.status,"\
                "dialer_subscriber.id "\
                "FROM dialer_subscriber "\
                "LEFT JOIN dialer_callrequest ON "\
                "subscriber_id=dialer_subscriber.id "\
                "LEFT JOIN dialer_campaign ON "\
                "dialer_callrequest.campaign_id=dialer_campaign.id "\
                "WHERE dialer_subscriber.campaign_id = %s "\
                "AND dialer_subscriber.duplicate_contact = '%s'"\
                % (str(campaign_id), str(contact))

        else:
            sql_statement = "SELECT DISTINCT contact_id, last_attempt, "\
                "count_attempt, completion_count_attempt, dialer_subscriber.status, "\
                "dialer_subscriber.id "\
                "FROM dialer_subscriber "\
                "LEFT JOIN dialer_callrequest ON "\
                "subscriber_id="\
                "dialer_subscriber.id "\
                "LEFT JOIN dialer_campaign ON "\
                "dialer_callrequest.campaign_id=dialer_campaign.id "\
                "WHERE dialer_subscriber.campaign_id"\
                "= %s" % (str(campaign_id))

        cursor.execute(sql_statement)
        row = cursor.fetchall()

        result = []
        for record in row:
            modrecord = {}
            modrecord['contact_id'] = record[0]
            modrecord['last_attempt'] = record[1]
            modrecord['count_attempt'] = record[2]
            modrecord['completion_count_attempt'] = record[3]
            modrecord['status'] = record[3]
            modrecord['subscriber_id'] = record[4]
            modrecord['contact'] = get_contact(record[0])
            result.append(modrecord)

        logger.debug('Subscriber GET API : result ok 200')

        self.log_throttled_access(request)
        return self.create_response(request, result)
