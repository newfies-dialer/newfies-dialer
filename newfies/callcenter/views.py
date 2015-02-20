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
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.template.context import RequestContext
from user_profile.models import Manager
from callcenter.models import Queue, Tier
from callcenter.constants import QUEUE_COLUMN_NAME, TIER_COLUMN_NAME
from callcenter.forms import QueueFrontEndForm, TierFrontEndForm
from django_lets_go.common_functions import get_pagination_vars
from survey.models import Section_template

redirect_url_to_queue_list = '/module/queue/'
redirect_url_to_tier_list = '/module/tier/'


@permission_required('callcenter.view_queue', login_url='/')
@login_required
def queue_list(request):
    """Queue list for the logged in Manager

    **Attributes**:

        * ``template`` - callcenter/queue/list.html

    **Logic Description**:

        * List all queue which belong to the logged in manager.
    """
    sort_col_field_list = ['name', 'strategy', 'time_base_score', 'updated_date']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    queue_list = Queue.objects.filter(manager=request.user).order_by(pag_vars['sort_order'])
    data = {
        'msg': request.session.get('msg'),
        'error_msg': request.session.get('error_msg'),
        'queue_list': queue_list,
        'total_queue': queue_list.count(),
        'QUEUE_COLUMN_NAME': QUEUE_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('callcenter/queue/list.html', data, context_instance=RequestContext(request))


@permission_required('callcenter.add_queue', login_url='/')
@login_required
def queue_add(request):
    """Add new queue for the logged in manager

    **Attributes**:

        * ``form`` - QueueFrontEndForm
        * ``template`` - callcenter/queue/change.html

    **Logic Description**:

        * Add a new queue which will belong to the logged in manager
          via the UserCreationForm & get redirected to the queue list
    """
    form = QueueFrontEndForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.manager = Manager.objects.get(username=request.user)
        obj.save()
        request.session["msg"] = _('"%(name)s" queue is added.') % {'name': obj.name}
        return HttpResponseRedirect(redirect_url_to_queue_list)

    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('callcenter/queue/change.html', data, context_instance=RequestContext(request))


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
        queue = get_object_or_404(Queue, pk=object_id, manager=request.user)

        if queue_delete_allow(object_id):
            # Delete queue
            request.session["msg"] = _('"%(name)s" is deleted.') % {'name': queue.name}
            queue.delete()
        else:
            request.session["error_msg"] = _('"%(name)s" is not allowed to delete because it is being used with survey.') % {'name': queue.name}
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
                    request.session["msg"] = _('%s queue(s) are deleted.') % deleted_list
                if not_deleted_list:
                    request.session["error_msg"] = _('%s queue(s) are not deleted because they are being used with surveys.')\
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
        * ``template`` - callcenter/queue/change.html

    **Logic Description**:

        * Update/delete selected queue from the queue list
          via QueueFrontEndForm & get redirected to the queue list
    """
    queue = get_object_or_404(Queue, pk=object_id, manager=request.user)
    form = QueueFrontEndForm(request.POST or None, instance=queue)
    if form.is_valid():
        # Delete queue
        if request.POST.get('delete'):
            queue_del(request, object_id)
            return HttpResponseRedirect(redirect_url_to_queue_list)
        else:
            # Update queue
            obj = form.save()
            request.session["msg"] = _('"%(name)s" is updated.') % {'name': obj.name}
            return HttpResponseRedirect(redirect_url_to_queue_list)

    data = {
        'form': form,
        'action': 'update',
    }
    return render_to_response('callcenter/queue/change.html', data, context_instance=RequestContext(request))


@permission_required('callcenter.view_tier', login_url='/')
@login_required
def tier_list(request):
    """Tier list for the logged in Manager

    **Attributes**:

        * ``template`` - callcenter/tier/list.html

    **Logic Description**:

        * List all tier which belong to the logged in manager.
    """
    sort_col_field_list = ['agent', 'queue', 'level', 'position', 'updated_date']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    tier_list = Tier.objects.filter(manager=request.user).order_by(pag_vars['sort_order'])
    data = {
        'msg': request.session.get('msg'),
        'tier_list': tier_list,
        'total_tier': tier_list.count(),
        'TIER_COLUMN_NAME': TIER_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('callcenter/tier/list.html', data, context_instance=RequestContext(request))


@permission_required('callcenter.add_tier', login_url='/')
@login_required
def tier_add(request):
    """Add new tier for the logged in manager

    **Attributes**:

        * ``form`` - TierFrontEndForm
        * ``template`` - callcenter/tier/change.html

    **Logic Description**:

        * Add a new tier which will belong to the logged in manager
          via the TierFrontEndForm & get redirected to the tier list
    """
    form = TierFrontEndForm(request.user.id, request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.manager = Manager.objects.get(username=request.user)
        obj.save()

        request.session["msg"] = _('"%(name)s" tier is added.') % {'name': obj.id}
        return HttpResponseRedirect(redirect_url_to_tier_list)
    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('callcenter/tier/change.html', data,
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
        tier = get_object_or_404(Tier, pk=object_id, manager=request.user)

        # Delete tier
        request.session["msg"] = _('"%(name)s" is deleted.') % {'name': tier.id}
        tier.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        try:
            tier_list = Tier.objects.extra(where=['id IN (%s)' % values])
            if tier_list:
                request.session["msg"] = _('%(count)s tier(s) are deleted.') % {'count': tier_list.count()}
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
        * ``template`` - callcenter/tier/change.html

    **Logic Description**:

        * Update/delete selected tier from the tier list
          via TierFrontEndForm & get redirected to the tier list
    """
    tier = get_object_or_404(Tier, pk=object_id, manager=request.user)
    form = TierFrontEndForm(request.user.id, request.POST or None, instance=tier)
    if form.is_valid():
        # Delete tier
        if request.POST.get('delete'):
            tier_del(request, object_id)
            return HttpResponseRedirect(redirect_url_to_tier_list)
        else:
            # Update tier
            form.save()
            request.session["msg"] = _('"%(id)s" tier is updated.') % {'id': tier.id}
            return HttpResponseRedirect(redirect_url_to_tier_list)

    data = {
        'form': form,
        'action': 'update',
    }
    return render_to_response('callcenter/tier/change.html', data, context_instance=RequestContext(request))
