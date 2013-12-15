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

from rest_framework import serializers
from appointment.models.users import CalendarUser, CalendarUserProfile
from appointment.function_def import get_calendar_user_id_list
from agent.models import AgentProfile


class CalendarUserProfileSerializer(serializers.ModelSerializer):
    manager = serializers.Field(source='manager')

    class Meta:
        model = CalendarUserProfile

    def get_fields(self, *args, **kwargs):
        """filter  field"""
        fields = super(CalendarUserProfileSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']
        calendar_user_list = get_calendar_user_id_list(request.user)
        agent_id_list = AgentProfile.objects.values_list('user_id', flat=True).filter(manager=request.user)
        if not self.object:
            fields['user'].queryset = CalendarUser.objects\
                .filter(is_staff=False, is_superuser=False)\
                .exclude(id__in=calendar_user_list)\
                .exclude(id__in=agent_id_list).order_by('id')
        else:
            fields['user'].queryset = CalendarUser.objects.filter(pk=self.object.user_id)

        return fields
