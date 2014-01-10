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
from appointment.models.users import CalendarUserProfile, CalendarUser
from appointment.models.calendars import Calendar
from user_profile.models import Manager


def get_all_calendar_user_id_list():
    """get calendar user id list for logged in user"""
    calendar_user_list = CalendarUserProfile.objects.values_list(
        'user_id', flat=True).all().order_by('id')
    return calendar_user_list


def get_calendar_user_id_list(user):
    """get calendar user id list for logged in user"""
    calendar_user_list = CalendarUserProfile.objects.values_list(
        'user_id', flat=True).filter(manager=user).order_by('id')
    return calendar_user_list


def get_calendar_user_list(calendar_user_list):
    """get calendar user list from calendar_user_list"""

    list_calendar_user = []
    list_calendar_user.append((0, '---'))
    calendar_user_list = CalendarUser.objects.values_list(
        'id', 'username').filter(id__in=calendar_user_list).order_by('id')
    for l in calendar_user_list:
        list_calendar_user.append((l[0], l[1]))

    return list_calendar_user


def get_calendar_list(calendar_user_list):
    """get calendar list from calendar_user_list"""

    list_calendar = []
    list_calendar.append((0, '---'))
    calendar_list = Calendar.objects.values_list(
        'id', 'name').filter(user_id__in=calendar_user_list).order_by('id')
    for l in calendar_list:
        list_calendar.append((l[0], l[1]))

    return list_calendar


def manager_list_of_calendar_user():
    """Return all managers of the system"""
    manager_list = []
    calendar_user_id_list = get_all_calendar_user_id_list()
    obj_list = Manager.objects.values_list('id', 'username')\
        .filter(is_staff=False, is_superuser=False)\
        .exclude(id__in=calendar_user_id_list).order_by('id')
    for l in obj_list:
        manager_list.append((l[0], l[1]))
    return manager_list
