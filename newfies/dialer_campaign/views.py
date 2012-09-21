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
from django.contrib.auth.decorators import login_required, \
                                           permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
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
from utils.helper import grid_common_function, get_grid_update_delete_link
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
    return HttpResponseRedirect(
                reverse("admin:dialer_campaign_campaign_changelist"))


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
    """Count no of Contacts from phonebook belonging to the campaign

    >>> count_contact_of_campaign(1)
    'Phonebook Empty'
    """
    count_contact = Contact.objects\
        .filter(phonebook__campaign=campaign_id).count()
    if not count_contact:
        return str("Phonebook Empty")
    return count_contact


def tpl_control_icon(icon):
    """
    function to produce control html icon
    """
    return 'style="text-decoration:none;background-image:url(' \
        + settings.STATIC_URL \
        + 'newfies/icons/%s);"' % icon


def get_url_campaign_status(id, status):
    """
    Helper to display campaign status button on the grid
    """
    #Store html for campaign control button
    control_play_style = tpl_control_icon('control_play.png')
    control_pause_style = tpl_control_icon('control_pause.png')
    control_abort_style = tpl_control_icon('abort_grey.png')
    control_stop_style = tpl_control_icon('control_stop.png')

    #set different url for the campaign status
    url_cpg_status = 'update_campaign_status_cust/' + str(id)
    url_cpg_start = url_cpg_status + '/1/'
    url_cpg_pause = url_cpg_status + '/2/'
    url_cpg_abort = url_cpg_status + '/3/'
    url_cpg_stop = url_cpg_status + '/4/'

    #according to the current status, disable link and change the button color
    if status == 1:
        url_cpg_start = '#'
        control_play_style = tpl_control_icon('control_play_blue.png')
    elif status == 2:
        url_cpg_pause = '#'
        control_pause_style = tpl_control_icon('control_pause_blue.png')
    elif status == 3:
        url_cpg_abort = '#'
        control_abort_style = tpl_control_icon('abort.png')
    elif status == 4:
        url_cpg_stop = '#'
        control_stop_style = tpl_control_icon('control_stop_blue.png')

    #return all the html button for campaign status management
    return "<a href='%s' class='icon' title='%s' %s>&nbsp;</a>\
        <a href='%s' class='icon' title='%s' %s>&nbsp;</a>\
        <a href='%s' class='icon' title='%s' %s>&nbsp;</a>\
        <a href='%s' class='icon' title='%s' %s>&nbsp;</a>" % \
        (url_cpg_start, _("Start"), control_play_style,
        url_cpg_pause, _("Pause"), control_pause_style,
        url_cpg_abort, _("Abort"), control_abort_style,
        url_cpg_stop, _("Stop"), control_stop_style)


def get_app_name(app_label, model_name, object_id):
    """To get app name from app_label, model_name & object_id"""
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
    campaign_list = campaign_list\
        .order_by(sortorder_sign + sortname)[start_page:end_page]

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
        get_grid_update_delete_link(request, row['id'],
            'dialer_campaign.change_campaign',
            _('Update campaign'), 'update') +\
        get_grid_update_delete_link(request, row['id'],
            'dialer_campaign.delete_campaign',
            _('Delete campaign'), 'delete') +\
        get_url_campaign_status(row['id'], row['status']),
        ]} for row in campaign_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@permission_required('dialer_campaign.view_campaign', login_url='/')
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
    Retrieve ContentType and Object ID from a string
    It is used by campaign_add & campaign_change

    >>> get_content_type("type:31-id:1")
    {'object_type': <ContentType: observed item>, 'object_id': '1'}
    """
    contenttype = {}
    matches = re.match("type:(\d+)-id:(\d+)", object_string).groups()
    object_type_id = matches[0]  # get 45 from "type:45-id:38"
    contenttype['object_id'] = matches[1]  # get 38 from "type:45-id:38"
    try:
        contenttype['object_type'] = ContentType.objects\
                                        .get(id=object_type_id)
    except:
        pass
    return contenttype


@permission_required('dialer_campaign.add_campaign', login_url='/')
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
            contenttype = get_content_type(form.cleaned_data['content_object'])
            obj.content_type = contenttype['object_type']
            obj.object_id = contenttype['object_id']
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


@permission_required('dialer_campaign.delete_campaign', login_url='/')
@login_required
def campaign_del(request, object_id):
    """Delete campaign for the logged in user

    **Attributes**:

        * ``object_id`` - Selected campaign object
        * ``object_list`` - Selected campaign objects

    **Logic Description**:

        * Delete the selected campaign from the campaign list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        campaign = get_object_or_404(Campaign, pk=object_id, user=request.user)
        request.session["msg"] = _('"%(name)s" is deleted.')\
                                 % {'name': campaign.name}
        campaign.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        try:
            campaign_list = Campaign.objects\
                                .filter(user=request.user)\
                                .extra(where=['id IN (%s)' % values])
            if campaign_list:
                request.session["msg"] = _('%(count)s campaign(s) are deleted.')\
                    % {'count': campaign_list.count()}
                campaign_list.delete()
        except:
            request.session["error_msg"] =\
                _('campaign(s) do not belong to user')

    return HttpResponseRedirect('/campaign/')


@permission_required('dialer_campaign.change_campaign', login_url='/')
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

    campaign = get_object_or_404(Campaign, pk=object_id, user=request.user)

    content_object = "type:%s-id:%s" % \
                        (campaign.content_type_id, campaign.object_id)
    form = CampaignForm(request.user,
                        instance=campaign,
                        initial={'content_object': content_object})

    if request.method == 'POST':
        # Delete campaign
        if request.POST.get('delete'):
            campaign_del(request, object_id)
            request.session["msg"] = _('"%(name)s" is deleted.')\
                % {'name': request.POST['name']}
            return HttpResponseRedirect('/campaign/')
        else:
            # Update campaign
            form = CampaignForm(request.user, request.POST, instance=campaign)
            previous_status = campaign.status
            if form.is_valid():
                form.save()
                obj = form.save(commit=False)
                contenttype = get_content_type(form.cleaned_data['content_object'])
                obj.content_type = contenttype['object_type']
                obj.object_id = contenttype['object_id']
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
