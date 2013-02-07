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


class SectionAPIPlayground(APIPlayground):

    schema = {
        "title": _("Section API Playground"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/section/",
                "description": _("This resource allows you to manage sections."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/section/",
                        "description": _("Returns all sections")
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/section/{section-id}/",
                        "description": _("Returns a specific section")
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/section/",
                        "description": _("Creates new section"),
                        "parameters": [{
                                           "name": "type",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "question",
                                           "type": "string",
                                           "default": "this is test question"
                                       },
                                       {
                                           "name": "script",
                                           "type": "string",
                                           "default": "this is test question"
                                       },
                                       {
                                           "name": "survey",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       ]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/section/{section-id}/",
                        "description": _("Update section"),
                        "parameters": [{
                                           "name": "type",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "question",
                                           "type": "string",
                                           "default": "this is test question"
                                       },
                                       {
                                           "name": "script",
                                           "type": "string",
                                           "default": "this is test question"
                                       },
                                       {
                                           "name": "survey",
                                           "type": "string",
                                           "default": "1"
                                       },
                                       ]
                    },
                    {
                        "method": "DELETE",
                        "url": "/api/v1/section/{section-id}/",
                        "description": _("Delete section"),
                        }
                ]
            },
            ]
    }
