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

from callcenter.models import Queue, Tier
from callcenter.constants import QUEUE_COLUMN_NAME
#from callcenter.forms import QueueForm
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
        'total_agent': queue_list.count(),
        'PAGE_SIZE': PAGE_SIZE,
        'QUEUE_COLUMN_NAME': QUEUE_COLUMN_NAME,
        'col_name_with_order': pagination_data['col_name_with_order'],
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))