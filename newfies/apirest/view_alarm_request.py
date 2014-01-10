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
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from apirest.alarm_request_serializers import AlarmRequestSerializer
from appointment.models.alarms import Alarm, AlarmRequest
from appointment.models.events import Event
from appointment.function_def import get_calendar_user_id_list
from permissions import CustomObjectPermissions


class AlarmRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows alarm request to be viewed or edited.
    """
    model = AlarmRequest
    queryset = AlarmRequest.objects.all()
    serializer_class = AlarmRequestSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

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

        event_url = 'http://%s/rest-api/event/%s/' % (self.request.META['HTTP_HOST'], str(event.id))
        final_data = {}
        final_data["event-url"] = event_url
        final_data["event-%s" % str(event.id)] = {}
        alarm_list = Alarm.objects.filter(event__parent_event=event).order_by('id')
        for alarm in alarm_list:
            alarm_url = 'http://%s/rest-api/alarm/%s/' % (self.request.META['HTTP_HOST'], str(alarm.id))
            final_data["event-%s" % str(event.id)]["alarm-%s" % str(alarm.id)] = {
                'url': alarm_url
            }

            alarm_requests = AlarmRequest.objects.filter(alarm=alarm).order_by('id')
            for alarm_request in alarm_requests:
                alarm_request_url = 'http://%s/rest-api/alarm-request/%s/' % (self.request.META['HTTP_HOST'], str(alarm_request.id))
                callrequest_url = 'http://%s/rest-api/callrequest/%s/' % (self.request.META['HTTP_HOST'], str(alarm_request.callrequest_id))
                final_data["event-%s" % str(event.id)]["alarm-%s" % str(alarm.id)]['alarm-request-%s' % str(alarm_request.id)] = {
                    "url": alarm_request_url,
                    "alarm-callrequest": callrequest_url,
                    "date": str(alarm_request.date),
                    "status": str(alarm_request.status),
                    "callstatus": str(alarm_request.callstatus),
                    "duration": str(alarm_request.duration),
                }

        return Response(final_data)
