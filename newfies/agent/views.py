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
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.template.context import RequestContext
from django.contrib.auth.forms import PasswordChangeForm

from agent.models import AgentProfile
from agent.forms import AgentChangeDetailExtendForm
from user_profile.forms import UserChangeDetailForm
from common.common_functions import current_view


@permission_required('agent.view_agent_dashboard', login_url='/')
@login_required
def agent_dashboard(request):
    """

    **Attributes**:

        * ``template`` - frontend/agent/dashboard.html
    """
    template = 'frontend/agent/dashboard.html'

    data = {
        'module': current_view(request),
    }

    return render_to_response(template, data,
        context_instance=RequestContext(request))


@login_required
def agent_detail_change(request):
    """User Detail change on Agent UI

    **Attributes**:

        * ``form`` - UserChangeDetailForm, AgentChangeDetailExtendForm,
                     PasswordChangeForm
        * ``template`` - 'frontend/registration/user_detail_change.html'

    **Logic Description**:

        * User is able to change his/her detail.
    """
    user_detail = get_object_or_404(User, username=request.user)
    user_detail_extened = AgentProfile.objects.get(user=user_detail)

    user_detail_form = UserChangeDetailForm(request.user,
                                            instance=user_detail)
    user_detail_extened_form = \
        AgentChangeDetailExtendForm(request.user,
                                    instance=user_detail_extened)
    user_password_form = PasswordChangeForm(user=request.user)

    msg_detail = ''
    msg_pass = ''

    error_detail = ''
    error_pass = ''
    action = ''
    if 'action' in request.GET:
        action = request.GET['action']

    if request.method == 'POST':
        if request.POST['form-type'] == "change-detail":
            user_detail_form = UserChangeDetailForm(
                request.user, request.POST, instance=user_detail)
            user_detail_extened_form = \
                AgentChangeDetailExtendForm(
                    request.user, request.POST, instance=user_detail_extened)
            action = 'tabs-1'
            if (user_detail_form.is_valid()
               and user_detail_extened_form.is_valid()):
                #DEMO / Disable
                if not settings.DEMO_MODE:
                    user_detail_form.save()
                    user_detail_extened_form.save()
                msg_detail = _('detail has been changed.')
            else:
                error_detail = _('please correct the errors below.')
        else:  # "change-password"
            user_password_form = PasswordChangeForm(user=request.user,
                                                    data=request.POST)
            action = 'tabs-2'
            if user_password_form.is_valid():
                #DEMO / Disable
                if not settings.DEMO_MODE:
                    user_password_form.save()
                msg_pass = _('your password has been changed.')
            else:
                error_pass = _('please correct the errors below.')

    template = 'frontend/registration/user_detail_change.html'
    data = {
        'module': current_view(request),
        'user_detail_form': user_detail_form,
        'user_detail_extened_form': user_detail_extened_form,
        'user_password_form': user_password_form,
        'msg_detail': msg_detail,
        'msg_pass': msg_pass,
        'error_detail': error_detail,
        'error_pass': error_pass,
        'action': action,
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))