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
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.db.models import Q
from django.conf import settings
from notification import models as notification
from dialer_campaign.models import common_contact_authorization
from dialer_campaign.views import notice_count, grid_common_function
from dialer_campaign.function_def import user_dialer_setting_msg
from dialer_settings.models import DialerSetting
from user_profile.models import UserProfile
from user_profile.forms import UserChangeDetailForm, \
                               UserChangeDetailExtendForm, \
                               CheckPhoneNumberForm
from common.common_functions import current_view


@login_required
def customer_detail_change(request):
    """User Detail change on Customer UI

    **Attributes**:

        * ``form`` - UserChangeDetailForm, UserChangeDetailExtendForm,
                        PasswordChangeForm, CheckPhoneNumberForm
        * ``template`` - 'frontend/registration/user_detail_change.html'

    **Logic Description**:

        * User is able to change his/her detail.
    """
    user_detail = get_object_or_404(User, username=request.user)
    try:
        user_detail_extened = UserProfile.objects.get(user=user_detail)
    except UserProfile.DoesNotExist:
        #create UserProfile
        user_detail_extened = UserProfile(user=user_detail)
        #DEMO / Disable
        user_detail_extened.save()

    user_detail_form = UserChangeDetailForm(request.user,
                                            instance=user_detail)
    user_detail_extened_form = \
        UserChangeDetailExtendForm(request.user,
                                   instance=user_detail_extened)

    user_password_form = PasswordChangeForm(user=request.user)
    check_phone_no_form = CheckPhoneNumberForm()

    try:
        user_ds = UserProfile.objects.get(user=request.user)
        dialer_set = DialerSetting.objects.get(id=user_ds.dialersetting.id)
    except:
        dialer_set = ''

    user_notification = \
        notification.Notice.objects.filter(recipient=request.user)
    # Search on sender name
    q = (Q(sender=request.user))
    if q:
        user_notification = user_notification.filter(q)

    msg_detail = ''
    msg_pass = ''
    msg_number = ''
    msg_note = ''
    error_detail = ''
    error_pass = ''
    error_number = ''
    action = ''

    if 'action' in request.GET:
        action = request.GET['action']

    if request.GET.get('msg_note') == 'true':
        msg_note = request.session['msg_note']

    # Mark all notification as read
    if request.GET.get('notification') == 'mark_read_all':
        notification_list = \
            notification.Notice.objects.filter(unseen=1,
                                               recipient=request.user)
        notification_list.update(unseen=0)
        msg_note = _('All notifications are marked as read.')

    if request.method == 'POST':
        if request.POST['form-type'] == "change-detail":
            user_detail_form = UserChangeDetailForm(request.user,
                                                    request.POST,
                                                    instance=user_detail)
            user_detail_extened_form = \
                UserChangeDetailExtendForm(request.user, request.POST,
                                           instance=user_detail_extened)
            action = 'tabs-1'
            if user_detail_form.is_valid() \
                and user_detail_extened_form.is_valid():
                #DEMO / Disable
                user_detail_form.save()
                user_detail_extened_form.save()
                msg_detail = _('Detail has been changed.')
            else:
                error_detail = _('Please correct the errors below.')
        elif request.POST['form-type'] == "check-number":  # check phone no
            action = 'tabs-5'
            check_phone_no_form = CheckPhoneNumberForm(data=request.POST)
            if check_phone_no_form.is_valid():
                if not common_contact_authorization(
                    request.user,
                    request.POST['phone_number']):
                    error_number = _('This phone number is not authorized.')
                else:
                    msg_number = _('This phone number is authorized.')
            else:
                error_number = _('Please correct the errors below.')
        else:  # "change-password"
            user_password_form = PasswordChangeForm(user=request.user,
                                                    data=request.POST)
            action = 'tabs-2'
            if user_password_form.is_valid():
                #DEMO / Disable
                user_password_form.save()
                msg_pass = _('Your password has been changed.')
            else:
                error_pass = _('Please correct the errors below.')

    template = 'frontend/registration/user_detail_change.html'
    data = {
        'module': current_view(request),
        'user_detail_form': user_detail_form,
        'user_detail_extened_form': user_detail_extened_form,
        'user_password_form': user_password_form,
        'check_phone_no_form': check_phone_no_form,
        'user_notification': user_notification,
        'msg_detail': msg_detail,
        'msg_pass': msg_pass,
        'msg_number': msg_number,
        'msg_note': msg_note,
        'error_detail': error_detail,
        'error_pass': error_pass,
        'error_number': error_number,
        'notice_count': notice_count(request),
        'dialer_set': dialer_set,
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
        'action': action,
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


def call_style(val):
    """Notification icon style

    >>> call_style('val')
    'style="text-decoration:none;background-image:url(/static/newfies/icons/new.png);"'

    >>> call_style('')
    'style="text-decoration:none;background-image:url(/static/newfies/icons/tick.png);"'
    """
    unseen_style = \
        'style="text-decoration:none;\
        background-image:url(%snewfies/icons/new.png);"' \
            % settings.STATIC_URL
    seen_style = \
        'style="text-decoration:none;\
        background-image:url(%snewfies/icons/tick.png);"' \
            % settings.STATIC_URL

    if val:
        return unseen_style
    else:
        return seen_style


# Notification
@login_required
def notification_grid(request):
    """notification list in json format for flexigrid

    **Model**: notification.Notice
    """
    grid_data = grid_common_function(request)
    page = int(grid_data['page'])
    start_page = int(grid_data['start_page'])
    end_page = int(grid_data['end_page'])
    sortorder_sign = grid_data['sortorder_sign']
    sortname = grid_data['sortname']

    user_notification = \
        notification.Notice.objects.filter(recipient=request.user)
    # Search on sender name
    q = (Q(sender=request.user))
    if q:
        user_notification = user_notification.filter(q)

    count = user_notification.count()
    user_notification_list = user_notification\
                     .order_by(sortorder_sign + sortname)[start_page:end_page]

    rows = [{'id': row.id,
             'cell': ['<input type="checkbox" name="select" class="checkbox"\
                      value="%s" />' % (str(row.id)),
                      str(row.message),
                      str(row.notice_type),
                      str(row.sender),
                      str(row.added),
                      str('<a href="../update_notice_status_cust/%s/" \
                      class="icon" %s>&nbsp;</a>' % (str(row.id), call_style(row.unseen))),
             ]}for row in user_notification_list]

    data = {'rows': rows,
            'page': page,
            'total': count}

    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


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
                request.session["msg_note"] = _('"%(name)s" is deleted.') \
                    % {'name': notification_obj.notice_type}
                notification_obj.delete()
            else:
                request.session["msg_note"] = _('"%(name)s" is marked as read.') \
                    % {'name': notification_obj.notice_type}
                notification_obj.update(unseen=0)

            return HttpResponseRedirect(
                    '/user_detail_change/?action=tabs-3&msg_note=true')
    except:
        # When object_id is 0 (Multiple records delete/mark as read)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        notification_list = \
            notification.Notice.objects.extra(where=['id IN (%s)' % values])
        if request.POST.get('mark_read') == 'false':
            request.session["msg_note"] = \
                _('%(count)s notification(s) are deleted.')\
                    % {'count': notification_list.count()}
            notification_list.delete()
        else:
            request.session["msg_note"] = \
                _('%(count)s notification(s) are marked as read.')\
                    % {'count': notification_list.count()}
            notification_list.update(unseen=0)
        return HttpResponseRedirect(
            '/user_detail_change/?action=tabs-3&msg_note=true')


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


@login_required
def update_notice_status_cust(request, id):
    """Notification Status (e.g. seen/unseen) can be changed from
    customer interface"""
    common_notification_status(request, id)
    return HttpResponseRedirect('/user_detail_change/?action=tabs-3')
