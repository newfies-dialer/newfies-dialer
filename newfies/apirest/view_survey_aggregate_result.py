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

from django.db import connection
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response
from dialer_campaign.models import Campaign
from survey.models import ResultAggregate
import logging
logger = logging.getLogger('newfies.filelog')


class SurveyAggregateResultViewSet(APIView):
    """
    List survey aggregate result per campaign
    """
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticatedOrReadOnly, )

    def get(self, request, campaign_id=0, format=None):
        """GET method of survey aggregate result API"""
        error = {}
        survey_result_kwargs = {}

        cursor = connection.cursor()
        try:
            survey_result_kwargs['campaign'] =\
                Campaign.objects.get(id=campaign_id)
        except:
            error_msg = "Campaign ID does not exists!"
            error['error'] = error_msg
            logger.error(error_msg)
            return Response(error)

        survey_result = ResultAggregate.objects\
            .filter(**survey_result_kwargs)\
            .values('section__question', 'response', 'count')\
            .order_by('section')

        return Response(survey_result)
