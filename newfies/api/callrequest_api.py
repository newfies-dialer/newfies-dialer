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
from django.contrib.contenttypes.models import ContentType

from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie import fields

from api.user_api import UserResource
from api.content_type_api import ContentTypeResource
from dialer_cdr.models import Callrequest


class CallrequestValidation(Validation):
    """
    Callrequest Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        content_type = bundle.data.get('content_type')
        if content_type == 'voice_app' or content_type == 'survey':
            try:
                content_type_id = ContentType.objects\
                .get(app_label=str(content_type)).id
                bundle.data['content_type'] = '/api/v1/contenttype/%s/'\
                % content_type_id
            except:
                errors['chk_content_type'] = ["The ContentType doesn't exist!"]
        else:
            errors['chk_content_type'] = ["Wrong option. \
                                            Enter 'voice_app' or 'survey' !"]

        object_id = bundle.data.get('object_id')
        if object_id:
            try:
                bundle.data['object_id'] = object_id
            except:
                errors['chk_object_id'] = ["App object Id doesn't exist!"]

        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        if request.method == 'POST':
            rq_count = Callrequest.objects\
            .filter(request_uuid=bundle.data.get('request_uuid'))\
            .count()
            if (rq_count != 0):
                errors['chk_request_uuid'] = ["The Request uuid duplicated!"]

        return errors


class CallrequestResource(ModelResource):
    """
    **Attributes**:

        * ``request_uuid`` - Unique id
        * ``call_time`` - Total call time
        * ``call_type`` - Call type
        * ``status`` - Call request status
        * ``callerid`` - Caller ID
        * ``callrequest_id``- Callrequest Id
        * ``timeout`` -
        * ``timelimit`` -
        * ``status`` -
        * ``campaign_subscriber`` -
        * ``campaign`` -
        * ``phone_number`` -
        * ``extra_dial_string`` -
        * ``extra_data`` -
        * ``num_attempt`` -
        * ``last_attempt_time`` -
        * ``result`` -
        * ``hangup_cause`` -
        * ``last_attempt_time`` -


    **Relationships**:

        * ``content_type`` - Defines the application (``voice_app`` or ``survey``) to use when the \
                             call is established on the A-Leg
        * ``object_id`` - Defines the object of content_type application

    **Validation**:

        * CallrequestValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"request_uuid": "2342jtdsf-00123", "call_time": "2011-10-20 12:21:22", "phone_number": "8792749823", "content_type":"voice_app", "object_id":1, "timeout": "30000", "callerid": "650784355", "call_type": "1"}' http://localhost:8000/api/v1/callrequest/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/app/campaign/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/callrequest/?format=json

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/callrequest/%callreq_id%/?format=json

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
                     "call_time":"2011-10-20T12:21:22",
                     "call_type":1,
                     "callerid":"650784355",
                     "created_date":"2011-10-14T07:33:41",
                     "extra_data":"",
                     "extra_dial_string":"",
                     "hangup_cause":"",
                     "id":"1",
                     "last_attempt_time":null,
                     "num_attempt":0,
                     "phone_number":"8792749823",
                     "request_uuid":"2342jtdsf-00123",
                     "resource_uri":"/api/v1/callrequest/1/",
                     "result":"",
                     "status":1,
                     "timelimit":3600,
                     "timeout":30000,
                     "updated_date":"2011-10-14T07:33:41",
                     "user":{
                        "first_name":"",
                        "id":"1",
                        "last_login":"2011-10-11T01:03:42",
                        "last_name":"",
                        "resource_uri":"/api/v1/user/1/",
                        "username":"areski"
                     },
                  }
               ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"content_type":"voice_app", "object_id":1, "status": "5"}' http://localhost:8000/api/v1/callrequest/%callrequest_id%/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    user = fields.ForeignKey(UserResource, 'user', full=True)
    content_type = fields.ForeignKey(ContentTypeResource,
        'content_type', full=True)

    class Meta:
        queryset = Callrequest.objects.all()
        resource_name = 'callrequest'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = CallrequestValidation()
        list_allowed_methods = ['get', 'post', 'put']
        detail_allowed_methods = ['get', 'post', 'put']
        # default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)
