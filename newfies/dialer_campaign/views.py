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
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.conf import settings
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.contrib.contenttypes.models import ContentType
from django.db.models import get_model
from notification import models as notification
from frontend.views import notice_count
from dialer_contact.models import Contact
from dialer_contact.views import grid_common_function, update_style, \
                                delete_style
from dialer_campaign.models import Campaign
from dialer_campaign.forms import CampaignForm
from dialer_campaign.function_def import user_attached_with_dialer_settings, \
                        check_dialer_setting, dialer_setting_limit, \
                        get_campaign_status_name, user_dialer_setting_msg
from dialer_campaign.tasks import collect_subscriber
from common.common_functions import current_view
import re


def common_send_notification(request, status, recipient=None):
    """User Notification (e.g. start | stop | pause | abort |
    contact/camapign limit) needs to be saved.
    It is a common function for the admin and customer UI's

    **Attributes**:

        * ``pk`` - primary key of the campaign record
        * ``status`` - get label for notifications

    **Logic Description**:

        * This function is used by ``update_campaign_status_admin()`` &
          ``update_campaign_status_cust()``

    """
    if not recipient:
        recipient = request.user
        sender = User.objects.get(is_superuser=1, username=recipient)
    else:
        if request.user.is_anonymous():
            sender = User.objects.get(is_superuser=1, username=recipient)
        else:
            sender = request.user

    if notification:
        note_label = notification.NoticeType.objects.get(default=status)
        notification.send([recipient],
                          note_label.label,
                          {"from_user": request.user},
                          sender=sender)
    return True


def common_campaign_status(pk, status):
    """Campaign Status (e.g. start | stop | abort | pause) needs to be changed.
    It is a common function for the admin and customer UI's

    **Attributes**:

        * ``pk`` - primary key of the campaign record
        * ``status`` - selected status for the campaign record

    **Logic Description**:

        * Selected Campaign's status needs to be changed.
          Changed status can be start, stop or pause.

        * This function is used by ``update_campaign_status_admin()`` &
          ``update_campaign_status_cust()``
    """
    campaign = Campaign.objects.get(pk=pk)
    previous_status = campaign.status
    campaign.status = status
    campaign.save()

    #Start tasks to import subscriber
    if status == "1" and previous_status != "1":
        collect_subscriber.delay(pk)

    return campaign.user


@login_required
def update_campaign_status_admin(request, pk, status):
    """Campaign Status (e.g. start|stop|pause|abort) can be changed from
    admin interface (via campaign list)"""
    recipient = common_campaign_status(pk, status)
    common_send_notification(request, status, recipient)
    return HttpResponseRedirect(reverse(
                                "admin:dialer_campaign_campaign_changelist"))


@login_required
def update_campaign_status_cust(request, pk, status):
    """Campaign Status (e.g. start|stop|pause|abort) can be changed from
    customer interface (via dialer_campaign/campaign list)"""
    recipient = common_campaign_status(pk, status)
    common_send_notification(request, status, recipient)
    return HttpResponseRedirect('/campaign/')


@login_required
def notify_admin(request):
    """Notify administrator regarding dialer setting configuration for
       system user via mail
    """
    # TODO : get recipient = admin user
    recipient = User.objects.get(pk=request.user.pk)
    if request.session['has_notified'] == False:
        common_send_notification(request, 7, recipient)
        # Send mail to ADMINS
        subject = _('Dialer setting configuration')
        message = _('Notification - User Dialer Setting The user "%(user)s" - "%(user_id)s" is not properly configured to use the system, please configure their dialer settings.') %\
          {'user': request.user, 'user_id': request.user.id}
        # mail_admins() is a shortcut for sending an email to the site admins,
        # as defined in the ADMINS setting
        mail_admins(subject, message)
        request.session['has_notified'] = True

    return HttpResponseRedirect('/dashboard/')


def count_contact_of_campaign(campaign_id):
    """Count no of Contacts from phonebook belonging to the campaign"""
    count_contact = \
        Contact.objects.filter(phonebook__campaign=campaign_id).count()
    if not count_contact:
        return str("Phonebook Empty")
    return count_contact


