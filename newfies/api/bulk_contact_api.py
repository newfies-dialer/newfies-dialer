# -*- coding: utf-8 -*-

#
# CDR-Stats License
# http://www.cdr-stats.org
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

from dialer_campaign.models import Contact, Phonebook
from dialer_campaign.function_def import check_dialer_setting, \
                                    dialer_setting_limit

import logging

logger = logging.getLogger('newfies.filelog')


class BulkContactValidation(Validation):
    """BulkContact Validation Class"""
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']
        if check_dialer_setting(request, check_for="contact"):
            errors['contact_dialer_setting'] = ["You have too many contacts \
                per campaign. You are allowed a maximum of %s" %\
                            dialer_setting_limit(request, limit_for="contact")]

        phonebook_id = bundle.data.get('phonebook_id')
        if phonebook_id:
            try:
                Phonebook.objects.get(id=phonebook_id)
            except Phonebook.DoesNotExist:
                errors['phonebook_error'] = ["Phonebook is not selected!"]
        else:
            errors['phonebook_error'] = ["Phonebook is not selected!"]

        return errors


class BulkContactResource(ModelResource):
    """API to bulk create contacts

    **Attributes**

        * ``contact`` - contact number of the Subscriber
        * ``phonebook_id`` - the phonebook Id to which we want to add\
        the contact

    **Validation**:

        * BulkContactValidation()

    **CURL Usage**::

        curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"phonebook_id": "1", "phoneno_list" : "12345,54344"}' http://localhost:8000/api/v1/bulkcontact/

    **Response**::

        HTTP/1.0 201 CREATED
        Date: Thu, 13 Oct 2011 11:42:44 GMT
        Server: WSGIServer/0.1 Python/2.7.1+
        Vary: Accept-Language, Cookie
        Content-Type: text/html; charset=utf-8
        Location: http://localhost:8000/api/v1/bulkcontact/None/
        Content-Language: en-us
    """
    class Meta:
        queryset = Contact.objects.all()
        resource_name = 'bulkcontact'
        authorization = Authorization()
        authentication = BasicAuthentication()
        allowed_methods = ['post']
        validation = BulkContactValidation()
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)

    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        logger.debug('BulkContact API get called')

        bundle.obj = self._meta.object_class()
        bundle = self.full_hydrate(bundle)

        phoneno_list = bundle.data.get('phoneno_list')
        phonebook_id = bundle.data.get('phonebook_id')
        phonenolist = list(phoneno_list.split(","))

        try:
            obj_phonebook = Phonebook.objects.get(id=phonebook_id)
            new_contact_count = 0
            for phoneno in phonenolist:
                new_contact = Contact.objects.create(
                    phonebook=obj_phonebook,
                    contact=phoneno,)
                new_contact_count = new_contact_count + 1
                new_contact.save()
        except:
            error_msg = "The contact duplicated (%s)!\n" % phoneno
            logger.error(error_msg)
            raise BadRequest(error_msg)

        logger.debug('BulkContact API : result ok 200')
        return bundle
