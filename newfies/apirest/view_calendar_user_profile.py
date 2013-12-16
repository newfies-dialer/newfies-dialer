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
from appointment.models.users import CalendarUserProfile
from apirest.calendar_user_profile_serializers import CalendarUserProfileSerializer
from appointment.function_def import get_calendar_user_id_list, \
    get_all_calendar_user_id_list
from user_profile.models import Manager


class CalendarUserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows calendar user profile to be viewed or edited.
    """
    queryset = CalendarUserProfile.objects.all()
    serializer_class = CalendarUserProfileSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticatedOrReadOnly, )
    lookup_field = ('user_id')

    def pre_save(self, obj):
        obj.manager = Manager.objects.get(username=self.request.user)

    def list(self, request, *args, **kwargs):
        """get list of all CalendarUser objects"""
        if self.request.user.is_superuser:
            calendar_user_list = get_all_calendar_user_id_list()
        else:
            calendar_user_list = get_calendar_user_id_list(request.user)

        snippets = CalendarUserProfile.objects.filter(user_id__in=calendar_user_list).order_by('id')
        list_data = []

        for c_user_profile in snippets:
            user_url = 'http://%s/rest-api/calendar-user-profile/%s/' % (self.request.META['HTTP_HOST'], str(c_user_profile.id))
            calendar_setting_url = 'http://%s/rest-api/calendar-setting/%s/' % (self.request.META['HTTP_HOST'], str(c_user_profile.calendar_setting_id))

            data = {
                'url': user_url,
                'id': c_user_profile.id,
                'accountcode': c_user_profile.accountcode,
                'calendar_setting': calendar_setting_url,
                'manager': str(c_user_profile.manager),
                'address': c_user_profile.address,
                'city': c_user_profile.city,
                'state': c_user_profile.state,
                'zip_code': c_user_profile.zip_code,
                'phone_no': c_user_profile.phone_no,
                'fax': c_user_profile.fax,
                'company_name': c_user_profile.company_name,
                'company_website': c_user_profile.company_website,
                #'language': c_user_profile.language,
            }
            list_data.append(data)

        temp_data = ", ".join(str(e) for e in list_data)
        import ast
        final_data = ast.literal_eval(temp_data)
        #serializer = CalendarUserSerializer(snippets, many=True)
        return Response(final_data)
