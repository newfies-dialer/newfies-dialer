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
from mod_mailer.models import MailTemplate


class MailTemplateSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/mail-template/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/mail-template/1/",
                        "label": "test_mail",
                        "template_key": "test_mail",
                        "from_email": "xyz@gmail.com",
                        "from_name": "xyz",
                        "subject": "hi",
                        "message_plaintext": "test message",
                        "message_html": "<h1>Hi</h1>",
                        "created_date": "2013-12-16T06:37:42.938Z"
                    }
                ]
            }
    """
    class Meta:
        model = MailTemplate
