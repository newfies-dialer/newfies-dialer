# -*- coding: utf-8 -*-
#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#
from rest_framework import viewsets
# from rest_framework.response import Response
from apirest.campaign_serializers import CampaignSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from dialer_campaign.models import Campaign
from apirest.permissions import CustomObjectPermissions


class CampaignViewSet(viewsets.ModelViewSet):
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
