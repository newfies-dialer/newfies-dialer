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

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, \
    permission_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.conf import settings
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.db.models import get_model
from dialer_contact.models import Phonebook
from dialer_campaign.models import Campaign
from dialer_campaign.forms import CampaignForm, DuplicateCampaignForm
from dialer_campaign.constants import CAMPAIGN_STATUS, CAMPAIGN_COLUMN_NAME
from dialer_campaign.function_def import user_attached_with_dialer_settings, \
    check_dialer_setting, dialer_setting_limit, user_dialer_setting_msg
from dialer_campaign.tasks import collect_subscriber
from survey.function_def import check_survey_campaign
from voice_app.function_def import check_voiceapp_campaign
from user_profile.constants import NOTIFICATION_NAME
from frontend_notification.views import notice_count, frontend_send_notification
from common.common_functions import current_view, get_pagination_vars
import re


@login_required
def update_campaign_status_admin(request, pk, status):
    """Campaign Status (e.g. start|stop|pause|abort) can be changed from
    admin interface (via campaign list)"""
    obj_campaign = Campaign.objects.get(id=pk)
    recipient = obj_campaign.update_status(status)
    frontend_send_notification(request, status, recipient)
    return HttpResponseRedirect(
        reverse("admin:dialer_campaign_campaign_changelist"))


@login_required
def update_campaign_status_cust(request, pk, status):
    """Campaign Status (e.g. start|stop|pause|abort) can be changed from
    customer interface (via dialer_campaign/campaign list)"""
    obj_campaign = Campaign.objects.get(id=pk)

    pagination_path = '/campaign/'
    if request.session.get('pagination_path'):
        pagination_path = request.session.get('pagination_path')

    # Notify user while campaign Start & no phonebook attached
    if int(status) == CAMPAIGN_STATUS.START and obj_campaign.phonebook.all().count() == 0:
        request.session['error_msg'] = _('Error : You have to assign a phonebook to your campaign before starting it')
    else:
        recipient = obj_campaign.update_status(status)
        frontend_send_notification(request, status, recipient)

        # Notify user while campaign Start
        if int(status) == CAMPAIGN_STATUS.START:
            request.session['info_msg'] = \
                _('The campaign global settings cannot be edited when the campaign is started')
            if obj_campaign.content_type.model == 'survey_template':
                check_survey_campaign(request, pk)
            elif obj_campaign.content_type.model == 'voiceapp_template':
                check_voiceapp_campaign(request, pk)

    return HttpResponseRedirect(pagination_path)


@login_required
def notify_admin(request):
    """Notify administrator regarding dialer setting configuration for
       system user via mail
    """
    # TODO : get recipient = admin user
    recipient = User.objects.get(pk=request.user.pk)
    if not request.session['has_notified']:
        frontend_send_notification(
            request, NOTIFICATION_NAME.dialer_setting_configuration, recipient)
        # Send mail to ADMINS
        subject = _('Dialer setting configuration')
        message = _('Notification - User Dialer Setting The user "%(user)s" - "%(user_id)s" is not properly configured to use the system, please configure their dialer settings.') %\
            {'user': request.user, 'user_id': request.user.id}
        # mail_admins() is a shortcut for sending an email to the site admins,
        # as defined in the ADMINS setting
        mail_admins(subject, message)
        request.session['has_notified'] = True

    return HttpResponseRedirect('/dashboard/')


def tpl_control_icon(icon):
    """
    function to produce control html icon
    """
    return 'style="text-decoration:none;background-image:url(%snewfies/icons/%s);"' % (settings.STATIC_URL, icon)


def get_url_campaign_status(id, status):
    """
    Helper to display campaign status button on the grid
    """
    #Store html for campaign control button
    control_play_style = tpl_control_icon('control_play.png')
    control_pause_style = tpl_control_icon('control_pause.png')
    control_abort_style = tpl_control_icon('control_abort.png')
    control_stop_style = tpl_control_icon('control_stop.png')

    #set different url for the campaign status
    url_cpg_status = 'update_campaign_status_cust/%s' % str(id)
    url_cpg_start = '%s/%s/' % (url_cpg_status, CAMPAIGN_STATUS.START)
    url_cpg_pause = '%s/%s/' % (url_cpg_status, CAMPAIGN_STATUS.PAUSE)
    url_cpg_abort = '%s/%s/' % (url_cpg_status, CAMPAIGN_STATUS.ABORT)
    url_cpg_stop = '%s/%s/' % (url_cpg_status, CAMPAIGN_STATUS.END)

    #according to the current status, disable link and change the button color
    if status == CAMPAIGN_STATUS.START:
        url_cpg_start = '#'
        control_play_style = tpl_control_icon('control_play_blue.png')
    elif status == CAMPAIGN_STATUS.PAUSE:
        url_cpg_pause = '#'
        control_pause_style = tpl_control_icon('control_pause_blue.png')
    elif status == CAMPAIGN_STATUS.ABORT:
        url_cpg_abort = '#'
        control_abort_style = tpl_control_icon('abort.png')
    elif status == CAMPAIGN_STATUS.END:
        url_cpg_stop = '#'
        control_stop_style = tpl_control_icon('control_stop_blue.png')

    #return all the html button for campaign status management
    return "<a href='%s' class='icon' title='%s' %s>&nbsp;</a> <a href='%s' class='icon' title='%s' %s>&nbsp;</a> <a href='%s' class='icon' title='%s' %s>&nbsp;</a> <a href='%s' class='icon' title='%s' %s>&nbsp;</a>" % \
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


def get_campaign_survey_view(campaign_object):
    """display view button on campaign list"""
    link = ''
    if campaign_object.status and int(campaign_object.status) == CAMPAIGN_STATUS.START:
        if campaign_object.content_type.model == 'survey':
            link = '<a href="/survey_view/%s/" target="_blank" class="icon" title="%s" %s>&nbsp;</a>' % \
                   (campaign_object.object_id, _('Survey'),
                    tpl_control_icon('zoom.png'))

        if campaign_object.content_type.model == 'voiceapp':
            link = '<a href="/voiceapp_view/%s/" target="_blank" class="icon" title="%s" %s>&nbsp;</a>' % \
                   (campaign_object.object_id, _('Voice app'),
                    tpl_control_icon('zoom.png'))

    if campaign_object.status and int(campaign_object.status) != CAMPAIGN_STATUS.START:
        if campaign_object.content_type.model == 'survey_template':
            link = '<a href="/survey/%s/" target="_blank" class="icon" title="%s" %s>&nbsp;</a>' %\
                   (campaign_object.object_id, _('Edit Survey'),
                    tpl_control_icon('zoom.png'))

        if campaign_object.content_type.model == 'voiceapp_template':
            link = '<a href="/voiceapp/%s/" target="_blank" class="icon" title="%s" %s>&nbsp;</a>' %\
                   (campaign_object.object_id, _('Edit Voice app'),
                    tpl_control_icon('zoom.png'))
    return link


def make_duplicate_campaign(campaign_object_id):
    link = '<a href="#campaign-duplicate"  url="/campaign_duplicate/%s/" class="campaign-duplicate icon" data-toggle="modal" data-controls-modal="campaign-duplicate" title="%s" %s>&nbsp;</a>'\
           % (campaign_object_id, _('Duplicate this campaign'),
              tpl_control_icon('layers.png'))
    return link


