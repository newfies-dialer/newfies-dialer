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
from apirest.callrequest_serializers import CallrequestSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from dialer_cdr.models import Callrequest
from permissions import CustomObjectPermissions


class CallrequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows campaigns to be viewed or edited.
    """
    model = Callrequest
    queryset = Callrequest.objects.all()
    serializer_class = CallrequestSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def pre_save(self, obj):
        obj.user = self.request.user

    def get_queryset(self):
        """
        This view should return a list of all the callrequests
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Callrequest.objects.all()
        else:
            queryset = Callrequest.objects.filter(user=self.request.user)
        return queryset
