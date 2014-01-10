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
from survey.models import Section_template, Branching_template


class BranchingTemplateSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"keys": "20", "section": "/rest-api/section-template/1/", "goto": "/rest-api/section-template/2/"}' http://localhost:8000/rest-api/branching-template/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Location: http://localhost:8000/rest-api/survey/1/
            Allow: GET, POST, HEAD, OPTIONS

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/branching-template/

                or

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/branching-template/%branching-template-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/branching-template/1/",
                        "keys": "0",
                        "created_date": "2013-06-13T12:42:28.531",
                        "updated_date": "2013-06-13T12:42:28.531",
                        "section": "http://127.0.0.1:8000/rest-api/section-template/1/",
                        "goto": null
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"keys": "3", "survey": "/rest-api/section_template/1/"}' http://localhost:8000/rest-api/branching-template/%branching-template-id%/

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
        model = Branching_template
