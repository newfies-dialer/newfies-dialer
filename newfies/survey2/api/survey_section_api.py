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

        type = bundle.data.get('type')
        if not bundle.data.get('question'):
            errors['question'] = ["Please add question field"]

        """
        if type == 2:
            if not bundle.data.get('key_0'):
                errors['key_0'] = ["Please add key field"]

        if type == 3:
            if not bundle.data.get('rating_laps'):
                errors['key_0'] = ["Please add rating_laps field"]
        """

        return errors


class SectionResource(ModelResource):
    """
    **Attributes**:

        * ``type`` - survey name.
        * ``question`` -
        * ``phrasing`` -
        * ``audiofile`` -
        * ``use_audiofile`` -
        * ``invalid_audiofile`` -
        * ``retries`` -
        * ``timeout`` -
        * ``key_0`` -
        * ``key_1`` -
        * ``key_2`` -
        * ``key_3`` -
        * ``key_4`` -
        * ``key_5`` -
        * ``key_6`` -
        * ``key_7`` -
        * ``key_8`` -
        * ``key_9`` -
        * ``rating_laps`` -
        * ``validate_number`` -
        * ``number_digits`` -
        * ``min_number`` -
        * ``max_number`` -
        * ``dial_phonenumber`` -
        * ``continue_survey`` -

    **Validation**:

        * SectionValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"type": 1, "question": "survey que", "survey": 1}' http://localhost:8000/api/v1/section/

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
                  "total_count":4
               },
               "objects":[
                  {
                     "continue_survey":false,
                     "created_date":"2012-09-13T08:06:05.344297",
                     "dial_phonenumber":null,
                     "id":"15",
                     "key_0":null,
                     "key_1":null,
                     "key_2":null,
                     "key_3":null,
                     "key_4":null,
                     "key_5":null,
                     "key_6":null,
                     "key_7":null,
                     "key_8":null,
                     "key_9":null,
                     "max_number":100,
                     "min_number":1,
                     "number_digits":null,
                     "order":1,
                     "phrasing":"this is test question hello",
                     "question":"this is test question",
                     "rating_laps":null,
                     "resource_uri":"/api/v1/section/15/",
                     "retries":0,
                     "survey":{
                        "created_date":"2012-09-13T08:05:51.458779",
                        "description":"",
                        "id":"2",
                        "name":"sample survey",
                        "order":1,
                        "resource_uri":"/api/v1/survey/2/",
                        "updated_date":"2012-09-14T07:56:30.304371",
                        "user":{
                           "first_name":"",
                           "id":"1",
                           "last_login":"2012-09-11T09:14:16.986223",
                           "last_name":"",
                           "resource_uri":"/api/v1/user/1/",
                           "username":"areski"
                        }
                     },
                     "timeout":null,
                     "type":1,
                     "updated_date":"2012-09-13T08:06:14.565249",
                     "use_audiofile":false,
                     "validate_number":true
                  }
               ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"question": "survey que", "type": "1", "survey": 1}' http://localhost:8000/api/v1/section/%section_id%/

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
