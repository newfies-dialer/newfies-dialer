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

from django.contrib.auth.models import User
#from django.conf import settings
from common.utils import BaseAuthenticatedClient
from appointment.models.users import CalendarSetting, CalendarUser, CalendarUserProfile
from appointment.models.calendars import Calendar
from appointment.models.events import Event
from appointment.models.alarms import Alarm
from appointment.views import calendar_setting_list


class AppointmentAdminView(BaseAuthenticatedClient):
    """Test cases for Appointment Admin Interface."""

    def test_admin_calendar_user_admin_list(self):
        """Test Function to check admin calendaruser list"""
        response = self.client.get("/admin/auth/calendaruser/")
        self.assertEqual(response.status_code, 200)

    def test_admin_calendar_user_admin_add(self):
        """Test Function to check admin calendaruser add"""
        response = self.client.get("/admin/auth/calendaruser/")
        self.assertEqual(response.status_code, 200)


class AppointmentCustomerView(BaseAuthenticatedClient):
    """Test cases for Appointment Customer Interface."""

    #fixtures = ['auth_user.json']

    def test_audiofile_view_list(self):
        """Test Function to check audio list"""
        response = self.client.get('/module/calendar_setting/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/appointment/calendar_setting/list.html')

        request = self.factory.get('/module/calendar_setting/')
        request.user = self.user
        request.session = {}
        response = calendar_setting_list(request)
        self.assertEqual(response.status_code, 200)
