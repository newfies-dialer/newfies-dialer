#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#


# Usage: py.test appointment/tests.py --ipdb
#

# from django.contrib.auth.models import User
# from django.conf import settings
# from django_lets_go.utils import BaseAuthenticatedClient
from user_profile.models import CalendarUser, CalendarUserProfile
from calendar_settings.models import CalendarSetting
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
from django.test.client import RequestFactory
import pytest
from django.contrib.auth.models import User
from django.test import TestCase, Client
from pytest import raises
from django.core.management import call_command
from newfies_factory.factories import UserFactory, SurveyTemplateFactory, SurveyFactory, \
    GatewayFactory, SMSGatewayFactory, CalendarSettingFactory, UserProfileFactory, CalendarUserProfileFactory, \
    ManagerFactory, CalendarUserFactory
from dialer_campaign.constants import AMD_BEHAVIOR
from django.core.urlresolvers import reverse


def test_an_exception():
    with raises(IndexError):
        # Indexing the 30th item in a 3 item list
        [5, 10, 15][30]


# class BaseAuthenticatedClient(TestCase):
#     """Common Authentication"""
#     fixtures = ['auth_user.json']

#     def setUp(self):
#         """To create admin user"""
#         self.client = Client()
#         self.user = User.objects.get(username='admin')
#         auth = '%s:%s' % ('admin', 'admin')
#         auth = 'Basic %s' % base64.encodestring(auth)
#         auth = auth.strip()
#         self.extra = {
#             'HTTP_AUTHORIZATION': auth,
#         }
#         login = self.client.login(username='admin', password='admin')
#         self.assertTrue(login)
#         self.factory = RequestFactory()

@pytest.fixture
def nf_user(transactional_db, client, admin_client, admin_user):
    user = UserFactory.create(first_name="Foo", username="myuser", password="password")
    user.save()
    # !!! doesn't work for some reason
    # login = client.login(user="myuser", password="password2")
    # assert login == True
    return user


@pytest.fixture
def nf_manager(transactional_db, client, admin_client, admin_user):
    manager = ManagerFactory.create(first_name="Foo", username="mymanager", password="password")
    manager.save()
    return manager


@pytest.fixture
def admin_user_profile(transactional_db, admin_client, admin_user):
    # Create user profile for Admin user
    prof = UserProfileFactory.create(user=admin_user)
    prof.save()
    return admin_user


@pytest.fixture
def appointment_fixtures(db, nf_user):
    survey_tmpl = SurveyTemplateFactory.create(user=nf_user)
    survey_tmpl.save()
    survey = SurveyFactory.create(user=nf_user)
    gateway = GatewayFactory.create()
    smsgateway = SMSGatewayFactory.create()
    calendarsetting = CalendarSettingFactory.create(user=nf_user)
    calendarsetting.save()
    result = {
        "client_user": nf_user,
        "survey_tmpl": survey_tmpl,
        "survey": survey,
        "gateway": gateway,
        "smsgateway": smsgateway,
        "calendarsetting": calendarsetting,
    }
    return result


def test_calendar_setting_view_list(admin_user, rf):
    # call_command('loaddata', 'user_profile/fixtures/auth_user.json')
    # url = reverse("thing_detail")
    request = rf.get(reverse('calendar_setting_list'))
    request.user = admin_user
    request.session = {}
    resp = calendar_setting_list(request)
    assert resp.status_code == 200


def test_calendar_setting_add_post(admin_client, client, admin_user, rf, appointment_fixtures, admin_user_profile):
    """Testing add calendarsetting"""
    survey = appointment_fixtures['survey']
    gateway = appointment_fixtures['gateway']

    data = {
        "label": "test calendar setting",
        "caller_name": "test",
        "callerid": "242534",
        # "sms_gateway": "1",
        "voicemail": "False",
        "call_timeout": "60",
        "survey": survey.id,
        "user": admin_user.id,
        "aleg_gateway": gateway.id,
        "amd_behavior": AMD_BEHAVIOR.ALWAYS}

    resp = client.post(reverse('calendar_setting_add'), data=data, follow=True)
    assert resp.status_code == 200
    request = rf.post(reverse('calendar_setting_add'), data, follow=True)
    request.user = admin_user
    request.session = {}
    resp = calendar_setting_add(request)
    # assert resp.status_code == 200


