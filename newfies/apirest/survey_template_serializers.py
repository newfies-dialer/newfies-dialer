# -*- coding: utf-8 -*-
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
from rest_framework import serializers
from survey.models import Survey_template


class SurveyTemplateSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "survey name"}' http://localhost:8000/rest-api/survey-template/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Location: http://localhost:8000/rest-api/survey-template/1/
            Allow: GET, POST, HEAD, OPTIONS

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/survey-template/

                or

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/survey-template/%survey-template-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/survey-template/1/",
                        "name": "Sample survey campaign",
                        "tts_language": "en",
                        "description": "ok",
                        "created_date": "2013-06-13T12:42:18.148",
                        "updated_date": "2013-06-13T12:42:31.527",
                        "user": "http://127.0.0.1:8000/rest-api/users/1/"
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"name": "sample survey"}' http://localhost:8000/rest-api/survey-template/%survey-template-id%/

        Response::

            HTTP/1.0 202 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    user = serializers.Field(source='user')

    class Meta:
        model = Survey_template
