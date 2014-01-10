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
from apirest.gateway_serializers import GatewaySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from dialer_gateway.models import Gateway
from user_profile.models import UserProfile
from permissions import CustomObjectPermissions


class GatewayViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows gateway to be viewed or edited.
    """
    queryset = Gateway.objects.all()
    serializer_class = GatewaySerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def get_queryset(self):
        """
        This view should return a list of all the alarms
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Gateway.objects.all()
        else:
            queryset = UserProfile.objects.get(user=self.request.user).userprofile_gateway.all()
        return queryset
