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
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404, render
from django.utils.translation import ugettext as _
from django.template.context import RequestContext
from django.contrib.auth.forms import PasswordChangeForm, \
    UserCreationForm, AdminPasswordChangeForm
from django.contrib.auth.models import Permission
from django.views.decorators.csrf import csrf_exempt
from agent.models import AgentProfile, Agent
from appointment.constants import CALENDAR_USER_COLUMN_NAME
from agent.forms import AgentChangeDetailExtendForm, AgentDetailExtendForm, \
    AgentNameChangeForm
from appointment.models.users import CalendarUserProfile, CalendarUser
from user_profile.forms import UserChangeDetailForm
from dialer_campaign.function_def import user_dialer_setting_msg
from common.common_functions import get_pagination_vars
import json


@permission_required('appointment.view_calendar_user', login_url='/')
@login_required
def calendar_user_list(request):
    """CalendarUser list for the logged in Manager

    **Attributes**:

        * ``template`` - frontend/appointment/calendar_user/list.html

    **Logic Description**:

        * List all calendar_user which belong to the logged in manager.
    """
    sort_col_field_list = ['user', 'status', 'contact', 'updated_date']
    default_sort_field = 'id'
    pagination_data = \
        get_pagination_vars(request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']

    calendar_user_list = CalendarUserProfile.objects\
        .filter(manager=request.user).order_by(sort_order)

    template = 'frontend/appointment/calendar_user/list.html'
    data = {
        'msg': request.session.get('msg'),
        'calendar_user_list': calendar_user_list,
        'total_calendar_user': calendar_user_list.count(),
        'PAGE_SIZE': PAGE_SIZE,
        'CALENDAR_USER_COLUMN_NAME': CALENDAR_USER_COLUMN_NAME,
        'col_name_with_order': pagination_data['col_name_with_order'],
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))