def test_calendar_setting_view_add(admin_client, client, nf_user, appointment_fixtures, admin_user_profile):
    """Test Function to check add calendar_setting"""
    client_user = appointment_fixtures['client_user']
    survey = appointment_fixtures['survey']
    gateway = appointment_fixtures['gateway']
    assert CalendarSetting.objects.count() == 1

    resp = admin_client.post(reverse('calendar_setting_add'), data={
        "callerid": "242534",
        "voicemail": "False",
        "call_timeout": "60",
        "voicemail_audiofile": "",
        "label": "test calendar setting",
        "caller_name": "test",
        "survey": survey.id,
        "user": client_user.id,
        "created_date": "2013-12-17T13:41:24.195",
        "aleg_gateway": gateway.id,
        "amd_behavior": ""}, follow=True)
    assert resp.status_code == 200
    # check that we have an extra CalendarSetting
    assert CalendarSetting.objects.count() == 2


def test_calendar_setting_view_update(admin_client, client, admin_user, rf, appointment_fixtures, admin_user_profile):
    """Test Function to check update calendar_setting"""
    survey = appointment_fixtures['survey']
    gateway = appointment_fixtures['gateway']
    list_calset = CalendarSetting.objects.all()
    assert len(list_calset) == 1
    resp = admin_client.post(reverse('calendar_setting_change', args=[list_calset[0].id]),
                             {"label": "newlabel", "caller_name": "newname", "survey": survey.id,
                              "aleg_gateway": gateway.id, "call_timeout": "60", }, follow=True)
    assert resp.status_code == 200
    calsetting = CalendarSetting.objects.get(pk=list_calset[0].id)
    assert calsetting.label == "newlabel"


def test_calendar_setting_view_del(admin_client, client, admin_user, rf, appointment_fixtures, admin_user_profile):
    # create new calendarsetting
    calendarsetting = CalendarSettingFactory.create(user=admin_user)
    calendarsetting.save()
    assert CalendarSetting.objects.count() == 2
    resp = admin_client.post(
        reverse('calendar_setting_del', args=[calendarsetting.id]), {'delete': True}, follow=True)
    assert resp.status_code == 200
    assert CalendarSetting.objects.count() == 1


def test_calendar_user_view_list(transactional_db, admin_client, client, admin_user, rf, appointment_fixtures,
                                 admin_user_profile, nf_manager):
    """Test Function to check calendar_user list"""
    # ManagerFactory.create(user=admin_user)
    # pytest.set_trace()
    # calendarsetting = CalendarSettingFactory.create(user=nf_manager)
    # calendarsetting.save()
    # cs_profile = CalendarUserProfileFactory.create(manager=nf_manager, calendar_setting=calendarsetting)

    resp = admin_client.get(reverse('calendar_user_list'))
    assert resp.status_code == 200


def test_calendar_user_view_add(transactional_db, admin_client, client, admin_user, rf, appointment_fixtures,
                                admin_user_profile, nf_manager):
    """Test Function to check add calendar_setting"""
    calendarsetting = CalendarSettingFactory.create(user=admin_user)
    calendarsetting.save()
    request = rf.get(reverse('calendar_user_add'))
    request.user = admin_user
    request.session = {}
    resp = calendar_user_add(request)
    assert resp.status_code == 200

    resp = admin_client.post(reverse('calendar_user_add'), data={
        "username": "caluser1",
        "password1": "password",
        "password2": "password",
        "calendar_setting_id": calendarsetting.id,
    }, follow=True)
    assert resp.status_code == 200

    request = rf.post(reverse('calendar_user_add'),
                      {
        "username": "caluser1",
        "password1": "password",
        "password2": "password",
        "calendar_setting_id": calendarsetting.id,
    }, follow=True)
    request.user = admin_user
    request.session = {}
    resp = calendar_user_add(request)
    assert resp.status_code == 200


