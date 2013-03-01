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
from django.utils.translation import gettext as _
from apiplayground import APIPlayground


class SurveyAPIPlayground(APIPlayground):

    schema = {
        "title": _("survey"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/survey/",
                "description": _("this resource allows you to manage survey."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/survey/",
                        "description": _("returns all surveys")
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/survey/{survey-id}/",
                        "description": _("returns a specific survey")
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/survey/",
                        "description": _("create new survey"),
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
                        "description": _("update survey"),
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
                        "description": _("delete survey"),
                    }
                ]
            },
            ]
    }
