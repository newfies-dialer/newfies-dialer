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

from django.contrib.auth.models import User
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie import fields

from api.user_api import UserResource
from survey.api.survey_api import SurveyAppResource
from survey.models import SurveyApp, SurveyQuestion


class SurveyQuestionValidation(Validation):
    """
    SurveyQuestion Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        surveyapp_id = bundle.data.get('surveyapp')
        if surveyapp_id:
            try:
                surveyapp_id = SurveyApp.objects.get(id=surveyapp_id).id
                bundle.data['surveyapp'] = '/api/v1/survey/%s/' % surveyapp_id
            except:
                errors['survey'] = ["The Survey app ID doesn't exist!"]

        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        return errors


class SurveyQuestionResource(ModelResource):
    """
    **Attributes**:

        * ``question`` - survey question
        * ``user`` - User ID
        * ``surveyapp`` - surveyapp ID
        * ``audio_message`` - audio file
        * ``message_type`` - Audio / Text2Speech

    **Validation**:

        * SurveyQuestionValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"question": "survey que", "tags": "", "user": "1", "surveyapp": "1", "message_type": "1"}' http://localhost:8000/api/v1/survey_question/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/survey_question/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/survey_question/?format=json

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
                      "resource_uri":"/api/v1/survey_question/1/",
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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"question": "survey que", "tags": "", "user": "1", "surveyapp": "1", "message_type": "1"}' http://localhost:8000/api/v1/survey_question/%survey_question_id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey_question/%survey_question_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey_question/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    user = fields.ForeignKey(UserResource, 'user', full=True)
    surveyapp = fields.ForeignKey(SurveyAppResource, 'surveyapp', full=True)
    class Meta:
        queryset = SurveyQuestion.objects.all()
        resource_name = 'survey_question'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = SurveyQuestionValidation()
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour
