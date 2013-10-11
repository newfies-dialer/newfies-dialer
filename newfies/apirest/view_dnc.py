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
from apirest.dnc_serializers import DNCSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from dnc.models import DNC


class DNCViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows dnc list to be viewed or edited.
    """
    queryset = DNC.objects.all()
    serializer_class = DNCSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        """
        This view should return a list of all the DNCs
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = DNC.objects.all()
        else:
            queryset = DNC.objects.filter(user=self.request.user)
        return queryset

    def pre_save(self, obj):
        obj.user = self.request.user
