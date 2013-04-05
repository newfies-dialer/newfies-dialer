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

from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie.exceptions import BadRequest
from tastypie import fields
from survey.api.survey_section_api import SectionResource
from survey.models import Section_template, Branching_template
import logging

logger = logging.getLogger('newfies.filelog')


class BranchingValidation(Validation):
    """
    BranchingValidation Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}
        if not bundle.data:
            errors['Data'] = 'Data set is empty'
        keys = bundle.data.get('keys')
        if keys and keys != '':
            dup_count = Branching_template.objects.filter(keys=str(keys)).count()
            if bundle.request.method == 'POST':
                if dup_count >= 1:
                    errors['duplicate_key'] = "Keys is already exist!"
            if bundle.request.method == 'PUT':
                if dup_count > 1:
                    errors['duplicate_key'] = "Keys is already exist!"
        else:
            errors['keys'] = "Please enter Keys."

        section_id = bundle.data.get('section')
        if section_id and section_id != '':
            try:
                section_id = Section_template.objects.get(id=section_id).id
                bundle.data['section'] = section_id
            except:
                errors['section'] = "The Section ID doesn't exist!"
        else:
            errors['section'] = "Please enter section."

        goto = bundle.data.get('goto')
        if goto and goto != '':
            try:
                section_id = Section_template.objects.get(id=goto).id
                bundle.data['goto'] = section_id
            except:
                errors['goto'] = "The Section ID doesn't exist!"

        if errors:
            raise BadRequest(errors)
        return errors


class BranchingResource(ModelResource):
    """
    **Attributes**:

        * ``keys`` - section's response key
        * ``section`` - survey question ID
        * ``goto`` - survey question ID

    **Validation**:

        * BranchingValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"keys": "1", "section": "1"}' http://localhost:8000/api/v1/branching/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/branching/1/
            Content-Language: en-us

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/branching/?format=json

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
                     "created_date":"2013-03-21T11:00:51.852136",
                     "id":1,
                     "keys":"0",
                     "resource_uri":"/api/v1/branching/1/",
                     "section":"/api/v1/section/1/",
                     "updated_date":"2013-03-21T11:00:51.852173"
                  }
               ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"keys": "1", "section": "1"}' http://localhost:8000/api/v1/branching/%branching_id%/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    **Delete**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/branching/%branching_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/branching/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    """
    section = fields.ForeignKey(SectionResource, 'section')
    goto = fields.ForeignKey(SectionResource, 'goto',
        null=True, blank=True)

    class Meta:
        queryset = Branching_template.objects.all()
        resource_name = 'branching'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = BranchingValidation()
        # default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)
        pass_request_user_to_django = True

    def full_hydrate(self, bundle, request=None):
        bundle.obj.keys = bundle.data.get('keys')
        bundle.obj.section = Section_template.objects.get(pk=bundle.data.get('section'))
        if bundle.data.get('goto'):
            bundle.obj.goto = Section_template.objects.get(pk=bundle.data.get('goto'))
        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        logger.debug('Branching API get called')

        self.is_valid(bundle)
        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        bundle = self.full_hydrate(bundle)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        bundle.obj.save()

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        logger.debug('Branching API : Result ok 200')
        return bundle