# def test_calendar_user_view_update(transactional_db, admin_client, client, admin_user, rf, appointment_fixtures,
#                                 admin_user_profile, nf_manager):
#     """Test Function to check update calendar user"""

#     calendaruser = CalendarUserFactory.create(username="myusername", password="mypassword")
#     calendaruser.save()
#     login = client.login(user="myusername", password="mypassword")
#     assert login == True

#     # pytest.set_trace()
#     # calendarsetting = CalendarSettingFactory.create(user=nf_manager)
#     # calendarsetting.save()
#     # cs_profile = CalendarUserProfileFactory.create(manager=nf_manager, calendar_setting=calendarsetting)

#     calendarsetting = CalendarSettingFactory.create(user=admin_user)
#     calendarsetting.save()

#     request = rf.post(reverse('calendar_user_change', args=[4]), {
#         "caller_name": "test",
#         "survey": "1",
#     }, follow=True)
#     request.user = admin_user
#     request.session = {}
#     resp = calendar_user_change(request, 3)
#     assert resp.status_code == 200

#     resp = admin_client.post(reverse('calendar_user_change', args=[3]), {'delete': True}, follow=True)
#     assert resp.status_code == 200

# class AppointmentCustomerView(BaseAuthenticatedClient):
#     """Test cases for Appointment Customer Interface."""

#     fixtures = [
#         'auth_user.json', 'gateway.json', 'dialer_setting.json',
#         'user_profile.json', 'phonebook.json', 'contact.json',
#         'survey.json', 'dnc_list.json', 'dnc_contact.json',
#         'campaign.json', 'subscriber.json', 'example_gateways.json',
#         'calendar_setting.json', 'calendar_user_profile.json',
#         'calendar.json', 'event.json', 'alarm.json'
#     ]

# !!! DONE
#     def test_calendar_setting_view_list(self):
#         """Test Function to check calendar_setting list"""
#         resp = self.client.get(reverse('calendar_setting_list'))
#         self.assertEqual(resp.status_code, 200)
#         self.assertTemplateUsed(resp, 'appointment/calendar_setting/list.html')

