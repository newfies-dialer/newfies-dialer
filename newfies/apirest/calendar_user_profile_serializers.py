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
from rest_framework import serializers
from appointment.models.users import CalendarUser, CalendarUserProfile
# from appointment.function_def import get_calendar_user_id_list
from agent.models import AgentProfile


class CalendarUserProfileSerializer(serializers.ModelSerializer):
    """
    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/calendar-user-profile/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/calendar-user-profile/%calendar-user-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "manager": "manager",
                        "id": 1,
                        "user": 3,
                        "address": null,
                        "city": null,
                        "state": null,
                        "country": "",
                        "zip_code": null,
                        "phone_no": null,
                        "fax": null,
                        "company_name": null,
                        "company_website": null,
                        "language": null,
                        "note": null,
                        "accountcode": null,
                        "created_date": "2013-12-16T06:26:06.153Z",
                        "updated_date": "2013-12-16T06:26:06.153Z",
                        "calendar_setting": 1
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"accountcode": "353652", "calendar_setting": "1"}' http://localhost:8000/rest-api/calendar-user-profile/%calendar-user-id%/

        Response::

            HTTP/1.0 200 OK
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    manager = serializers.Field(source='manager')

    class Meta:
        model = CalendarUserProfile

    def get_fields(self, *args, **kwargs):
        """filter  field"""
        fields = super(CalendarUserProfileSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']
        agent_id_list = AgentProfile.objects.values_list('user_id', flat=True).filter(manager=request.user)
        fields['user'].queryset = CalendarUser.objects\
            .filter(is_staff=False, is_superuser=False)\
            .exclude(id__in=agent_id_list).order_by('id')
        """
        calendar_user_list = get_calendar_user_id_list(request.user)

        if not self.object:
            fields['user'].queryset = CalendarUser.objects\
                .filter(is_staff=False, is_superuser=False)\
                .exclude(id__in=calendar_user_list)\
                .exclude(id__in=agent_id_list).order_by('id')
        else:
            fields['user'].queryset = CalendarUser.objects.filter(pk=self.object.user_id)
        """

        return fields
