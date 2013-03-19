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
from tastypie.resources import ModelResource, ALL
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie import fields
from api.user_api import UserResource
from dnc.models import DNC


class DNCValidation(Validation):
    """DNC Validation Class"""
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': 'Data set is empty'}

        errors = {}

        for key, value in bundle.data.items():
            if not isinstance(value, basestring):
                continue
        # Not working
        #try:
        #    bundle.data['user'] = '/api/v1/user/%s/' % request.user.id
        #except:
        #    errors['chk_user'] = ["The User doesn't exist!"]

        return errors


class DNCResource(ModelResource):
    """DNC Model

    **Attributes**:

        * ``name`` - DNC name

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "Sample DNC"}' http://localhost:8000/api/v1/dnc/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/dnc/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/dnc/?format=json

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
                     "created_date":"2013-03-15T18:28:30.208000",
                     "id":1,
                     "name":"sample dnc",
                     "resource_uri":"/api/v1/dnc/1/",
                     "updated_date":"2013-03-15T18:28:30.208000"
                  },
                  {
                     "created_date":"2013-03-18T18:10:36.506007",
                     "id":2,
                     "name":"more dnc",
                     "resource_uri":"/api/v1/dnc/2/",
                     "updated_date":"2013-03-18T18:10:36.506065"
                  }
               ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"name": "Test DNC"}' http://localhost:8000/api/v1/dnc/%dnc_id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/dnc/%dnc_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/dnc/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    **Search**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/dnc/?name='test dnc'
    """
    user = fields.ForeignKey(UserResource, 'user', full=True)
    class Meta:
        queryset = DNC.objects.all()
        resource_name = 'dnc'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = DNCValidation()
        filtering = {
            'name': ALL,
        }
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)
