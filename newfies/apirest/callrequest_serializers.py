# -*- coding: utf-8 -*-
#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from dialer_cdr.models import Callrequest


class CallrequestSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"request_uuid": "2342jtdsf-00123", "call_time": "2011-10-20 12:21:22", "phone_number": "8792749823", "content_type":"/rest-api/content_type/49/", "object_id":1, "timeout": "30000", "callerid": "650784355", "call_type": "1"}' http://localhost:8000/rest-api/callrequest/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/app/callrequest/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/callrequest/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/callrequest/%callreq_id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"content_type":"/rest-api/content_type/49/", "object_id":1, "status": "5"}' http://localhost:8000/rest-api/callrequest/%callrequest_id%/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    """
    user = serializers.Field(source='user')

    class Meta:
        model = Callrequest

    def get_fields(self, *args, **kwargs):
        """filter content_type field"""
        fields = super(CallrequestSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']

        if request.method != 'GET':
            fields['aleg_gateway'].queryset = request.user.get_profile().userprofile_gateway.all()
            if self.object and self.object:
                fields['content_type'].queryset = ContentType.objects.filter(model__in=["survey"])
            else:
                fields['content_type'].queryset = ContentType.objects.filter(model__in=["survey_template"])

        return fields
