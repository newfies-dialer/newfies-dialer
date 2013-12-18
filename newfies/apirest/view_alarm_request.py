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
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from apirest.alarm_request_serializers import AlarmRequestSerializer
from appointment.models.alarms import AlarmRequest
from appointment.models.events import Event
from appointment.function_def import get_calendar_user_id_list
import ast


class AlarmRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows alarm request to be viewed or edited.
    """
    queryset = AlarmRequest.objects.all()
    serializer_class = AlarmRequestSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        """
        This view should return a list of all the alarms
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = AlarmRequest.objects.all()
        else:
            calendar_user_list = get_calendar_user_id_list(self.request.user)
            queryset = AlarmRequest.objects.filter(
                alarm__event__creator_id__in=calendar_user_list)
        return queryset

    @action(methods=['GET'])
    def get_nested_alarm_request(self, request, pk=None):
        """it will get all nested alarm request"""
        #alarm_request = self.get_object()

        if self.request.user.is_superuser:
            try:
                event = Event.objects.get(pk=pk)
            except:
                final_data = {"error": "event id is not valid"}
                return Response(final_data)
        else:
            try:
                calendar_user_list = get_calendar_user_id_list(self.request.user)
                event = Event.objects.get(pk=pk, creator_id__in=calendar_user_list)
            except:
                final_data = {"error": "event id is not valid"}
                return Response(final_data)

        alarm_request_queryset = AlarmRequest.objects.filter(
            alarm__event__parent_event=event).order_by('-id')

        list_data = []
        for alarm_request in alarm_request_queryset:
            alarm_request_url = 'http://%s/rest-api/alarm-request/%s/' % (self.request.META['HTTP_HOST'], str(alarm_request.id))
            callrequest_url = 'http://%s/rest-api/callrequest/%s/' % (self.request.META['HTTP_HOST'], str(alarm_request.callrequest_id))
            alarm_url = 'http://%s/rest-api/alarm/%s/' % (self.request.META['HTTP_HOST'], str(alarm_request.alarm_id))
            event_url = 'http://%s/rest-api/event/%s/' % (self.request.META['HTTP_HOST'], str(alarm_request.alarm.event_id))

            data = {
                'url': alarm_request_url,
                'callrequest': callrequest_url,
                'alarm': {
                    'url': alarm_url,
                    'event': {
                        'url': event_url,
                    }
                }
            }
            list_data.append(data)

        if list_data:
            temp_data = ", ".join(str(e) for e in list_data)
            final_data = ast.literal_eval(temp_data)
        else:
            final_data = {"note": "no alarm request found"}
        return Response(final_data)
