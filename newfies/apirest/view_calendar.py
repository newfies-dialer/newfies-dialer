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
from apirest.calendar_serializers import CalendarSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from appointment.models.calendars import Calendar
from appointment.models.users import CalendarUser


class CalendarViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows phonebook to be viewed or edited.
    """
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        """
        This view should return a list of all the phonebooks
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Calendar.objects.all()
        else:
            queryset = Calendar.objects.filter(
                user=CalendarUser.objects.get(username=self.request.user))
        return queryset

    def pre_save(self, obj):
        obj.user = CalendarUser.objects.get(username=self.request.user)
