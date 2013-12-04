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
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from appointment.models.users import CalendarUser
from appointment.models.calendars import Calendar

from apirest.calendar_user_serializers import CalendarUserSerializer


class CalendarUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows calendar user to be viewed or edited.
    """
    queryset = CalendarUser.objects.filter(is_staff=False, is_superuser=False)
    serializer_class = CalendarUserSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticatedOrReadOnly, )

    def list(self, request, *args, **kwargs):
        """get list of all CalendarUser objects"""
        snippets = CalendarUser.objects.all()
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
            data = {
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

        temp_data = ", ".join(str(e) for e in list_data)
        import ast
        final_data = ast.literal_eval(temp_data)
        #serializer = CalendarUserSerializer(snippets, many=True)
        return Response(final_data)

    def post_save(self, obj, created=False):
        """Create Calendar object with default name & current Calendar User"""
        Calendar.objects.create(
            name='default',
            user=obj,
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
