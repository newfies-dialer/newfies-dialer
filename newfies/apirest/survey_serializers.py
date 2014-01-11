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
from survey.models import Survey


class SurveySerializer(serializers.HyperlinkedModelSerializer):
    """
    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/sealed-survey/

                or

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/sealed-survey/%sealed_survey_id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/sealed-survey/1/",
                        "name": "Sample survey campaign",
                        "tts_language": "en",
                        "description": "ok",
                        "created_date": "2013-06-13T12:42:18.148",
                        "updated_date": "2013-06-13T12:42:31.527",
                        "user": "http://127.0.0.1:8000/rest-api/users/1/"
                    }
                ]
            }
    """

    class Meta:
        model = Survey
