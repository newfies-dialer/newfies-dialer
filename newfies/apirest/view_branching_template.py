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
from apirest.branching_template_serializers import BranchingTemplateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from survey.models import Branching_template
from permissions import CustomObjectPermissions


class BranchingTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows content_type to be viewed or edited.
    """
    model = Branching_template
    queryset = Branching_template.objects.all()
    serializer_class = BranchingTemplateSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def get_queryset(self):
        """
        This view should return a list of all the branching
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Branching_template.objects.all()
        else:
            queryset = Branching_template.objects.filter(section__survey__user=self.request.user)
        return queryset
