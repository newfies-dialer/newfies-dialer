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
from apirest.sms_template_serializers import SMSTemplateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from sms_module.models import SMSTemplate
from permissions import CustomObjectPermissions


class SMSTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows rule to be viewed or edited.
    """
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)
