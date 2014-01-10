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
from rest_framework import viewsets
#from rest_framework.response import Response
from apirest.campaign_serializers import CampaignSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from dialer_campaign.models import Campaign
from permissions import CustomObjectPermissions


class CampaignViewSet(viewsets.ModelViewSet):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "mycampaign", "description": "", "callerid": "1239876", "startingdate": "2013-06-13 13:13:33", "expirationdate": "2013-06-14 13:13:33", "frequency": "20", "callmaxduration": "50", "maxretry": "3", "intervalretry": "3000", "calltimeout": "45", "aleg_gateway": "1", "content_type": "survey_template", "object_id" : "1", "extra_data": "2000", "phonebook_id": "1", "voicemail": "True", "amd_behavior": "1", "voicemail_audiofile": "1", "dnc": "", "phonebook": "1"}' http://localhost:8000/rest-api/campaigns/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Allow: GET, POST, HEAD, OPTIONS

            {"id": 1, "campaign_code": "JDQBG", "name": "mycampaign1", "description": "", "callerid": "1239876", "phonebook": ["/rest-api/phonebook/1/", "/rest-api/phonebook/2/"], "startingdate": "2013-06-13T13:13:33", "expirationdate": "2013-06-14T13:13:33", "aleg_gateway": "http://localhost:8000/rest-api/gateway/1/", "user": "http://localhost:8000/rest-api/users/1/", "status": 2, "content_type": "http://localhost:8000/rest-api/content_type/49/", "object_id": 1, "extra_data": "2000", "dnc": null, "frequency": 20, "callmaxduration": 50, "maxretry": 3, "intervalretry": 3000, "calltimeout": 45, "daily_start_time": "00:00:00", "daily_stop_time": "23:59:59", "monday": true, "tuesday": true, "wednesday": true, "thursday": true, "friday": true, "saturday": true, "sunday": true, "completion_maxretry": 0, "completion_intervalretry": 900}

    """
    model = Campaign
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def pre_save(self, obj):
        obj.user = self.request.user

    def get_queryset(self):
        """
        This view should return a list of all the campaigns
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Campaign.objects.all()
        else:
            queryset = Campaign.objects.filter(user=self.request.user)
        return queryset
