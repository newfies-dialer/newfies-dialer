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
from tastypie import fields

from survey.api.survey_question_api import SurveyQuestionResource
from survey.models import SurveyQuestion, SurveyResponse


class SurveyResponseValidation(Validation):
    """
    SurveyResponse Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        key = bundle.data.get('key')
        if key:
            dup_count = SurveyResponse.objects.filter(key=str(key)).count()
            if request.method == 'POST':
                if dup_count >= 1:
                    errors['duplicate_key'] = ["Key is already exist!"]
            if request.method == 'PUT':
                if dup_count > 1:
                    errors['duplicate_key'] = ["Key is already exist!"]

        surveyquestion_id = bundle.data.get('surveyquestion')
        if surveyquestion_id:
            try:
                surveyquestion_id = SurveyQuestion.objects.get(id=surveyquestion_id).id
                bundle.data['surveyquestion'] = '/api/v1/survey_question/%s/' % surveyquestion_id
            except:
                errors['surveyquestion'] = ["The Survey question ID doesn't exist!"]

        return errors


class SurveyResponseResource(ModelResource):
    """
    **Attributes**:

        * ``key`` - survey question's response key
        * ``key value`` - response key value
        * ``surveyquestion`` - survey question ID

    **Validation**:

        * SurveyResponseValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"key": "Apple", "keyvalue": "1", "surveyquestion": "1"}' http://localhost:8000/api/v1/survey_response/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/survey_response/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/survey_response/?format=json

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
                     "resource_uri":"/api/v1/survey_response/3/",
                     "surveyquestion":{
                        "created_date":"2011-12-15T13:10:49",
                        "id":"17",
                        "message_type":1,
                        "order":1,
                        "question":"Servey Qus",
                        "resource_uri":"/api/v1/survey_question/17/",
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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"key": "Apple", "keyvalue": "1", "surveyquestion": "1"}' http://localhost:8000/api/v1/survey_response/%survey_response_id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey_response/%survey_response_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey_response/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    """
    surveyquestion = fields.ForeignKey(SurveyQuestionResource, 'surveyquestion', full=True)
    class Meta:
        queryset = SurveyResponse.objects.all()
        resource_name = 'survey_response'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = SurveyResponseValidation()
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour
