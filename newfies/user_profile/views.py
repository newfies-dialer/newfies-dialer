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

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from dialer_campaign.models import common_contact_authorization
from dialer_campaign.function_def import user_dialer_setting_msg
from dialer_settings.models import DialerSetting
from user_profile.models import UserProfile
from user_profile.forms import UserChangeDetailForm, \
    UserChangeDetailExtendForm, UserPasswordChangeForm,\
    CheckPhoneNumberForm


@login_required
def customer_detail_change(request):
    """User Detail change on Customer UI

    **Attributes**:

        * ``form`` - UserChangeDetailForm, UserChangeDetailExtendForm,
                        UserPasswordChangeForm, CheckPhoneNumberForm
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
        if not settings.DEMO_MODE:
            user_detail_extened.save()

    user_detail_form = UserChangeDetailForm(request.user,
                                            instance=user_detail)
    user_detail_extened_form = UserChangeDetailExtendForm(request.user,
                                                          instance=user_detail_extened)

    user_password_form = UserPasswordChangeForm(user=request.user)
    check_phone_no_form = CheckPhoneNumberForm()

    msg_detail = ''
    msg_pass = ''
    msg_number = ''

    error_detail = ''
    error_pass = ''
    error_number = ''
    action = ''
    if 'action' in request.GET:
        action = request.GET['action']

    if request.method == 'POST':
        if request.POST['form-type'] == "change-detail":
            user_detail_form = UserChangeDetailForm(
                request.user, request.POST, instance=user_detail)
            user_detail_extened_form = UserChangeDetailExtendForm(
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
        elif request.POST['form-type'] == "check-number":  # check phone no
            action = 'tabs-4'
            check_phone_no_form = CheckPhoneNumberForm(data=request.POST)
            if check_phone_no_form.is_valid():
                dialersetting = request.user.get_profile().dialersetting
                if not common_contact_authorization(dialersetting, request.POST['phone_number']):
                    error_number = _('this phone number is not authorized.')
                else:
                    msg_number = _('this phone number is authorized.')
            else:
                error_number = _('please correct the errors below.')
        else:  # "change-password"
            user_password_form = UserPasswordChangeForm(user=request.user,
                                                        data=request.POST)
            action = 'tabs-2'
            if user_password_form.is_valid():
                #DEMO / Disable
                if not settings.DEMO_MODE:
                    user_password_form.save()
                msg_pass = _('your password has been changed.')
            else:
                error_pass = _('please correct the errors below.')

    try:
        dialer_set = user_detail_extened.dialersetting
    except:
        dialer_set = ''

    template = 'frontend/registration/user_detail_change.html'
    data = {
        'user_detail_form': user_detail_form,
        'user_detail_extened_form': user_detail_extened_form,
        'user_password_form': user_password_form,
        'check_phone_no_form': check_phone_no_form,
        'msg_detail': msg_detail,
        'msg_pass': msg_pass,
        'msg_number': msg_number,
        'error_detail': error_detail,
        'error_pass': error_pass,
        'error_number': error_number,
        'dialer_set': dialer_set,
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
        'action': action,
    }
    return render_to_response(template, data, context_instance=RequestContext(request))
