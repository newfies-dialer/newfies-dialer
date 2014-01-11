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

#from django.contrib.auth.models import User
#from django.conf import settings
from common.utils import BaseAuthenticatedClient
from appointment.models.users import CalendarSetting, CalendarUser, CalendarUserProfile
from appointment.models.calendars import Calendar
from appointment.models.events import Event
from appointment.models.alarms import Alarm
from appointment.views import calendar_setting_list, calendar_user_list, calendar_list,\
    event_list, alarm_list, calendar_setting_add, calendar_setting_change,\
    calendar_setting_del, calendar_user_add, calendar_user_change, calendar_user_del,\
    calendar_add, calendar_change, calendar_del, event_add, event_change, event_del,\
    alarm_add, alarm_change, alarm_del
from datetime import datetime
from django.utils.timezone import utc


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
        """Test Function to check admin alarm list"""
        response = self.client.get("/admin/appointment/alarm/")
        self.assertEqual(response.status_code, 200)

    def test_admin_alarm_admin_add(self):
        """Test Function to check admin alarm add"""
        response = self.client.get("/admin/appointment/alarm/add/")
        self.assertEqual(response.status_code, 200)


class AppointmentCustomerView(BaseAuthenticatedClient):
    """Test cases for Appointment Customer Interface."""

    fixtures = [
        'auth_user.json', 'gateway.json', 'dialer_setting.json',
        'user_profile.json', 'phonebook.json', 'contact.json',
        'survey.json', 'dnc_list.json', 'dnc_contact.json',
        'campaign.json', 'subscriber.json', 'example_gateways.json',
        'calendar_setting.json', 'calendar_user_profile.json',
        'calendar.json', 'event.json', 'alarm.json'
    ]

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

    def test_calendar_setting_view_add(self):
        """Test Function to check add calendar_setting"""
        request = self.factory.get('/module/calendar_setting/add/')
        request.user = self.user
        request.session = {}
        response = calendar_setting_add(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/module/calendar_setting/add/', data={
            "sms_gateway": "1",
            "callerid": "242534",
            "voicemail": "False",
            "call_timeout": "60",
            "voicemail_audiofile": "",
            "label": "test calendar setting",
            "caller_name": "test",
            "survey": "1",
            "user": "2",
            "created_date": "2013-12-17T13:41:24.195",
            "aleg_gateway": "1",
            "amd_behavior": ""}, follow=True)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/module/calendar_setting/add/', {
            "sms_gateway": "1",
            "callerid": "242534",
            "voicemail": "False",
            "call_timeout": "60",
            "voicemail_audiofile": "",
            "label": "test calendar setting",
            "caller_name": "test",
            "survey": "1",
            "user": "2",
            "created_date": "2013-12-17T13:41:24.195",
            "aleg_gateway": "1",
            "amd_behavior": ""}, follow=True)
        request.user = self.user
        request.session = {}
        response = calendar_setting_add(request)
        self.assertEqual(response.status_code, 302)

    def test_calendar_setting_view_update(self):
        """Test Function to check update calendar_setting"""
        request = self.factory.post('/module/calendar_setting/1/', {
            "caller_name": "test",
            "survey": "1",
        }, follow=True)
        request.user = self.user
        request.session = {}
        response = calendar_setting_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/module/calendar_setting/1/', {'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        response = calendar_setting_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_calendar_setting_view_delete(self):
        """Test Function to check delete calendar_setting"""
        # delete calendar_setting
        request = self.factory.post('/module/calendar_setting/del/1/', follow=True)
        request.user = self.user
        request.session = {}
        response = calendar_setting_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/module/calendar_setting/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = calendar_setting_del(request, 0)
        self.assertEqual(response.status_code, 302)

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

    def test_calendar_user_view_add(self):
        """Test Function to check add calendar_setting"""
        request = self.factory.get('/module/calendar_user/add/')
        request.user = self.user
        request.session = {}
        response = calendar_user_add(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/module/calendar_user/add/', data=
            {
                "username": "caluser1",
                "password": "caluser1",
                "calendar_setting_id": 1,
            }, follow=True)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/module/calendar_user/add/',
            {
                "username": "caluser1",
                "password": "caluser1",
                "calendar_setting_id": 1
            }, follow=True)
        request.user = self.user
        request.session = {}
        response = calendar_user_add(request)
        self.assertEqual(response.status_code, 200)

    def test_calendar_user_view_update(self):
        """Test Function to check update calendar user"""
        request = self.factory.post('/module/calendar_user/4/', {
            "caller_name": "test",
            "survey": "1",
        }, follow=True)
        request.user = self.user
        request.session = {}
        #response = calendar_user_change(request, 3)
        #self.assertEqual(response.status_code, 200)

        request = self.factory.post('/module/calendar_user/3/', {'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        #response = calendar_user_change(request, 3)
        #self.assertEqual(response.status_code, 302)

    def test_calendar_user_view_delete(self):
        """Test Function to check delete calendar user"""
        # delete calendar_setting
        request = self.factory.post('/module/calendar_user/del/4/', follow=True)
        request.user = self.user
        request.session = {}
        #response = calendar_user_del(request, 4)
        #self.assertEqual(response.status_code, 302)

        request = self.factory.post('/module/calendar_user/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        #response = calendar_user_del(request, 0)
        #self.assertEqual(response.status_code, 302)

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

    def test_calendar_view_add(self):
        """Test Function to check add calendar"""
        request = self.factory.get('/module/calendar/add/')
        request.user = self.user
        request.session = {}
        response = calendar_add(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/module/calendar/add/', data=
            {
                "name": "test calendar",
                "max_concurrent": 1,
            }, follow=True)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/module/calendar/add/',
            {
                "name": "test calendar",
                "max_concurrent": 1,
            }, follow=True)
        request.user = self.user
        request.session = {}
        response = calendar_add(request)
        self.assertEqual(response.status_code, 302)

    def test_calendar_view_update(self):
        """Test Function to check update calendar"""
        request = self.factory.post('/module/calendar/1/', {
            "caller_name": "test",
            "survey": "1",
        }, follow=True)
        request.user = self.user
        request.session = {}
        response = calendar_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/module/calendar/1/', {'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        response = calendar_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_calendar_view_delete(self):
        """Test Function to check delete calendar"""
        # delete calendar
        request = self.factory.post('/module/calendar/del/1/', follow=True)
        request.user = self.user
        request.session = {}
        response = calendar_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/module/calendar/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = calendar_del(request, 0)
        self.assertEqual(response.status_code, 302)

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

    def test_event_view_add(self):
        """Test Function to check add event"""
        request = self.factory.get('/module/event/add/')
        request.user = self.user
        request.session = {}
        response = event_add(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/module/event/add/', data=
            {
                "title": "test event",
                "description": "",
                "creator_id": 1,
                "created_on": datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d"),
                "calendar_id": 1,
            }, follow=True)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/module/event/add/',
            {
                "title": "test event",
                "description": "",
                "creator_id": 1,
                "created_on": datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d"),
                "calendar_id": 1,
            }, follow=True)
        request.user = self.user
        request.session = {}
        response = event_add(request)
        self.assertEqual(response.status_code, 200)

    def test_event_view_update(self):
        """Test Function to check update event"""
        request = self.factory.post('/module/event/1/', {
            "title": "test event",
            "description": "",
        }, follow=True)
        request.user = self.user
        request.session = {}
        response = event_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/module/event/1/', {'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        response = event_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_event_view_delete(self):
        """Test Function to check delete event"""
        # delete event
        request = self.factory.post('/module/event/del/1/', follow=True)
        request.user = self.user
        request.session = {}
        response = event_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/module/event/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = event_del(request, 0)
        self.assertEqual(response.status_code, 302)

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

    def test_alarm_view_add(self):
        """Test Function to check add alarm"""
        request = self.factory.get('/module/alarm/add/')
        request.user = self.user
        request.session = {}
        response = alarm_add(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/module/alarm/add/', data=
            {
                "alarm_phonenumber": "123456789",
                "alarm_email": "notify@xyz.com",
                "advance_notice": 1,
                "event_id": 1,
                "maxretry": 1,
            }, follow=True)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/module/alarm/add/',
            {
                "alarm_phonenumber": "123456789",
                "alarm_email": "notify@xyz.com",
                "advance_notice": 1,
                "event_id": 1,
                "maxretry": 1,
            }, follow=True)
        request.user = self.user
        request.session = {}
        response = alarm_add(request)
        self.assertEqual(response.status_code, 200)

    def test_alarm_view_update(self):
        """Test Function to check update alarm"""
        request = self.factory.post('/module/alarm/1/', {
            "title": "test event",
            "description": "",
        }, follow=True)
        request.user = self.user
        request.session = {}
        response = alarm_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/module/alarm/1/', {'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        response = alarm_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_alarm_view_delete(self):
        """Test Function to check delete alarm"""
        # delete event
        request = self.factory.post('/module/alarm/del/1/', follow=True)
        request.user = self.user
        request.session = {}
        response = alarm_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/module/alarm/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = alarm_del(request, 0)
        self.assertEqual(response.status_code, 302)
