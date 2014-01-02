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
from appointment.views import calendar_setting_list, calendar_user_list, calendar_list,\
    event_list, alarm_list


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

    def test_admin_calendar_setting_admin_list(self):
        """Test Function to check admin calendar setting list"""
        response = self.client.get("/admin/appointment/calendarsetting/")
        self.assertEqual(response.status_code, 200)

    def test_admin_calendar_setting_admin_add(self):
        """Test Function to check admin calendar setting add"""
        response = self.client.get("/admin/appointment/calendarsetting/add/")
        self.assertEqual(response.status_code, 200)

    def test_admin_calendar_admin_list(self):
        """Test Function to check admin calendar list"""
        response = self.client.get("/admin/appointment/calendar/")
        self.assertEqual(response.status_code, 200)

    def test_admin_calendar_admin_add(self):
        """Test Function to check admin calendar add"""
        response = self.client.get("/admin/appointment/calendar/add/")
        self.assertEqual(response.status_code, 200)

    def test_admin_event_admin_list(self):
        """Test Function to check admin event list"""
        response = self.client.get("/admin/appointment/event/")
        self.assertEqual(response.status_code, 200)

    def test_admin_event_admin_add(self):
        """Test Function to check admin event add"""
        response = self.client.get("/admin/appointment/event/add/")
        self.assertEqual(response.status_code, 200)

    def test_admin_alarm_admin_list(self):
        """Test Function to check admin event list"""
        response = self.client.get("/admin/appointment/calendar/")
        self.assertEqual(response.status_code, 200)

    def test_admin_alarm_admin_add(self):
        """Test Function to check admin alarm add"""
        response = self.client.get("/admin/appointment/alarm/add/")
        self.assertEqual(response.status_code, 200)


class AppointmentCustomerView(BaseAuthenticatedClient):
    """Test cases for Appointment Customer Interface."""

    #fixtures = ['auth_user.json']

    def test_calendar_setting_view_list(self):
        """Test Function to check calendar_setting list"""
        response = self.client.get('/module/calendar_setting/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/appointment/calendar_setting/list.html')

        request = self.factory.get('/module/calendar_setting/')
        request.user = self.user
        request.session = {}
        response = calendar_setting_list(request)
        self.assertEqual(response.status_code, 200)

    def test_calendar_user_view_list(self):
        """Test Function to check calendar_user list"""
        response = self.client.get('/module/calendar_user/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/appointment/calendar_user/list.html')

        request = self.factory.get('/module/calendar_user/')
        request.user = self.user
        request.session = {}
        response = calendar_user_list(request)
        self.assertEqual(response.status_code, 200)

    def test_calendar_view_list(self):
        """Test Function to check calendar list"""
        response = self.client.get('/module/calendar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/appointment/calendar/list.html')

        request = self.factory.get('/module/calendar/')
        request.user = self.user
        request.session = {}
        response = calendar_list(request)
        self.assertEqual(response.status_code, 200)

    def test_event_view_list(self):
        """Test Function to check event list"""
        response = self.client.get('/module/event/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/appointment/event/list.html')

        request = self.factory.get('/module/calendar/')
        request.user = self.user
        request.session = {}
        response = event_list(request)
        self.assertEqual(response.status_code, 200)

    def test_alarm_view_list(self):
        """Test Function to check alarm list"""
        response = self.client.get('/module/alarm/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/appointment/alarm/list.html')

        request = self.factory.get('/module/alarm/')
        request.user = self.user
        request.session = {}
        response = alarm_list(request)
        self.assertEqual(response.status_code, 200)
