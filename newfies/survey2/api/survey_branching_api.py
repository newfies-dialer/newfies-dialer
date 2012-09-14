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
from tastypie import fields

from survey2.api.survey_section_api import SectionResource
from survey2.models import Section, Branching


class BranchingValidation(Validation):
    """
    BranchingValidation Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}
        if not bundle.data:
            errors['Data'] = ['Data set is empty']
        key = bundle.data.get('key')
        if key:
            dup_count = Branching.objects.filter(key=str(key)).count()
            if request.method == 'POST':
                if dup_count >= 1:
                    errors['duplicate_key'] = ["Key is already exist!"]
            if request.method == 'PUT':
                if dup_count > 1:
                    errors['duplicate_key'] = ["Key is already exist!"]

        section_id = bundle.data.get('section')
        if section_id:
            try:
                section_id = Section.objects.get(id=section_id).id
                bundle.data['section_id'] = \
                      '/api/v1/section_id/%s/' % section_id
            except:
                errors['section_id'] = \
                      ["The Section ID doesn't exist!"]

        return errors


class BranchingResource(ModelResource):
    """
    **Attributes**:

        * ``keys`` - section's response key
        * ``section`` - survey question ID

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
                     "created_date":"2011-12-15T14:54:50",
                     "id":"3",
                     "key":"YES",
                     "keyvalue":"1",
                     "resource_uri":"/api/v1/branching/3/",
                     "surveyquestion":{
                        "created_date":"2011-12-15T13:10:49",
                        "id":"17",
                        "message_type":1,
                        "order":1,
                        "question":"Servey Qus",
                        "resource_uri":"/api/v1/section/17/",
                        "surveyapp":{
                           "created_date":"2011-12-15T09:55:25",
                           "description":"",
                           "id":"5",
                           "name":"new test",
                           "order":2,
                           "resource_uri":"/api/v1/survey/5/",
                           "updated_date":"2011-12-15T14:45:46",
                           "user":{
                              "first_name":"",
                              "id":"1",
                              "last_login":"2011-12-14T07:26:00",
                              "last_name":"",
                              "resource_uri":"/api/v1/user/1/",
                              "username":"areski"
                           }
                        },
                        "tags":"",
                        "updated_date":"2011-12-15T13:10:49",
                        "user":{
                           "first_name":"",
                           "id":"1",
                           "last_login":"2011-12-14T07:26:00",
                           "last_name":"",
                           "resource_uri":"/api/v1/user/1/",
                           "username":"areski"
                        }
                     },
                     "updated_date":"2011-12-15T14:54:50"
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
    section = fields.ForeignKey(SectionResource,
                                'section', full=True)

    class Meta:
        queryset = Branching.objects.all()
        resource_name = 'branching'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = BranchingValidation()
        # default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)
        pass_request_user_to_django = True