def get_url_campaign_status(id, status):

    control_play_style = \
        'style="text-decoration:none;background-image:url(' \
        + settings.STATIC_URL \
        + 'newfies/icons/control_play.png);"'
    control_pause_style = \
        'style="text-decoration:none;background-image:url(' \
        + settings.STATIC_URL \
        + 'newfies/icons/control_pause.png);"'
    control_abort_style = \
        'style="text-decoration:none;background-image:url(' \
        + settings.STATIC_URL\
        + 'newfies/icons/abort.png);"'
    control_stop_style = \
        'style="text-decoration:none;background-image:url(' \
        + settings.STATIC_URL\
        + 'newfies/icons/control_stop.png);"'

    control_play_blue_style = \
        'style="text-decoration:none;background-image:url(' \
        + settings.STATIC_URL \
        + 'newfies/icons/control_play_blue.png);"'
    control_pause_blue_style = \
        'style="text-decoration:none;background-image:url(' \
        + settings.STATIC_URL \
        + 'newfies/icons/control_pause_blue.png);"'
    control_abort_blue_style = \
        'style="text-decoration:none;background-image:url(' \
        + settings.STATIC_URL \
        + 'newfies/icons/abort.png);"'
    control_stop_blue_style = \
        'style="text-decoration:none;background-image:url(' \
        + settings.STATIC_URL \
        + 'newfies/icons/control_stop_blue.png);"'

    if status == 1:
        url_str = "<a href='#' class='icon' title='" + \
            _("campaign is running") + "' " +\
            control_play_style + ">&nbsp;</a>\
            <a href='update_campaign_status_cust/" + str(id) +\
            "/2/' class='icon' title='" + _("Pause") + "' " +\
            str(control_pause_blue_style) +\
            ">&nbsp;</a><a href='update_campaign_status_cust/" + str(id) +\
            "/3/' class='icon' title='" + _("Abort") + "' " +\
            str(control_abort_blue_style) +\
            ">&nbsp;</a><a href='update_campaign_status_cust/"\
            + str(id) + "/4/' class='icon' title='" + _("Stop") + "' " +\
            str(control_stop_blue_style) + ">&nbsp;</a>"

    if status == 2:
        url_str = "<a href='update_campaign_status_cust/" + str(id) +\
            "/1/' class='icon' title='" + _("Start") + "' " +\
            control_play_blue_style + ">&nbsp;</a><a href='#' \
            class='icon' title='" + _("campaign is paused") + "' " +\
            control_pause_style + ">&nbsp;</a>" +\
            "<a href='update_campaign_status_cust/" + str(id) +\
            "/3/' class='icon' title='" + _("Abort") + "' " +\
            control_abort_blue_style +\
            ">&nbsp;</a>" +\
            "<a href='update_campaign_status_cust/" + str(id) +\
            "/4/' class='icon' title='" + _("Stop") + "' " +\
            control_stop_blue_style +\
            ">&nbsp;</a>"

    if status == 3:
        url_str = "<a href='update_campaign_status_cust/" + str(id) +\
            "/1/' class='icon' title='" + _("Start") + "' " +\
            control_play_blue_style +\
            ">&nbsp;</a>" + "<a href='update_campaign_status_cust/" +\
            str(id) + "/2/' class='icon' \
            title='" + _("Pause") + "' " + control_pause_blue_style +\
            ">&nbsp;</a>" +\
            "<a href='#' class='icon' title='" + _("campaign is aborted") +\
            "' " + control_abort_style + " >&nbsp;</a>" +\
            "<a href='update_campaign_status_cust/" + str(id) +\
            "/4/' class='icon' title='" + _("Stop") + "' " +\
            control_stop_blue_style + ">&nbsp;</a>"
    if status == 4:
        url_str = "<a href='update_campaign_status_cust/" + str(id) +\
            "/1/' class='icon' title='" + _("Start") + "' " +\
            control_play_blue_style +\
            ">&nbsp;</a>" +\
            "<a href='update_campaign_status_cust/" + str(id) +\
            "/2/' class='icon' title='" + _("Pause") + "' " +\
            control_pause_blue_style +\
            ">&nbsp;</a>" +\
            "<a href='update_campaign_status_cust/" + str(id) +\
            "/3/' class='icon' title='" + _("Abort") + "' " +\
            control_abort_blue_style +\
            ">&nbsp;</a>" + \
            "<a href='#' class='icon' title='" + _("campaign is stopped") + \
            "' " + control_stop_style + ">&nbsp;</a>"

    return url_str


