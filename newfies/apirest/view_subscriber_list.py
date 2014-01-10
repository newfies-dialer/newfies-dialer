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
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from apirest.subscriber_list_serializers import SubscriberListSerializer
from dialer_campaign.models import Subscriber
from permissions import CustomObjectPermissions


class SubscriberListViewSet(viewsets.ReadOnlyModelViewSet):
    """SubscriberListViewSet"""
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberListSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def get_queryset(self):
        """
        This view should return a list of all the Subscriber
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Subscriber.objects.all()
        else:
            queryset = Subscriber.objects.filter(campaign__user=self.request.user)
        return queryset
