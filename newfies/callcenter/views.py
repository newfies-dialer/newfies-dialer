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
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.template.context import RequestContext
from django.contrib.auth.models import Permission
from user_profile.models import Manager
from callcenter.models import Queue, Tier
from callcenter.constants import QUEUE_COLUMN_NAME, TIER_COLUMN_NAME
from callcenter.forms import QueueFrontEndForm
from dialer_campaign.function_def import user_dialer_setting_msg
from common.common_functions import current_view, get_pagination_vars


@permission_required('callcenter.view_queue_list', login_url='/')
@login_required
def queue_list(request):
    """Queue list for the logged in Manager

    **Attributes**:

        * ``template`` - frontend/queue/list.html

    **Logic Description**:

        * List all queue which belong to the logged in manager.
    """
    sort_col_field_list = ['id', 'manager', 'updated_date']
    default_sort_field = 'id'
    pagination_data = \
        get_pagination_vars(request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']

    queue_list = Queue.objects\
        .filter(manager=request.user).order_by(sort_order)

    template = 'frontend/queue/list.html'
    data = {
        'module': current_view(request),
        'msg': request.session.get('msg'),
        'queue_list': queue_list,
        'total_queue': queue_list.count(),
        'PAGE_SIZE': PAGE_SIZE,
        'QUEUE_COLUMN_NAME': QUEUE_COLUMN_NAME,
        'col_name_with_order': pagination_data['col_name_with_order'],
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('callcenter.add_queue', login_url='/')
@login_required
def queue_add(request):
    """Add new queue for the logged in manager

    **Attributes**:

        * ``form`` - QueueFrontEndForm
        * ``template`` - frontend/queue/change.html

    **Logic Description**:

        * Add a new queue which will belong to the logged in manager
          via the UserCreationForm & get redirected to the queue list
    """
    form = QueueFrontEndForm()
    if request.method == 'POST':
        form = QueueFrontEndForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.manager = Manager.objects.get(username=request.user)
            obj.save()

            request.session["msg"] = _('"%(name)s" queue is added.') %\
                {'name': request.POST['strategy']}
            return HttpResponseRedirect('/queue/')

    template = 'frontend/queue/change.html'
    data = {
        'module': current_view(request),
        'form': form,
        'action': 'add',
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('callcenter.delete_queue', login_url='/')
@login_required
def queue_del(request, object_id):
    """Delete queue for the logged in Manager

    **Attributes**:

        * ``object_id`` - Selected queue object
        * ``object_list`` - Selected queue objects

    **Logic Description**:

        * Delete selected queue from the queue list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        queue = get_object_or_404(
            Queue, pk=object_id, manager=request.user)

        # Delete queue
        request.session["msg"] = _('"%(name)s" is deleted.')\
            % {'name': queue.strategy}
        queue.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        try:
            queue_list = Queue.objects.extra(where=['id IN (%s)' % values])
            if queue_list:
                request.session["msg"] =\
                    _('%(count)s queue(s) are deleted.')\
                    % {'count': queue_list.count()}
                queue_list.delete()
        except:
            raise Http404
    return HttpResponseRedirect('/queue/')


@permission_required('callcenter.change_queue', login_url='/')
@login_required
def queue_change(request, object_id):
    """Update/Delete queue for the logged in manager

    **Attributes**:

        * ``object_id`` - Selected queue object
        * ``form`` - QueueFrontEndForm
        * ``template`` - frontend/queue/change.html

    **Logic Description**:

        * Update/delete selected queue from the queue list
          via QueueFrontEndForm & get redirected to the queue list
    """
    queue = get_object_or_404(
        Queue, pk=object_id, manager=request.user)

    form = QueueFrontEndForm(instance=queue)
    if request.method == 'POST':
        # Delete queue
        if request.POST.get('delete'):
            queue_del(request, object_id)
            return HttpResponseRedirect('/queue/')
        else:
            # Update queue
            form = QueueFrontEndForm(request.POST, instance=queue)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%(name)s" is updated.') \
                    % {'name': request.POST['strategy']}
                return HttpResponseRedirect('/queue/')

    template = 'frontend/queue/change.html'
    data = {
        'module': current_view(request),
        'form': form,
        'action': 'update',
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('callcenter.view_tier_list', login_url='/')
@login_required
def tier_list(request):
    """Tier list for the logged in Manager

    **Attributes**:

        * ``template`` - frontend/tier/list.html

    **Logic Description**:

        * List all tier which belong to the logged in manager.
    """
    sort_col_field_list = ['id', 'agent', 'queue', 'level', 'position', 'updated_date']
    default_sort_field = 'id'
    pagination_data = \
        get_pagination_vars(request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']

    tier_list = Tier.objects\
        .filter(manager=request.user).order_by(sort_order)

    template = 'frontend/tier/list.html'
    data = {
        'module': current_view(request),
        'msg': request.session.get('msg'),
        'tier_list': tier_list,
        'total_tier': tier_list.count(),
        'PAGE_SIZE': PAGE_SIZE,
        'TIER_COLUMN_NAME': TIER_COLUMN_NAME,
        'col_name_with_order': pagination_data['col_name_with_order'],
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))