#         request = self.factory.get(reverse('calendar_setting_list'))
#         request.user = self.user
#         request.session = {}
#         resp = calendar_setting_list(request)
#         self.assertEqual(resp.status_code, 200)

    # !!! DONE
    # def test_calendar_setting_view_add(self):
    #     """Test Function to check add calendar_setting"""
    #     request = self.factory.get(reverse('calendar_setting_add'))
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_setting_add(request)
    #     self.assertEqual(resp.status_code, 200)

    #     resp = self.client.post(reverse('calendar_setting_add'), data={
    #         "sms_gateway": "1",
    #         "callerid": "242534",
    #         "voicemail": "False",
    #         "call_timeout": "60",
    #         "voicemail_audiofile": "",
    #         "label": "test calendar setting",
    #         "caller_name": "test",
    #         "survey": "1",
    #         "user": "2",
    #         "created_date": "2013-12-17T13:41:24.195",
    #         "aleg_gateway": "1",
    #         "amd_behavior": ""}, follow=True)
    #     self.assertEqual(resp.status_code, 200)

    #     request = self.factory.post(reverse('calendar_setting_add'), {
    #         "sms_gateway": "1",
    #         "callerid": "242534",
    #         "voicemail": "False",
    #         "call_timeout": "60",
    #         "voicemail_audiofile": "",
    #         "label": "test calendar setting",
    #         "caller_name": "test",
    #         "survey": "1",
    #         "user": "2",
    #         "created_date": "2013-12-17T13:41:24.195",
    #         "aleg_gateway": "1",
    #         "amd_behavior": ""}, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_setting_add(request)
    #     self.assertEqual(resp.status_code, 302)

    # !!! DONE
    # def test_calendar_setting_view_update(self):
    #     """Test Function to check update calendar_setting"""
    #     request = self.factory.post('/module/calendar_setting/1/', {
    #         "caller_name": "test",
    #         "survey": "1",
    #     }, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_setting_change(request, 1)
    #     self.assertEqual(resp.status_code, 200)

    #     request = self.factory.post('/module/calendar_setting/1/', {'delete': True}, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_setting_change(request, 1)
    #     self.assertEqual(resp.status_code, 200)

    # !!! DONE
    # def test_calendar_setting_view_delete(self):
    #     """Test Function to check delete calendar_setting"""
    #     # delete calendar_setting
    #     request = self.factory.post('/module/calendar_setting/del/1/', follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_setting_del(request, 1)
    #     self.assertEqual(resp.status_code, 302)

    #     request = self.factory.post('/module/calendar_setting/del/', {'select': '1'})
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_setting_del(request, 0)
    #     self.assertEqual(resp.status_code, 302)

    # !!! DONE
    # def test_calendar_user_view_list(self):
    #     """Test Function to check calendar_user list"""
    #     resp = self.client.get('/module/calendar_user/')
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertTemplateUsed(resp, 'appointment/calendar_user/list.html')

    #     request = self.factory.get('/module/calendar_user/')
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_user_list(request)
    #     self.assertEqual(resp.status_code, 200)

    # !!! DONE
    # def test_calendar_user_view_add(self):
    #     """Test Function to check add calendar_setting"""
    #     request = self.factory.get(reverse('calendar_user_add'))
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_user_add(request)
    #     self.assertEqual(resp.status_code, 200)

    #     resp = self.client.post(reverse('calendar_user_add'), data=
    #         {
    #             "username": "caluser1",
    #             "password": "caluser1",
    #             "calendar_setting_id": 1,
    #         }, follow=True)
    #     self.assertEqual(resp.status_code, 200)

    #     request = self.factory.post(reverse('calendar_user_add'),
    #         {
    #             "username": "caluser1",
    #             "password": "caluser1",
    #             "calendar_setting_id": 1
    #         }, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_user_add(request)
    #     self.assertEqual(resp.status_code, 200)

    # !!! In progress
    # def test_calendar_user_view_update(self):
    #     """Test Function to check update calendar user"""
    #     request = self.factory.post('/module/calendar_user/4/', {
    #         "caller_name": "test",
    #         "survey": "1",
    #     }, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     #resp = calendar_user_change(request, 3)
    #     #self.assertEqual(resp.status_code, 200)

    #     request = self.factory.post('/module/calendar_user/3/', {'delete': True}, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     #resp = calendar_user_change(request, 3)
    #     #self.assertEqual(resp.status_code, 302)

    # def test_calendar_user_view_delete(self):
    #     """Test Function to check delete calendar user"""
    #     # delete calendar_setting
    #     request = self.factory.post('/module/calendar_user/del/4/', follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     #resp = calendar_user_del(request, 4)
    #     #self.assertEqual(resp.status_code, 302)

    #     request = self.factory.post('/module/calendar_user/del/', {'select': '1'})
    #     request.user = self.user
    #     request.session = {}
    #     #resp = calendar_user_del(request, 0)
    #     #self.assertEqual(resp.status_code, 302)

    # def test_calendar_view_list(self):
    #     """Test Function to check calendar list"""
    #     resp = self.client.get('/module/calendar/')
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertTemplateUsed(resp, 'appointment/calendar/list.html')

    #     request = self.factory.get('/module/calendar/')
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_list(request)
    #     self.assertEqual(resp.status_code, 200)

    # def test_calendar_view_add(self):
    #     """Test Function to check add calendar"""
    #     request = self.factory.get('/module/calendar/add/')
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_add(request)
    #     self.assertEqual(resp.status_code, 200)

    #     resp = self.client.post('/module/calendar/add/', data=
    #         {
    #             "name": "test calendar",
    #             "max_concurrent": 1,
    #         }, follow=True)
    #     self.assertEqual(resp.status_code, 200)

    #     request = self.factory.post('/module/calendar/add/',
    #         {
    #             "name": "test calendar",
    #             "max_concurrent": 1,
    #         }, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_add(request)
    #     self.assertEqual(resp.status_code, 302)

    # def test_calendar_view_update(self):
    #     """Test Function to check update calendar"""
    #     request = self.factory.post('/module/calendar/1/', {
    #         "caller_name": "test",
    #         "survey": "1",
    #     }, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_change(request, 1)
    #     self.assertEqual(resp.status_code, 200)

    #     request = self.factory.post('/module/calendar/1/', {'delete': True}, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_change(request, 1)
    #     self.assertEqual(resp.status_code, 200)

    # def test_calendar_view_delete(self):
    #     """Test Function to check delete calendar"""
    #     # delete calendar
    #     request = self.factory.post('/module/calendar/del/1/', follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_del(request, 1)
    #     self.assertEqual(resp.status_code, 302)

    #     request = self.factory.post('/module/calendar/del/', {'select': '1'})
    #     request.user = self.user
    #     request.session = {}
    #     resp = calendar_del(request, 0)
    #     self.assertEqual(resp.status_code, 302)

    # def test_event_view_list(self):
    #     """Test Function to check event list"""
    #     resp = self.client.get('/module/event/')
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertTemplateUsed(resp, 'appointment/event/list.html')

    #     request = self.factory.get('/module/calendar/')
    #     request.user = self.user
    #     request.session = {}
    #     resp = event_list(request)
    #     self.assertEqual(resp.status_code, 200)

    # def test_event_view_add(self):
    #     """Test Function to check add event"""
    #     request = self.factory.get('/module/event/add/')
    #     request.user = self.user
    #     request.session = {}
    #     resp = event_add(request)
    #     self.assertEqual(resp.status_code, 200)

    #     resp = self.client.post('/module/event/add/', data=
    #         {
    #             "title": "test event",
    #             "description": "",
    #             "creator_id": 1,
    #             "created_on": datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d"),
    #             "calendar_id": 1,
    #         }, follow=True)
    #     self.assertEqual(resp.status_code, 200)

    #     request = self.factory.post('/module/event/add/',
    #         {
    #             "title": "test event",
    #             "description": "",
    #             "creator_id": 1,
    #             "created_on": datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d"),
    #             "calendar_id": 1,
    #         }, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = event_add(request)
    #     self.assertEqual(resp.status_code, 200)

    # def test_event_view_update(self):
    #     """Test Function to check update event"""
    #     request = self.factory.post('/module/event/1/', {
    #         "title": "test event",
    #         "description": "",
    #     }, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = event_change(request, 1)
    #     self.assertEqual(resp.status_code, 200)

    #     request = self.factory.post('/module/event/1/', {'delete': True}, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = event_change(request, 1)
    #     self.assertEqual(resp.status_code, 200)

    # def test_event_view_delete(self):
    #     """Test Function to check delete event"""
    #     # delete event
    #     request = self.factory.post('/module/event/del/1/', follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = event_del(request, 1)
    #     self.assertEqual(resp.status_code, 302)

    #     request = self.factory.post('/module/event/del/', {'select': '1'})
    #     request.user = self.user
    #     request.session = {}
    #     resp = event_del(request, 0)
    #     self.assertEqual(resp.status_code, 302)

    # def test_alarm_view_list(self):
    #     """Test Function to check alarm list"""
    #     resp = self.client.get('/module/alarm/')
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertTemplateUsed(resp, 'appointment/alarm/list.html')

    #     request = self.factory.get('/module/alarm/')
    #     request.user = self.user
    #     request.session = {}
    #     resp = alarm_list(request)
    #     self.assertEqual(resp.status_code, 200)

    # def test_alarm_view_add(self):
    #     """Test Function to check add alarm"""
    #     request = self.factory.get('/module/alarm/add/')
    #     request.user = self.user
    #     request.session = {}
    #     resp = alarm_add(request)
    #     self.assertEqual(resp.status_code, 200)

    #     resp = self.client.post('/module/alarm/add/', data=
    #         {
    #             "alarm_phonenumber": "123456789",
    #             "alarm_email": "notify@xyz.com",
    #             "advance_notice": 1,
    #             "event_id": 1,
    #             "maxretry": 1,
    #         }, follow=True)
    #     self.assertEqual(resp.status_code, 200)

    #     request = self.factory.post('/module/alarm/add/',
    #         {
    #             "alarm_phonenumber": "123456789",
    #             "alarm_email": "notify@xyz.com",
    #             "advance_notice": 1,
    #             "event_id": 1,
    #             "maxretry": 1,
    #         }, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = alarm_add(request)
    #     self.assertEqual(resp.status_code, 200)

    # def test_alarm_view_update(self):
    #     """Test Function to check update alarm"""
    #     request = self.factory.post('/module/alarm/1/', {
    #         "title": "test event",
    #         "description": "",
    #     }, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = alarm_change(request, 1)
    #     self.assertEqual(resp.status_code, 200)

    #     request = self.factory.post('/module/alarm/1/', {'delete': True}, follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = alarm_change(request, 1)
    #     self.assertEqual(resp.status_code, 200)

    # def test_alarm_view_delete(self):
    #     """Test Function to check delete alarm"""
    #     # delete event
    #     request = self.factory.post('/module/alarm/del/1/', follow=True)
    #     request.user = self.user
    #     request.session = {}
    #     resp = alarm_del(request, 1)
    #     self.assertEqual(resp.status_code, 302)

    #     request = self.factory.post('/module/alarm/del/', {'select': '1'})
    #     request.user = self.user
    #     request.session = {}
    #     resp = alarm_del(request, 0)
    #     self.assertEqual(resp.status_code, 302)


