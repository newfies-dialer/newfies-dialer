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
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from appointment.models.users import CalendarUser, CalendarUserProfile,\
    CalendarSetting
from appointment.models.calendars import Calendar
from appointment.function_def import get_calendar_user_id_list, \
    get_all_calendar_user_id_list
from apirest.calendar_user_serializers import CalendarUserSerializer
from user_profile.models import Manager
from permissions import CustomObjectPermissions
import ast


class CalendarUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows calendar user to be viewed or edited.
    """
    model = CalendarUser
    queryset = CalendarUser.objects.filter(is_staff=False, is_superuser=False)
    serializer_class = CalendarUserSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def list(self, request, *args, **kwargs):
        """get list of all CalendarUser objects"""
        if self.request.user.is_superuser:
            calendar_user_list = get_all_calendar_user_id_list()
        else:
            calendar_user_list = get_calendar_user_id_list(request.user)

        snippets = CalendarUser.objects.filter(id__in=calendar_user_list).order_by('id')
        list_data = []

        for c_user in snippets:
            try:
                calendar_obj = Calendar.objects.get(user=c_user)
                calendar_dict = {
                    'name': calendar_obj.name,
                    'max_concurrent': calendar_obj.max_concurrent,
                }
            except:
                calendar_dict = {}

            user_url = 'http://%s/rest-api/calendar-user/%s/' % (self.request.META['HTTP_HOST'], str(c_user.id))
            data = {
                'url': user_url,
                'id': c_user.id,
                'username': c_user.username,
                'password': c_user.password,
                'last_name': c_user.last_name,
                'first_name': c_user.first_name,
                'email': c_user.email,
                #'groups': c_user.groups,
                'calendar': calendar_dict,
            }
            list_data.append(data)

        if list_data:
            temp_data = ", ".join(str(e) for e in list_data)
            final_data = ast.literal_eval(temp_data)
        else:
            final_data = {"note": "no calendar-user found"}
        #serializer = CalendarUserSerializer(snippets, many=True)
        return Response(final_data)

    def post_save(self, obj, created=False):
        """Create Calendar User object with default name & current Calendar User"""

        if created:
            obj.set_password(self.request.DATA['password'])
            obj.save()

            CalendarUserProfile.objects.create(
                user=obj,
                manager=Manager.objects.get(username=self.request.user),
                calendar_setting=CalendarSetting.objects.filter(user=self.request.user)[0]
            )

    def retrieve(self, request, *args, **kwargs):
        """retrieve CalendarUser object"""
        self.object = self.get_object()
        data = dict()
        try:
            calendar_obj = Calendar.objects.get(user=self.object)
            calendar_dict = {
                'name': calendar_obj.name,
                'max_concurrent': calendar_obj.max_concurrent,
            }
        except:
            calendar_dict = {}

        data = {
            'id': self.object.id,
            'username': self.object.username,
            'password': self.object.password,
            'last_name': self.object.last_name,
            'first_name': self.object.first_name,
            'email': self.object.email,
            #'groups': c_user.groups,
            'calendar': calendar_dict,
        }

        #serializer = self.get_serializer(self.object)
        return Response(data)
