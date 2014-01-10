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
from django.conf import settings
#from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.template.context import RequestContext
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Permission
#from django.views.decorators.csrf import csrf_exempt
from agent.models import AgentProfile, Agent
from agent.constants import AGENT_COLUMN_NAME
from agent.forms import AgentChangeDetailExtendForm, AgentDetailExtendForm, \
    AgentNameChangeForm, AgentCreationForm, AgentPasswordChangeForm
from user_profile.models import Manager
from user_profile.forms import UserChangeDetailForm
from dialer_campaign.function_def import user_dialer_setting_msg
from common.common_functions import get_pagination_vars
#import json

redirect_url_to_agent_list = '/module/agent/'


def agent_login_form(request):
    """agent login Page"""
    template = 'frontend/agent/login_form.html'
    data = {}
    return render_to_response(template, data,
        context_instance=RequestContext(request))


def agent_login(request):
    """agent login Page"""
    template = 'frontend/agent/login.html'
    data = {
        'action': 'tabs-1',
    }
    return render_to_response(template, data,
        context_instance=RequestContext(request))


def agent_logout(request):
    """agent login Page"""
    template = 'frontend/agent/logout.html'
    data = {
        'action': 'tabs-2',
    }
    return render_to_response(template, data,
        context_instance=RequestContext(request))


def auth(request):
    if 'HTTP_AUTHORIZATION' in request.META:
        uname, passwd = request.META['HTTP_AUTHORIZATION'].split(':')
        user = authenticate(username=uname, password=passwd)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.user = user

                # Once we have logged the user in return the serialized response
                # TODO: not defined api ?
                serializer = api.user.UserSerializer(request.user)
                # TODO: not defined JSONResponse ?
                return JSONResponse(serializer.data)

    # They did not provide basic authentication
    response = HttpResponse()
    response.status_code = 401
    return response


@permission_required('auth.view_agent_dashboard', login_url='/')
@login_required
def agent_dashboard(request):
    """

    **Attributes**:

        * ``template`` - frontend/agent/dashboard.html
    """
    template = 'frontend/agent/dashboard.html'

    data = {
    }

    return render_to_response(template, data,
        context_instance=RequestContext(request))


