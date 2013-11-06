# -*- coding: utf-8 -*-
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

from rest_framework import viewsets
from apirest.alarm_request_serializers import AlarmRequestSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from appointment.models.alarms import AlarmRequest


class AlarmRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows alarm request to be viewed or edited.
    """
    queryset = AlarmRequest.objects.all()
    serializer_class = AlarmRequestSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        """
        This view should return a list of all the alarms
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = AlarmRequest.objects.all()
        else:
            queryset = AlarmRequest.objects.filter(alarm__survey__user=self.request.user)
        return queryset
