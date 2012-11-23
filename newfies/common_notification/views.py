#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _

from django.db.models import Q
from django.conf import settings
from notification import models as notification
from common_notification.constants import NOTICE_COLUMN_NAME
from common.common_functions import current_view, get_pagination_vars


@login_required
def notice_count(request):
    """Get count of logged in user's notifications"""
    notice_count = notification.Notice.objects\
        .filter(recipient=request.user, unseen=1)\
        .count()
    return notice_count


def common_notification_status(request, id):
    """Notification Status (e.g. seen/unseen) need to be change.
    It is a common function for admin and customer UI

    **Attributes**:

        * ``pk`` - primary key of notice record

    **Logic Description**:

        * Selected Notification's status need to be changed.
          Changed status can be seen or unseen.
    """
    notice = notification.Notice.objects.get(pk=id)
    if notice.unseen == 1:
        notice.unseen = 0
    else:
        notice.unseen = 1
    notice.save()
    return True


def get_notification_list_for_view(request):
    sort_col_field_list = ['message', 'notice_type', 'sender', 'added']
    default_sort_field = 'message'
    pagination_data =\
        get_pagination_vars(request, sort_col_field_list, default_sort_field)
    sort_order = pagination_data['sort_order']

    user_notification =\
        notification.Notice.objects.filter(recipient=request.user)
    # Search on sender name
    q = (Q(sender=request.user))
    if q:
        user_notification = user_notification.filter(q)

    user_notification = user_notification.order_by(sort_order)
    data = {
        'pagination_data': pagination_data,
        'user_notification': user_notification,
    }
    return data


@login_required
def user_notification(request):
    """User Detail change on Customer UI

    **Attributes**:

        * ``form`` - UserChangeDetailForm, UserChangeDetailExtendForm,
                        PasswordChangeForm, CheckPhoneNumberForm
        * ``template`` - 'frontend/registration/user_detail_change.html'

    **Logic Description**:

        * User is able to change his/her detail.
    """

    notification_data = get_notification_list_for_view(request)
    PAGE_SIZE = notification_data['pagination_data']['PAGE_SIZE']
    sort_order = notification_data['pagination_data']['sort_order']
    col_name_with_order = notification_data['pagination_data']['col_name_with_order']
    user_notification = notification_data['user_notification']

    msg_note = ''
    if request.GET.get('msg_note') == 'true':
        msg_note = request.session['msg_note']

    # Mark all notification as read
    if request.GET.get('notification') == 'mark_read_all':
        notification_list = notification.Notice.objects\
            .filter(unseen=1, recipient=request.user)
        notification_list.update(unseen=0)
        msg_note = _('All notifications are marked as read.')


    template = 'frontend/common_notification/user_notification.html'
    data = {
        'module': current_view(request),
        'msg_note': msg_note,
        'notice_count': notice_count(request),
        'user_notification': user_notification,
        'col_name_with_order': col_name_with_order,
        'PAGE_SIZE': PAGE_SIZE,
        'NOTICE_COLUMN_NAME': NOTICE_COLUMN_NAME,
    }
    return render_to_response(template, data,
        context_instance=RequestContext(request))


@login_required
def notification_del_read(request, object_id):
    """Delete notification for the logged in user

    **Attributes**:

        * ``object_id`` - Selected notification object
        * ``object_list`` - Selected notification objects

    **Logic Description**:

        * Delete/Mark as Read the selected notification
    """
    try:
        # When object_id is not 0
        notification_obj = notification.Notice.objects.get(pk=object_id)
        # Delete/Read notification
        if object_id:
            if request.POST.get('mark_read') == 'false':
                request.session["msg_note"] = _('"%(name)s" is deleted.')\
                                              % {'name': notification_obj.notice_type}
                notification_obj.delete()
            else:
                request.session["msg_note"] = _('"%(name)s" is marked as read.')\
                                              % {'name': notification_obj.notice_type}
                notification_obj.update(unseen=0)

            return HttpResponseRedirect(
                '/user_notification/?msg_note=true')
    except:
        # When object_id is 0 (Multiple records delete/mark as read)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        notification_list =\
            notification.Notice.objects.extra(where=['id IN (%s)' % values])
        if request.POST.get('mark_read') == 'false':
            request.session["msg_note"] =\
            _('%(count)s notification(s) are deleted.')\
                % {'count': notification_list.count()}
            notification_list.delete()
        else:
            request.session["msg_note"] =\
            _('%(count)s notification(s) are marked as read.')\
                % {'count': notification_list.count()}
            notification_list.update(unseen=0)
        return HttpResponseRedirect(
            '/user_notification/?msg_note=true')


@login_required
def update_notification(request, id):
    """Notification Status (e.g. seen/unseen) can be changed from
    customer interface"""
    common_notification_status(request, id)
    return HttpResponseRedirect('/user_notification/')
