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
from survey.models import Survey


class SurveyValidation(Validation):
    """SurveyApp Validation Class"""
    def is_valid(self, bundle, request=None):
        errors = {}
        if not bundle.data:
            errors['Data'] = ['Data set is empty']
        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        return errors


class SurveyResource(ModelResource):
    """
    **Attributes**:

        * ``name`` - survey name
        * ``description`` -
        * ``user_id`` - User ID

    **Validation**:

        * SurveyValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "surveyname", "description": ""}' http://localhost:8000/api/v1/survey/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/survey/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/survey/?format=json

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
                     "created_date":"2011-04-08T07:55:05",
                     "description":"This is default survey",
                     "id":"1",
                     "name":"survey name",
                     "resource_uri":"/api/v1/survey/1/",
                     "updated_date":"2011-04-08T07:55:05",
                     "user":{
                        "first_name":"",
                        "id":"1",
                        "last_login":"2011-10-11T01:03:42",
                        "last_name":"",
                        "resource_uri":"/api/v1/user/1/",
                        "username":"areski"
                     }
                  }
               ]
            }


    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"name": "survey name", "description": ""}' http://localhost:8000/api/v1/survey/%survey_id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey/%survey_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey/

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

    class Meta:
        queryset = Survey.objects.all()
        resource_name = 'survey'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = SurveyValidation()
        list_allowed_methods = ['post', 'get', 'put', 'delete']
        detail_allowed_methods = ['post', 'get', 'put', 'delete']
        # default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)


