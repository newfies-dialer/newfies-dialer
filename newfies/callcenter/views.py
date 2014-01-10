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
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.template.context import RequestContext
from user_profile.models import Manager
from callcenter.models import Queue, Tier
from callcenter.constants import QUEUE_COLUMN_NAME, TIER_COLUMN_NAME
from callcenter.forms import QueueFrontEndForm, TierFrontEndForm
from dialer_campaign.function_def import user_dialer_setting_msg
from common.common_functions import get_pagination_vars
from survey.models import Section_template

redirect_url_to_queue_list = '/module/queue/'
redirect_url_to_tier_list = '/module/tier/'


@permission_required('callcenter.view_queue', login_url='/')
@login_required
def queue_list(request):
    """Queue list for the logged in Manager

    **Attributes**:

        * ``template`` - frontend/queue/list.html

    **Logic Description**:

        * List all queue which belong to the logged in manager.
    """
    sort_col_field_list = ['name', 'strategy', 'time_base_score', 'updated_date']
    default_sort_field = 'id'
    pagination_data = get_pagination_vars(
        request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']

    queue_list = Queue.objects\
        .filter(manager=request.user).order_by(sort_order)

    template = 'frontend/queue/list.html'
    data = {
        'msg': request.session.get('msg'),
        'error_msg': request.session.get('error_msg'),
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
                {'name': obj.name}
            return HttpResponseRedirect(redirect_url_to_queue_list)

    template = 'frontend/queue/change.html'
    data = {
        'form': form,
        'action': 'add',
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


def queue_delete_allow(queue_id):
    """Check queue is attached to any survey section or not"""
    try:
        section_count = Section_template.objects.filter(queue_id=queue_id).count()
        if section_count > 0:
            return False
        else:
            return True
    except:
        return True


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

        if queue_delete_allow(object_id):
            # Delete queue
            request.session["msg"] = _('"%(name)s" is deleted.')\
                % {'name': queue.name}
            queue.delete()
        else:
            request.session["error_msg"] = \
                _('"%(name)s" is not allowed to delete because it is being used with survey.')\
                % {'name': queue.name}
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        deleted_list = []
        not_deleted_list = []
        try:
            queue_list = Queue.objects.extra(where=['id IN (%s)' % values])
            if queue_list:
                for queue_obj in queue_list:
                    if queue_delete_allow(queue_obj.id):
                        deleted_list.append(str(queue_obj.name))
                        queue_obj.delete()
                    else:
                        not_deleted_list.append(str(queue_obj.name))

                if deleted_list:
                    request.session["msg"] =\
                        _('%s queue(s) are deleted.') % deleted_list
                if not_deleted_list:
                    request.session["error_msg"] =\
                        _('%s queue(s) are not deleted because they are being used with surveys.')\
                        % not_deleted_list
        except:
            raise Http404
    return HttpResponseRedirect(redirect_url_to_queue_list)


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
            return HttpResponseRedirect(redirect_url_to_queue_list)
        else:
            # Update queue
            form = QueueFrontEndForm(request.POST, instance=queue)
            if form.is_valid():
                obj = form.save()
                request.session["msg"] = _('"%(name)s" is updated.') \
                    % {'name': obj.name}
                return HttpResponseRedirect(redirect_url_to_queue_list)

    template = 'frontend/queue/change.html'
    data = {
        'form': form,
        'action': 'update',
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('callcenter.view_tier', login_url='/')
@login_required
def tier_list(request):
    """Tier list for the logged in Manager

    **Attributes**:

        * ``template`` - frontend/tier/list.html

    **Logic Description**:

        * List all tier which belong to the logged in manager.
    """
    sort_col_field_list = ['agent', 'queue', 'level', 'position', 'updated_date']
    default_sort_field = 'id'
    pagination_data = get_pagination_vars(request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']

    tier_list = Tier.objects\
        .filter(manager=request.user).order_by(sort_order)

    template = 'frontend/tier/list.html'
    data = {
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


@permission_required('callcenter.add_tier', login_url='/')
@login_required
def tier_add(request):
    """Add new tier for the logged in manager

    **Attributes**:

        * ``form`` - TierFrontEndForm
        * ``template`` - frontend/tier/change.html

    **Logic Description**:

        * Add a new tier which will belong to the logged in manager
          via the TierFrontEndForm & get redirected to the tier list
    """
    form = TierFrontEndForm(request.user.id)
    if request.method == 'POST':
        form = TierFrontEndForm(request.user.id, request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.manager = Manager.objects.get(username=request.user)
            obj.save()

            request.session["msg"] = _('"%(name)s" tier is added.') %\
                {'name': obj.id}
            return HttpResponseRedirect(redirect_url_to_tier_list)

    template = 'frontend/tier/change.html'
    data = {
        'form': form,
        'action': 'add',
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('callcenter.delete_tier', login_url='/')
@login_required
def tier_del(request, object_id):
    """Delete tier for the logged in Manager

    **Attributes**:

        * ``object_id`` - Selected tier object
        * ``object_list`` - Selected tier objects

    **Logic Description**:

        * Delete selected tier from the tier list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        tier = get_object_or_404(
            Tier, pk=object_id, manager=request.user)

        # Delete tier
        request.session["msg"] = _('"%(name)s" is deleted.')\
            % {'name': tier.id}
        tier.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        try:
            tier_list = Tier.objects.extra(where=['id IN (%s)' % values])
            if tier_list:
                request.session["msg"] =\
                    _('%(count)s tier(s) are deleted.')\
                    % {'count': tier_list.count()}
                tier_list.delete()
        except:
            raise Http404
    return HttpResponseRedirect(redirect_url_to_tier_list)


@permission_required('callcenter.change_tier', login_url='/')
@login_required
def tier_change(request, object_id):
    """Update/Delete tier for the logged in manager

    **Attributes**:

        * ``object_id`` - Selected tier object
        * ``form`` - TierFrontEndForm
        * ``template`` - frontend/tier/change.html

    **Logic Description**:

        * Update/delete selected tier from the tier list
          via TierFrontEndForm & get redirected to the tier list
    """
    tier = get_object_or_404(
        Tier, pk=object_id, manager=request.user)

    form = TierFrontEndForm(request.user.id, instance=tier)
    if request.method == 'POST':
        # Delete tier
        if request.POST.get('delete'):
            tier_del(request, object_id)
            return HttpResponseRedirect(redirect_url_to_tier_list)
        else:
            # Update tier
            form = TierFrontEndForm(request.user.id, request.POST, instance=tier)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%(id)s" tier is updated.') \
                    % {'id': tier.id}
                return HttpResponseRedirect(redirect_url_to_tier_list)

    template = 'frontend/tier/change.html'
    data = {
        'form': form,
        'action': 'update',
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))
