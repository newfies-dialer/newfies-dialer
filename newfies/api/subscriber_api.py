# -*- coding: utf-8 -*-

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

from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie.exceptions import BadRequest
from dialer_contact.models import Contact, Phonebook
from dialer_campaign.models import Campaign, Subscriber
from dialer_campaign.function_def import check_dialer_setting, \
                            dialer_setting_limit

import logging

logger = logging.getLogger('newfies.filelog')


class SubscriberValidation(Validation):
    """
    Subscriber Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}
        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        if check_dialer_setting(request, check_for="contact"):
            errors['contact_dialer_setting'] = ["You have too many contacts \
                per campaign. You are allowed a maximum of %s" % \
                        dialer_setting_limit(request, limit_for="contact")]

        if request.method == 'POST':
            phonebook_id = bundle.data.get('phonebook_id')
            if phonebook_id:
                try:
                    Phonebook.objects.get(id=phonebook_id)
                except Phonebook.DoesNotExist:
                    errors['phonebook_error'] = ["Phonebook is not selected!"]
            else:
                errors['phonebook_error'] = ["Phonebook is not selected!"]

        return errors


class SubscriberResource(ModelResource):
    """
    **Attributes Details**:

        * ``contact`` - contact number of the Subscriber
        * ``last_name`` - last name of the Subscriber
        * ``first_name`` - first name of the Subscriber
        * ``email`` - email id of the Subscriber
        * ``description`` - Short description of the Subscriber
        * ``additional_vars`` - Additional settings for the Subscriber
        * ``phonebook_id`` - the phonebook Id to which we want to add\
        the Subscriber

    **Validation**:

        * SubscriberValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"contact": "650784355", "last_name": "belaid", "first_name": "areski", "email": "areski@gmail.com", "phonebook_id" : "1"}' http://localhost:8000/api/v1/subscriber/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Wed, 18 May 2011 13:23:14 GMT
            Server: WSGIServer/0.1 Python/2.6.2
            Vary: Authorization
            Content-Length: 0
            Location: http://localhost:8000/api/v1/subscriber/1/
            Content-Type: text/plain

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/subscriber/?format=json

        Response::

            {
               "meta":{
                  "limit":20,
                  "next":null,
                  "offset":0,
                  "previous":null,
                  "total_count":1
               },
               "objects":[
                  {
                     "count_attempt":1,
                     "completion_count_attempt":1,
                     "created_date":"2012-01-17T03:58:49",
                     "duplicate_contact":"123456789",
                     "id":"1",
                     "last_attempt":"2012-01-17T15:28:37",
                     "resource_uri":"/api/v1/subscriber/1/",
                     "status":2,
                     "updated_date":"2012-02-07T02:22:19"
                  }
               ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"status": "2", "contact": "123546"}' http://localhost:8000/api/v1/subscriber/%campaign_id%/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    class Meta:
        queryset = Subscriber.objects.all()
        resource_name = 'subscriber'
        authorization = Authorization()
        authentication = BasicAuthentication()
        list_allowed_methods = ['get', 'post', 'put']
        detail_allowed_methods = ['get', 'post', 'put']
        validation = SubscriberValidation()
        filtering = {
            'contact': 'exact',
        }
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)

    def obj_create(self, bundle, request=None, **kwargs):
        """
        TODO: Add doc
        """
        logger.debug('Subscriber POST API get called')

        phonebook_id = bundle.data.get('phonebook_id')
        obj_phonebook = Phonebook.objects.get(id=phonebook_id)

        #this method will also create a record into Subscriber
        #this is defined in signal post_save_add_contact
        new_contact = Contact.objects.create(
            contact=bundle.data.get('contact'),
            last_name=bundle.data.get('last_name'),
            first_name=bundle.data.get('first_name'),
            email=bundle.data.get('email'),
            description=bundle.data.get('description'),
            status=1,  # default active
            phonebook=obj_phonebook)
        # Assign new contact object
        bundle.obj = new_contact

        # Insert the contact to the subscriber also for
        # each campaign using this phonebook

        campaign_obj = Campaign.objects.filter(
            phonebook=obj_phonebook,
            user=request.user)
        for c_campaign in campaign_obj:
            imported_phonebook = []
            if c_campaign.imported_phonebook:
                # for example:- c_campaign.imported_phonebook = 1,2,3
                # So convert imported_phonebook string into int list
                imported_phonebook = map(int,
                    c_campaign.imported_phonebook.split(','))

            phonebook_list = c_campaign.phonebook\
                                .values_list('id', flat=True)\
                                .all()
            phonebook_list = map(int, phonebook_list)

            common_phonebook_list = []
            if phonebook_list:
                common_phonebook_list = list(set(imported_phonebook) &\
                                            set(phonebook_list))
                if common_phonebook_list:
                    contact_list = Contact.objects\
                                .filter(phonebook__in=common_phonebook_list,
                                    status=1)
                    for con_obj in contact_list:
                        try:
                            Subscriber.objects.create(
                                contact=con_obj,
                                duplicate_contact=con_obj.contact,
                                status=1,  # START
                                campaign=c_campaign)
                        except:
                            #TODO Catching duplicate error
                            pass

        logger.debug('Subscriber POST API : result ok 200')
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_update``.
        """
        logger.debug('Subscriber PUT API get called')

        temp_url = request.META['PATH_INFO']
        temp_id = temp_url.split('/api/v1/subscriber/')[1]
        campaign_id = temp_id.split('/')[0]

        try:
            campaign_obj = Campaign.objects.get(id=campaign_id)
        except:
            error_msg = "Campaign ID does not exists!"
            logger.error(error_msg)
            raise BadRequest(error_msg)

        try:
            subscriber = Subscriber.objects\
                .get(duplicate_contact=bundle.data.get('contact'),
                    campaign=campaign_obj)
            subscriber.status = bundle.data.get('status')
            subscriber.save()
        except:
            error_msg = "A model matching arguments could not be found."
            logger.error(error_msg)
            raise BadRequest(error_msg)

        logger.debug('Subscriber PUT API : result ok 200')
        return bundle
