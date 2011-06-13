from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.db.models import *
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from notification import models as notification
from dialer_campaign.views import current_view, notice_count
from user_profile.forms import *


@login_required
def customer_detail_change(request):
    """User Detail change on Customer UI

    **Attributes**:

        * ``form`` - UserChangeDetailForm
        * ``template`` - 'frontend/registration/user_detail_change.html'

    **Logic Description**:

        * User is able to change his/her detail.
    """
    user_detail = User.objects.get(username=request.user)
    user_detail_form = UserChangeDetailForm(user=request.user,
                                            instance=user_detail)
    user_password_form = PasswordChangeForm(user=request.user)


    user_notification = \
    notification.Notice.objects.filter(recipient=request.user)
    # Search on sender name
    q = (Q(sender=request.user))
    if q:
        user_notification = user_notification.filter(q)

    msg_detail = ''
    msg_pass = ''
    error_detail = ''
    error_pass = ''
    selected = 0

    if 'selected' in request.GET:
        selected = request.GET['selected']

    if request.method == 'POST':
        if request.POST['form-type'] == "change-detail":
            user_detail_form = UserChangeDetailForm(request.user, request.POST,
                                                    instance=user_detail)
            selected = 0
            if user_detail_form.is_valid():
                user_detail_form.save()
                msg_detail = _('Your detail has been changed successfully.')
            else:
                error_detail = _('Please correct the errors below.')
        else: # "change-password"
            user_password_form = PasswordChangeForm(user=request.user,
                                                    data=request.POST)
            selected = 1
            if user_password_form.is_valid():
                user_password_form.save()
                msg_pass = _('Your password has been changed successfully.')
            else:
                error_pass = _('Please correct the errors below.')
    
    template = 'frontend/registration/user_detail_change.html'
    data = {
        'module': current_view(request),
        'user_detail_form': user_detail_form,
        'user_password_form': user_password_form,
        'user_notification': user_notification,
        'msg_detail': msg_detail,
        'msg_pass': msg_pass,
        'selected': selected,
        'error_detail': error_detail,
        'error_pass': error_pass,
        'notice_count': notice_count(request),
    }    
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def view_notification(request, id):
    """Notice view in detail on Customer UI

    **Attributes**:
       
        * ``template`` - 'frontend/registration/user_notice.html'

    **Logic Description**:

        * User is able to change his/her detail.
    """
    user_notice = notification.Notice.objects.get(pk=id)
    user_notice.unseen = 0
    user_notice.save()
    template = 'frontend/registration/user_notice.html'
    data = {
        'module': current_view(request),
        'notice': user_notice,
        'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


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
    return HttpResponseRedirect('/user_detail_change/?selected=2')
