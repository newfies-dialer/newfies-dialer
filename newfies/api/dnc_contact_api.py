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
from dnc.models import DNCContact
from api.dnc_api import DNCResource


class DNCContactValidation(Validation):
    """DNC Contact Validation Class"""
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': 'Please enter data'}

        errors = {}

        for key, value in bundle.data.items():
            if not isinstance(value, basestring):
                continue
        return errors


class DNCContactResource(ModelResource):
    """DNCContact Model

    **Attributes**:

        * ``phone_number`` -
        * ``dnc_id`` - DNC ID

    **Validation**:

        * DNCContactValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"phone_number": "1234675", "dnc": "/api/v1/dnc/1/"}' http://localhost:8000/api/v1/dnc_contact/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/dnc_contact/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/dnc_contact/?format=json

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
                     "created_date":"2013-03-15T18:29:35.400000",
                     "dnc":{
                        "created_date":"2013-03-15T18:28:30.208000",
                        "id":1,
                        "name":"sample dnc",
                        "resource_uri":"/api/v1/dnc/1/",
                        "updated_date":"2013-03-15T18:28:30.208000"
                     },
                     "id":1,
                     "phone_number":"123456789",
                     "resource_uri":"/api/v1/dnc_contact/1/",
                     "updated_date":"2013-03-15T18:29:35.400000"
                  },
               ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"phone_number": "123456"}' http://localhost:8000/api/v1/dnc_contact/%dnc_contact_id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/dnc_contact/%dnc_contact_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/dnc_contact/

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

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/dnc_contact/?phone_number=12345

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/dnc_contact/?dnc=1
    """
    dnc = fields.ForeignKey(DNCResource, 'dnc', full=True)
    class Meta:
        queryset = DNCContact.objects.all()
        resource_name = 'dnc_contact'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = DNCContactValidation()
        filtering = {
            'phone_number': ALL,
            'dnc': ALL,
        }
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)
