# -*- coding: utf-8 -*-
#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.conf.urls import url
from django.http import HttpResponse

from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.throttle import BaseThrottle
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie import http

from dialer_campaign.models import Campaign
from survey2.models import ResultAggregate
import logging

logger = logging.getLogger('newfies.filelog')


class ResultAggregateResource(ModelResource):
    """
    **Attributes Details**:

        * ``section__question`` -
        * ``response`` -
        * ``count`` -

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/survey_aggregate_result/%campaign_id%/?format=json

        Response::

            [
               {
                  "section__question":u'What is your prefered fruit?',
                  "response":"apple",
                  "count": 1,
               },
               {
                  "section__question":u'What is your prefered fruit?',
                  "response":"orange",
                  "count": 3,
               }
            ]

    """
    class Meta:
        resource_name = 'survey_aggregate_result'
        authorization = Authorization()
        authentication = BasicAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        # default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)

    def override_urls(self):
        """Override urls"""
        return [
            url(r'^(?P<resource_name>%s)/(.+)/$' %\
                self._meta.resource_name, self.wrap_view('read')),
            ]

    def read_response(self, request, data,
                      response_class=HttpResponse, **response_kwargs):
        """To display API's result"""
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized,
            content_type=desired_format, **response_kwargs)

    def read(self, request=None, **kwargs):
        """GET method of Subscriber API"""
        logger.debug('Survey Aggregate Result GET API get called')
        auth_result = self._meta.authentication.is_authenticated(request)
        if not auth_result is True:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

        logger.debug('Survey Aggregate Result GET API authorization called!')
        auth_result = self._meta.authorization.is_authorized(request, object)

        temp_url = request.META['PATH_INFO']
        temp_id = temp_url.split('/api/v1/survey_aggregate_result/')[1]
        camp_id = temp_id.split('/')[0]

        try:
            campaign_id = int(camp_id)
        except:
            error_msg = "No value for Campaign ID !"
            logger.error(error_msg)
            raise BadRequest(error_msg)

        survey_result_kwargs = {}
        try:
            survey_result_kwargs['campaign'] =\
                Campaign.objects.get(id=campaign_id)
        except:
            error_msg = "Campaign ID does not exists!"
            logger.error(error_msg)
            raise BadRequest(error_msg)

        survey_result = ResultAggregate.objects\
            .filter(**survey_result_kwargs)\
            .values('section__question', 'response', 'count')\
            .order_by('section')

        logger.debug('Subscriber GET API : result ok 200')
        return self.read_response(request, survey_result)



