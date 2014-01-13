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
from callcenter.models import Queue
from apirest.queue_serializers import QueueSerializer
from user_profile.models import Manager
from permissions import CustomObjectPermissions


class QueueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows queue to be viewed or edited.
    """
    model = Queue
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def get_queryset(self):
        """
        This view should return a list of all the phonebooks
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Queue.objects.all()
        else:
            queryset = Queue.objects.filter(manager=self.request.user)
        return queryset

    def pre_save(self, obj):
        obj.manager = Manager.objects.get(username=self.request.user)
