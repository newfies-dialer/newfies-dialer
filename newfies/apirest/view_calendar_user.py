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
from appointment.models.users import CalendarUser
from apirest.calendar_user_serializers import CalendarUserSerializer


class CalendarUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows calendar user to be viewed or edited.
    """
    queryset = CalendarUser.objects.filter(is_staff=False, is_superuser=False)
    serializer_class = CalendarUserSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticatedOrReadOnly, )
