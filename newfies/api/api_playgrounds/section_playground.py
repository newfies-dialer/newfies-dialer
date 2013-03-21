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
        "title": _("section"),
        "base_url": "http://localhost/api/v1/",
        "resources": [
            {
                "name": "/section/",
                "description": _("this resource allows you to manage sections."),
                "endpoints": [
                    {
                        "method": "GET",
                        "url": "/api/v1/section/",
                        "description": _("returns all sections")
                    },
                    {
                        "method": "GET",
                        "url": "/api/v1/section/{section-id}/",
                        "description": _("returns a specific section")
                    },
                    {
                        "method": "POST",
                        "url": "/api/v1/section/",
                        "description": _("create new section"),
                        "parameters": [{
                                           "name": "type",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "question",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "this is test question"
                                       },
                                       {
                                           "name": "script",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "this is test question"
                                       },
                                       {
                                           "name": "survey",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "retries",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },

                                       {
                                           "name": "timeout",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_0",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_1",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_2",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_3",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_4",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_5",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_6",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_7",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_8",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_9",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "rating_laps",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "validate_number",
                                           "type": "string",
                                           "is_required": False,
                                           "default": "True"
                                       },
                                       {
                                           "name": "number_digits",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "min_number",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "max_number",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "phonenumber",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "conference",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       }
                                       ]
                    },
                    {
                        "method": "PUT",
                        "url": "/api/v1/section/{section-id}/",
                        "description": _("update section"),
                        "parameters": [{
                                           "name": "type",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "question",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "this is test question"
                                       },
                                       {
                                           "name": "script",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "this is test question"
                                       },
                                       {
                                           "name": "survey",
                                           "type": "string",
                                           "is_required": True,
                                           "default": "1"
                                       },
                                       {
                                           "name": "retries",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },

                                       {
                                           "name": "timeout",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_0",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_1",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_2",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_3",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_4",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_5",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_6",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_7",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_8",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "key_9",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "rating_laps",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "validate_number",
                                           "type": "string",
                                           "is_required": False,
                                           "default": "True"
                                       },
                                       {
                                           "name": "number_digits",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "min_number",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "max_number",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "phonenumber",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       },
                                       {
                                           "name": "conference",
                                           "type": "string",
                                           "is_required": False,
                                           "default": ""
                                       }
                                       ]
                    },
                    {
                        "method": "DELETE",
                        "url": "/api/v1/section/{section-id}/",
                        "description": _("delete section"),
                        }
                ]
            },
            ]
    }
