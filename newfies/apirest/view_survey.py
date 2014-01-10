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
from apirest.survey_serializers import SurveySerializer
from survey.models import Survey
from permissions import CustomObjectPermissions


class SurveyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows survey to be viewed.
    """
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def get_queryset(self):
        """
        This view should return a list of all the survey
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Survey.objects.all()
        else:
            queryset = Survey.objects.filter(user=self.request.user)
        return queryset
