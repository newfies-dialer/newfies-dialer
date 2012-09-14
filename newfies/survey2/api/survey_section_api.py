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

from django.contrib.auth.models import User
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie import fields

from api.user_api import UserResource
from survey2.api.survey_api import SurveyResource
from survey2.models import Survey, Section


class SectionValidation(Validation):
    """
    Section Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        survey_id = bundle.data.get('survey')
        if survey_id:
            try:
                survey_id = Survey.objects.get(id=survey_id).id
                bundle.data['survey'] = '/api/v1/survey/%s/' % survey_id
            except:
                errors['survey'] = ["The Survey ID doesn't exist!"]
        return errors


class SectionResource(ModelResource):
    """
    **Attributes**:

        * ``question`` - survey question
        * ``survey`` - survey ID
        * ``audio_message`` - audio file
        * ``message_type`` - Audio / Text2Speech

    **Validation**:

        * SectionValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"question": "survey que", "tags": "", "user": "1", "survey": "1", "message_type": "1"}' http://localhost:8000/api/v1/section/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/section/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/section/?format=json

        Response::

            {
                "meta":{
                  "limit":20,
                  "next":null,
                  "offset":0,
                  "previous":null,
                  "total_count":2
                },
                "objects":[
                   {
                      "created_date":"2011-12-15T13:10:49",
                      "id":"1",
                      "message_type":1,
                      "order":1,
                      "question":"Test Servey Qus",
                      "resource_uri":"/api/v1/section/1/",
                      "surveyapp":{
                         "created_date":"2011-12-15T09:55:25",
                         "description":"",
                         "id":"5",
                         "name":"new test",
                         "order":2,
                         "resource_uri":"/api/v1/survey/5/",
                         "updated_date":"2011-12-15T09:55:25",
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
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"question": "survey que", "tags": "", "user": "1", "surveyapp": "1", "message_type": "1"}' http://localhost:8000/api/v1/section/%section_id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/section/%section_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/section/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    survey = fields.ForeignKey(SurveyResource, 'survey', full=True)

    class Meta:
        queryset = Section.objects.all()
        resource_name = 'section'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = SectionValidation()
        # default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)
