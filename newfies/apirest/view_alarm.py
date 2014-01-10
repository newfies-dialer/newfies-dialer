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
from apirest.alarm_serializers import AlarmSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from appointment.models.alarms import Alarm
from appointment.function_def import get_calendar_user_id_list
from permissions import CustomObjectPermissions


class AlarmViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows alarm to be viewed or edited.
    """
    model = Alarm
    queryset = Alarm.objects.all()
    serializer_class = AlarmSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def get_queryset(self):
        """
        This view should return a list of all the alarms
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Alarm.objects.all()
        else:
            calendar_user_list = get_calendar_user_id_list(self.request.user)
            queryset = Alarm.objects.filter(event__creator_id__in=calendar_user_list)
        return queryset
