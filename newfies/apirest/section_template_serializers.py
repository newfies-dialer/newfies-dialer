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
from survey.models import Section_template


class SectionTemplateSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"type": "1", "audiofile": "/rest-api/audio-files/1/", "question": "survey que", "survey": "/rest-api/survey-template/1/", "invalid_audiofile": "/rest-api/audio-files/1/", "queue": "/rest-api/queue/1/"}' http://localhost:8000/rest-api/section-template/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Location: http://localhost:8000/rest-api/section-template/1/
            Allow: GET, POST, HEAD, OPTIONS

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/section-template/

                or

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/section-template/%section-template-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/section-template/1/",
                        "order": 1,
                        "type": 1,
                        "question": "this is test question",
                        "script": "this is test question",
                        "audiofile": null,
                        "retries": null,
                        "timeout": 5,
                        "key_0": null,
                        "key_1": null,
                        "key_2": null,
                        "key_3": null,
                        "key_4": null,
                        "key_5": null,
                        "key_6": null,
                        "key_7": null,
                        "key_8": null,
                        "key_9": null,
                        "rating_laps": 9,
                        "validate_number": true,
                        "number_digits": 2,
                        "min_number": 0,
                        "max_number": 99,
                        "phonenumber": null,
                        "conference": null,
                        "completed": false,
                        "queue": null,
                        "created_date": "2013-06-13T12:42:28.457",
                        "updated_date": "2013-06-13T12:42:28.511",
                        "survey": "http://127.0.0.1:8000/rest-api/survey-template/1/",
                        "invalid_audiofile": null
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"type": "1", "question": "survey que", "survey": "/rest-api/survey-template/1/", "invalid_audiofile": "/rest-api/audio-files/1/"}' http://localhost:8000/rest-api/section-template/%section-template-id%/

        Response::

            HTTP/1.0 202 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """

    class Meta:
        model = Section_template
