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
from apirest.dnc_contact_serializers import DNCContactSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from dnc.models import DNCContact
from permissions import CustomObjectPermissions


class DNCContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows dnc contact to be viewed or edited.
    """
    model = DNCContact
    queryset = DNCContact.objects.all()
    serializer_class = DNCContactSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def get_queryset(self):
        """
        This view should return a list of all the DNC Contacts
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = DNCContact.objects.all()
        else:
            queryset = DNCContact.objects.filter(dnc__user=self.request.user)
        return queryset