@login_required
def agent_change_password(request, object_id):
    """
    User Detail change on Agent UI

    **Attributes**:

        * ``form`` - AgentPasswordChangeForm
        * ``template`` - 'frontend/agent/change_password.html',
             'frontend/registration/user_detail_change.html'

    **Logic Description**:

        * Reset Agent password.
    """
    msg_pass = ''
    error_pass = ''

    agent_userdetail = get_object_or_404(Agent, pk=object_id)
    agent_username = agent_userdetail.username

    user_password_form = AgentPasswordChangeForm(user=agent_userdetail)

    if request.method == 'POST':
        user_password_form = AgentPasswordChangeForm(user=agent_userdetail,
                                                     data=request.POST)
        if user_password_form.is_valid():
            user_password_form.save()
            request.session["msg"] = _('%s password has been changed.' % agent_username)
            return HttpResponseRedirect(redirect_url_to_agent_list)
        else:
            error_pass = _('please correct the errors below.')

    template = 'frontend/agent/change_password.html'
    data = {
        'agent_username': agent_username,
        'user_password_form': user_password_form,
        'msg_pass': msg_pass,
        'error_pass': error_pass,
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@login_required
def agent_detail(request):
    user_detail = get_object_or_404(Agent, username=request.user)
    user_detail_extened = AgentProfile.objects.get(user=user_detail)

    user_detail_form = UserChangeDetailForm(request.user,
                                            instance=user_detail)
    user_detail_extened_form = \
        AgentDetailExtendForm(request.user,
                              instance=user_detail_extened)
    user_password_form = PasswordChangeForm(user=request.user)

    template = 'frontend/agent/agent_detail.html'
    data = {
        'user_detail_form': user_detail_form,
        'user_detail_extened_form': user_detail_extened_form,
        'user_password_form': user_password_form,
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def agent_detail_change(request):
    """User Detail change on Agent UI

    **Attributes**:

        * ``form`` - UserChangeDetailForm, AgentDetailExtendForm,
                     PasswordChangeForm
        * ``template`` - 'frontend/registration/user_detail_change.html'

    **Logic Description**:

        * User is able to change his/her detail.
    """
    user_detail = get_object_or_404(Agent, username=request.user)
    user_detail_extened = AgentProfile.objects.get(user=user_detail)

    user_detail_form = UserChangeDetailForm(request.user,
                                            instance=user_detail)
    user_detail_extened_form = \
        AgentDetailExtendForm(request.user,
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
                AgentDetailExtendForm(
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


@permission_required('agent.view_agent', login_url='/')
@login_required
def agent_list(request):
    """Agent list for the logged in Manager

    **Attributes**:

        * ``template`` - frontend/agent/list.html

    **Logic Description**:

        * List all agents which belong to the logged in manager.
    """
    sort_col_field_list = ['user', 'status', 'contact', 'updated_date']
    default_sort_field = 'id'
    pagination_data = get_pagination_vars(
        request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']

    agent_list = AgentProfile.objects \
        .filter(manager=request.user).order_by(sort_order)

    template = 'frontend/agent/list.html'
    data = {
        'msg': request.session.get('msg'),
        'agent_list': agent_list,
        'total_agent': agent_list.count(),
        'PAGE_SIZE': PAGE_SIZE,
        'AGENT_COLUMN_NAME': AGENT_COLUMN_NAME,
        'col_name_with_order': pagination_data['col_name_with_order'],
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('agent.add_agentprofile', login_url='/')
@login_required
def agent_add(request):
    """Add new Agent for the logged in manager

    **Attributes**:

        * ``form`` - AgentCreationForm
        * ``template`` - frontend/agent/change.html

    **Logic Description**:

        * Add a new agent which will belong to the logged in manager
          via the AgentCreationForm & get redirected to the agent list
    """
    form = AgentCreationForm()
    if request.method == 'POST':
        form = AgentCreationForm(request.POST)
        if form.is_valid():
            new_agent = form.save()

            new_agent_profile = AgentProfile.objects.create(
                user=new_agent,
                manager=Manager.objects.get(username=request.user),
                is_agent=True
            )
            permission = Permission.objects.get(codename='view_agent_dashboard')
            new_agent.user_permissions.add(permission)

            request.session["msg"] = _('"%(name)s" added as agent.') % \
                {'name': request.POST['username']}
            return HttpResponseRedirect(redirect_url_to_agent_list + '%s/' % str(new_agent_profile.id))

    template = 'frontend/agent/change.html'
    data = {
        'form': form,
        'action': 'add',
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('agent.delete_agentprofile', login_url='/')
@login_required
def agent_del(request, object_id):
    """Delete a agent for a logged in manager

    **Attributes**:

        * ``object_id`` - Selected agent object
        * ``object_list`` - Selected agent objects

    **Logic Description**:

        * Delete agent from a agent list.
    """
    if int(object_id) != 0:
        # When object_id is not 0
        # 1) delete agent profile & agent
        agent_profile = get_object_or_404(
            AgentProfile, pk=object_id, manager_id=request.user.id)
        agent = Agent.objects.get(pk=agent_profile.user_id)

        request.session["msg"] = _('"%(name)s" is deleted.') \
            % {'name': agent}
        agent.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        try:
            # 1) delete all agents belonging to a managers
            agent_list = AgentProfile.objects \
                .filter(manager_id=request.user.id) \
                .extra(where=['id IN (%s)' % values])

            if agent_list:
                user_list = agent_list.values_list('user_id', flat=True)
                agents = Agent.objects.filter(pk__in=user_list)
                request.session["msg"] = _('%(count)s agent(s) are deleted.') \
                    % {'count': agent_list.count()}
                agents.delete()
        except:
            raise Http404

    return HttpResponseRedirect(redirect_url_to_agent_list)


@permission_required('agent.change_agentprofile', login_url='/')
@login_required
def agent_change(request, object_id):
    """Update/Delete Agent for the logged in manager

    **Attributes**:

        * ``object_id`` - Selected agent object
        * ``form`` - AgentChangeDetailExtendForm, AgentNameChangeForm
        * ``template`` - frontend/agent/change.html

    **Logic Description**:

        * Update/delete selected agent from the agent list
          via AgentChangeDetailExtendForm & get redirected to agent list
    """
    agent_profile = get_object_or_404(AgentProfile, pk=object_id, manager_id=request.user.id)
    agent_userdetail = get_object_or_404(Agent, pk=agent_profile.user_id)

    form = AgentChangeDetailExtendForm(request.user, instance=agent_profile)
    agent_username_form = AgentNameChangeForm(initial={
        'username': agent_userdetail.username,
        'password': agent_userdetail.password})

    if request.method == 'POST':
        if request.POST.get('delete'):
            agent_del(request, object_id)
            return HttpResponseRedirect(redirect_url_to_agent_list)
        else:
            form = AgentChangeDetailExtendForm(request.user, request.POST,
                                               instance=agent_profile)

            agent_username_form = AgentNameChangeForm(
                request.POST, initial={'password': agent_userdetail.password},
                instance=agent_userdetail)

            # Save agent username
            if agent_username_form.is_valid():
                agent_username_form.save()

                if form.is_valid():
                    form.save()
                    request.session["msg"] = _('"%(name)s" is updated.') \
                        % {'name': agent_profile.user}
                    return HttpResponseRedirect(redirect_url_to_agent_list)

    template = 'frontend/agent/change.html'
    data = {
        'form': form,
        'agent_username_form': agent_username_form,
        'action': 'update',
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))
