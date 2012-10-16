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
from apiplayground import APIPlayground


class SurveyAPIPlayground(APIPlayground):

    schema = {
        "title": "Survey API Playground",
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/survey/",
                "description": "This resource allows you to manage survey.",
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/survey/",
                        "description": "Returns all surveys"
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/survey/{survey-id}/",
                        "description": "Returns a specific survey"
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/survey/",
                        "description": "Creates new survey",
                        "parameters": [{
                                           "name": "name",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "Sample Campaign"
                                       },
                                       {
                                           "name": "description",
                                           "type": "string"
                                       },
                                       ]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/survey/{survey-id}/",
                        "description": "Update survey",
                        "parameters": [{
                                           "name": "name",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "Sample Campaign"
                                       },
                                       {
                                           "name": "description",
                                           "type": "string"
                                       },
                                       ]
                    },
                    {
                        "method": "DELETE",
                        "url": "/api/v1/survey/{survey-id}/",
                        "description": "Delete survey",
                    }
                ]
            },
            ]
    }
