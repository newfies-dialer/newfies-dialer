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
from dialer_campaign.models import Subscriber


class SubscriberListSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/subscriber-list/

        Response::

            [
                {
                    "id": 1,
                    "contact": "/rest-api/contact/11/",
                    "campaign": "/rest-api/campaigns/3/",
                    "last_attempt": null,
                    "count_attempt": 0,
                    "completion_count_attempt": 0,
                    "duplicate_contact": "34235464",
                    "status": 1
                },
                {
                    "id": 2,
                    "contact": "/rest-api/contact/12/",
                    "campaign": "/rest-api/campaigns/3/",
                    "last_attempt": null,
                    "count_attempt": 0,
                    "completion_count_attempt": 0,
                    "duplicate_contact": "34235464",
                    "status": 1
                }
            ]
    """
    class Meta:
        model = Subscriber
        fields = (
            'url', 'contact', 'campaign', 'last_attempt', 'count_attempt',
            'completion_count_attempt', 'status', 'created_date', 'updated_date',
        )