@permission_required('dialer_campaign.view_campaign', login_url='/')
@login_required
def campaign_list(request):
    """List all campaigns for the logged in user

    **Attributes**:

        * ``template`` - frontend/campaign/list.html

    **Logic Description**:

        * List all campaigns belonging to the logged in user
    """
    request.session['pagination_path'] = request.META['PATH_INFO'] + '?' + request.META['QUERY_STRING']
    sort_col_field_list = ['id', 'name', 'startingdate', 'status', 'totalcontact']
    default_sort_field = 'id'
    pagination_data =\
        get_pagination_vars(request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']

    campaign_list = Campaign.objects.filter(user=request.user).order_by(sort_order)

    template = 'frontend/campaign/list.html'
    data = {
        'module': current_view(request),
        'campaign_list': campaign_list,
        'total_campaign': campaign_list.count(),
        'PAGE_SIZE': PAGE_SIZE,
        'CAMPAIGN_COLUMN_NAME': CAMPAIGN_COLUMN_NAME,
        'col_name_with_order': pagination_data['col_name_with_order'],
        'msg': request.session.get('msg'),
        'error_msg': request.session.get('error_msg'),
        'info_msg': request.session.get('info_msg'),
        'notice_count': notice_count(request),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    request.session['info_msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


def get_content_type(object_string):
    """
    Retrieve ContentType and Object ID from a string
    It is used by campaign_add & campaign_change

    >>> get_content_type("type:31-id:1")
    {'object_type': <ContentType: Phonebook>, 'object_id': '1'}
    """
    contenttype = {}
    matches = re.match("type:(\d+)-id:(\d+)", object_string).groups()
    object_type_id = matches[0]  # get 45 from "type:45-id:38"
    contenttype['object_id'] = matches[1]  # get 38 from "type:45-id:38"
    contenttype['object_type'] = ContentType.objects.get(id=object_type_id)
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
                % {'limit': dialer_setting_limit(request, limit_for="campaign")}
            request.session['msg'] = msg

            # campaign limit reached
            frontend_send_notification(request, NOTIFICATION_NAME.campaign_limit_reached)
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
            if obj.status == CAMPAIGN_STATUS.START:
                if obj.content_type.model == 'survey_template':
                    check_survey_campaign(request, obj.id)
                elif obj.content_type.model == 'voiceapp_template':
                    check_voiceapp_campaign(request, obj.id)

                collect_subscriber.delay(obj.pk)

            form.save_m2m()

            request.session["msg"] = _('"%(name)s" added.') %\
                {'name': request.POST['name']}
            return HttpResponseRedirect('/campaign/')

    template = 'frontend/campaign/change.html'
    data = {
        'module': current_view(request),
        'form': form,
        'action': 'add',
        'notice_count': notice_count(request),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
        'AMD': settings.AMD,
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
            raise Http404

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

    if campaign.status == CAMPAIGN_STATUS.START:
        request.session['info_msg'] =\
            _('The campaign is started, you can only edit Dialer settings and Campaign schedule')

    if request.method == 'POST':
        # Delete campaign
        if request.POST.get('delete'):
            campaign_del(request, object_id)
            request.session["msg"] = _('"%(name)s" is deleted.')\
                % {'name': request.POST['name']}
            request.session['error_msg'] = ''
            return HttpResponseRedirect('/campaign/')
        else:
            # Update campaign
            form = CampaignForm(request.user, request.POST, instance=campaign)
            previous_status = int(campaign.status)

            if form.is_valid():
                form.save()
                obj = form.save(commit=False)

                selected_content_object = form.cleaned_data['content_object']
                if not selected_content_object:
                    selected_content_object = form.cleaned_data['selected_content_object']
                # while campaign status is running
                if campaign.status == CAMPAIGN_STATUS.START:
                    if request.POST.get('selected_phonebook'):
                        selected_phonebook = str(request.POST
                            .get('selected_phonebook')).split(',')
                        obj.phonebook = Phonebook.objects\
                            .filter(id__in=selected_phonebook)

                contenttype = get_content_type(selected_content_object)
                obj.content_type = contenttype['object_type']
                obj.object_id = contenttype['object_id']
                obj.save()

                # Start tasks to import subscriber
                if (obj.status
                   and int(obj.status) == CAMPAIGN_STATUS.START
                   and previous_status != CAMPAIGN_STATUS.START):
                    collect_subscriber.delay(obj.id)

                request.session["msg"] = _('"%(name)s" is updated.') \
                    % {'name': request.POST['name']}
                request.session['error_msg'] = ''
                return HttpResponseRedirect('/campaign/')

    template = 'frontend/campaign/change.html'
    data = {
        'module': current_view(request),
        'form': form,
        'action': 'update',
        'notice_count': notice_count(request),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
        'error_msg': request.session.get('error_msg'),
        'info_msg': request.session.get('info_msg'),
        'AMD': settings.AMD,
    }
    request.session['error_msg'] = ''
    request.session['info_msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def campaign_duplicate(request, id):
    form = DuplicateCampaignForm()
    request.session['error_msg'] = ''
    if request.method == 'POST':
        form = DuplicateCampaignForm(request.POST)
        if form.is_valid():

            campaign_obj = Campaign.objects.get(pk=id)
            del campaign_obj.__dict__['_state']
            del campaign_obj.__dict__['id']
            del campaign_obj.__dict__['campaign_code']

            dup_campaign = Campaign(**campaign_obj.__dict__)
            dup_campaign.campaign_code = request.POST.get('campaign_code')
            dup_campaign.name = request.POST.get('name')
            dup_campaign.status = CAMPAIGN_STATUS.PAUSE
            dup_campaign.totalcontact = 0
            dup_campaign.completed = 0
            dup_campaign.imported_phonebook = ''
            dup_campaign.save()

            # Many to many field
            for pb in request.POST.getlist('phonebook'):
                dup_campaign.phonebook.add(pb)

            return HttpResponseRedirect('/campaign/')
        else:
            request.session['error_msg'] = True
    else:
        request.session['error_msg'] = ''

    template = 'frontend/campaign/campaign_duplicate.html'
    data = {
        'module': current_view(request),
        'campaign_id': id,
        'form': form,
        'notice_count': notice_count(request),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
        'err_msg': request.session.get('error_msg'),
    }
    request.session['error_msg'] = ''
    return render_to_response(template, data,
        context_instance=RequestContext(request))
