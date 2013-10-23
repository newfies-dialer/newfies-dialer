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
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from callcenter.models import Queue
from apirest.queue_serializers import QueueSerializer
import logging
logger = logging.getLogger('newfies.filelog')


class QueueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows queue to be viewed or edited.
    """
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticatedOrReadOnly, )

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
        obj.manager = self.request.user
