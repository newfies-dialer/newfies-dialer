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


class CalendarUserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CalendarUserProfile

    def get_fields(self, *args, **kwargs):
        """filter  field"""
        fields = super(CalendarUserProfileSerializer, self).get_fields(*args, **kwargs)
        fields['user'].queryset = CalendarUser.objects.all()  # .filter(is_staff=False, is_superuser=False)
        return fields