def get_app_name(app_label, model_name, object_id):
    try:
        return get_model(app_label, model_name).objects.get(pk=object_id)
    except:
        return '-'


# Campaign
@login_required
def campaign_grid(request):
    """Campaign list in json format for flexigrid

    **Model**: Campaign
    """
    grid_data = grid_common_function(request)
    page = int(grid_data['page'])
    start_page = int(grid_data['start_page'])
    end_page = int(grid_data['end_page'])
    sortorder_sign = grid_data['sortorder_sign']
    sortname = grid_data['sortname']

    campaign_list = Campaign.objects\
                    .values('id', 'campaign_code', 'name', 'startingdate',
                            'expirationdate', 'aleg_gateway',
                            'aleg_gateway__name', 'content_type__name',
                            'content_type__app_label', 'object_id',
                            'content_type__model', 'status')\
                    .filter(user=request.user)
    count = campaign_list.count()
    campaign_list = \
        campaign_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    rows = [
        {'id': row['id'],
        'cell': ['<input type="checkbox" name="select" class="checkbox"\
        value="' + str(row['id']) + '" />',
        row['campaign_code'],
        row['name'],
        row['startingdate'].strftime('%Y-%m-%d %H:%M:%S'),
        row['content_type__name'],
        str(get_app_name(row['content_type__app_label'],
                        row['content_type__model'],
                        row['object_id'])),
        count_contact_of_campaign(row['id']),
        get_campaign_status_name(row['status']),
        '<a href="' + str(row['id']) + '/" class="icon" ' \
        + update_style + ' title="' + _('Update campaign') + '">&nbsp;</a>' \
        + '<a href="del/' + str(row['id']) \
        + '/" class="icon" ' + delete_style \
        + ' onClick="return get_alert_msg(' + str(row['id']) + ');" title="' \
        + _('Delete campaign') + '">&nbsp;</a>' \
        + get_url_campaign_status(row['id'], row['status']),
        ]} for row in campaign_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@login_required
def campaign_list(request):
    """List all campaigns for the logged in user

    **Attributes**:

        * ``template`` - frontend/campaign/list.html

    **Logic Description**:

        * List all campaigns belonging to the logged in user
    """
    template = 'frontend/campaign/list.html'
    data = {
        'module': current_view(request),
        'msg': request.session.get('msg'),
        'error_msg': request.session.get('error_msg'),
        'notice_count': notice_count(request),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


def get_content_type(object_string):
    """
    It is used by campaign_add & campaign_change to get ContentType object
    """
    result_array = {}
    matches = re.match("type:(\d+)-id:(\d+)", object_string).groups()
    object_type_id = matches[0]  # get 45 from "type:45-id:38"
    result_array['object_id'] = matches[1]  # get 38 from "type:45-id:38"
    try:
        result_array['object_type'] = ContentType.objects\
                                        .get(id=object_type_id)
    except:
        pass
    return result_array


@login_required
def campaign_add(request):
    """Add a new campaign for the logged in user

    **Attributes**:

        * ``form`` - CampaignForm
        * ``template`` - frontend/campaign/change.html

    **Logic Description**:

        * Before adding a campaign, check dialer setting limit if
          applicable to the user.
        * Add the new campaign which will belong to the logged in user
          via CampaignForm & get redirected to campaign list
    """
    # If dialer setting is not attached with user, redirect to campaign list
    if user_attached_with_dialer_settings(request):
        request.session['error_msg'] = \
            _("In order to add a campaign, you need to have your settings configured properly, please contact the admin.")
        return HttpResponseRedirect("/campaign/")

    # Check dialer setting limit
    if request.user and request.method != 'POST':
        # check Max Number of running campaign
        if check_dialer_setting(request, check_for="campaign"):
            msg = _("you have too many campaigns. Max allowed %(limit)s") \
                    % {'limit': \
                        dialer_setting_limit(request, limit_for="campaign")}
            request.session['msg'] = msg

            # campaign limit reached
            common_send_notification(request, '5')
            return HttpResponseRedirect("/campaign/")

    form = CampaignForm(request.user)
    # Add campaign
    if request.method == 'POST':
        form = CampaignForm(request.user, request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            result_array = \
                get_content_type(form.cleaned_data['content_object'])
            obj.content_type = result_array['object_type']
            obj.object_id = result_array['object_id']
            obj.user = User.objects.get(username=request.user)
            obj.save()

            # Start tasks to import subscriber
            if obj.status == 1:
                collect_subscriber.delay(obj.pk)
            form.save_m2m()

            request.session["msg"] = _('"%(name)s" is added.') %\
                {'name': request.POST['name']}
            return HttpResponseRedirect('/campaign/')

    template = 'frontend/campaign/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'add',
       'notice_count': notice_count(request),
       'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def campaign_del(request, object_id):
    """Delete campaign for the logged in user

    **Attributes**:

        * ``object_id`` - Selected campaign object
        * ``object_list`` - Selected campaign objects

    **Logic Description**:

        * Delete the selected campaign from the campaign list
    """
    try:
        # When object_id is not 0
        campaign = Campaign.objects.get(pk=object_id)
        # Delete campaign
        if object_id:
            request.session["msg"] = _('"%(name)s" is deleted.') \
                % {'name': campaign.name}
            campaign.delete()
            return HttpResponseRedirect('/campaign/')
    except:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        campaign_list = Campaign.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] = _('%(count)s campaign(s) are deleted.')\
            % {'count': campaign_list.count()}
        campaign_list.delete()
        return HttpResponseRedirect('/campaign/')


@login_required
def campaign_change(request, object_id):
    """Update/Delete campaign for the logged in user

    **Attributes**:

        * ``object_id`` - Selected campaign object
        * ``form`` - CampaignForm
        * ``template`` - frontend/campaign/change.html

    **Logic Description**:

        * Update/delete selected campaign from the campaign list
          via CampaignForm & get redirected to the campaign list
    """
    # If dialer setting is not attached with user, redirect to campaign list
    if user_attached_with_dialer_settings(request):
        return HttpResponseRedirect("/campaign/")

    campaign = Campaign.objects.get(pk=object_id)

    content_object = "type:%s-id:%s" % \
                        (campaign.content_type_id, campaign.object_id)
    form = CampaignForm(request.user,
                        instance=campaign,
                        initial={'content_object': content_object})
    if request.method == 'POST':
        # Delete campaign
        if request.POST.get('delete'):
            campaign_del(request, object_id)
            return HttpResponseRedirect('/campaign/')
        else:
            # Update campaign
            form = CampaignForm(request.user, request.POST, instance=campaign)
            previous_status = campaign.status
            if form.is_valid():
                form.save()
                obj = form.save(commit=False)
                result_array = \
                    get_content_type(form.cleaned_data['content_object'])
                obj.content_type = result_array['object_type']
                obj.object_id = result_array['object_id']
                obj.save()

                # Start tasks to import subscriber
                if obj.status == 1 and previous_status != 1:
                    collect_subscriber.delay(obj.id)

                request.session["msg"] = _('"%(name)s" is updated.') \
                    % {'name': request.POST['name']}
                return HttpResponseRedirect('/campaign/')

    template = 'frontend/campaign/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'update',
       'notice_count': notice_count(request),
       'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))