# class AppointmentAdminView(BaseAuthenticatedClient):
#     """Test cases for Appointment Admin Interface."""

#     def test_admin_calendar_user_admin_list(self):
#         """Test Function to check admin calendaruser list"""
#         resp = self.client.get("/admin/auth/calendaruser/")
#         self.assertEqual(resp.status_code, 200)

#     def test_admin_calendar_user_admin_add(self):
#         """Test Function to check admin calendaruser add"""
#         resp = self.client.get("/admin/auth/calendaruser/")
#         self.assertEqual(resp.status_code, 200)

#     def test_admin_calendar_setting_admin_list(self):
#         """Test Function to check admin calendar setting list"""
#         resp = self.client.get("/admin/appointment/calendarsetting/")
#         self.assertEqual(resp.status_code, 200)

#     def test_admin_calendar_setting_admin_add(self):
#         """Test Function to check admin calendar setting add"""
#         resp = self.client.get("/admin/appointment/calendarsetting/add/")
#         self.assertEqual(resp.status_code, 200)

#     def test_admin_calendar_admin_list(self):
#         """Test Function to check admin calendar list"""
#         resp = self.client.get("/admin/appointment/calendar/")
#         self.assertEqual(resp.status_code, 200)

#     def test_admin_calendar_admin_add(self):
#         """Test Function to check admin calendar add"""
#         resp = self.client.get("/admin/appointment/calendar/add/")
#         self.assertEqual(resp.status_code, 200)

#     def test_admin_event_admin_list(self):
#         """Test Function to check admin event list"""
#         resp = self.client.get("/admin/appointment/event/")
#         self.assertEqual(resp.status_code, 200)

#     def test_admin_event_admin_add(self):
#         """Test Function to check admin event add"""
#         resp = self.client.get("/admin/appointment/event/add/")
#         self.assertEqual(resp.status_code, 200)

#     def test_admin_alarm_admin_list(self):
#         """Test Function to check admin alarm list"""
#         resp = self.client.get("/admin/appointment/alarm/")
#         self.assertEqual(resp.status_code, 200)

#     def test_admin_alarm_admin_add(self):
#         """Test Function to check admin alarm add"""
#         resp = self.client.get("/admin/appointment/alarm/add/")
#         self.assertEqual(resp.status_code, 200)
