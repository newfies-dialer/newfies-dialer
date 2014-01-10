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
from apirest.sms_campaign_serializers import SMSCampaignSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from sms_module.models import SMSCampaign
from permissions import CustomObjectPermissions


class SMSCampaignViewSet(viewsets.ModelViewSet):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "mysmscampaign", "description": "", "callerid": "1239876", "startingdate": "2013-06-13 13:13:33", "expirationdate": "2013-06-14 13:13:33", "frequency": "20", "callmaxduration": "50", "maxretry": "3", "phonebook_id": "1"}' http://localhost:8000/rest-api/sms-campaign/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Allow: GET, POST, HEAD, OPTIONS

    """
    model = SMSCampaign
    queryset = SMSCampaign.objects.all()
    serializer_class = SMSCampaignSerializer
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
            queryset = SMSCampaign.objects.all()
        else:
            queryset = SMSCampaign.objects.filter(user=self.request.user)
        return queryset
