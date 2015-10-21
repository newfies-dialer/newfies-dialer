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

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from dateutil.relativedelta import relativedelta
from django.utils.timezone import utc

from datetime import datetime
import re
import tablib
from frontend_notification.views import frontend_send_notification
from django_lets_go.common_functions import ceil_strdate, getvar, get_pagination_vars, unset_session_var

from .models import Campaign, Subscriber
from .forms import CampaignForm, DuplicateCampaignForm, \
    SubscriberSearchForm, CampaignSearchForm
from .constants import CAMPAIGN_STATUS, CAMPAIGN_COLUMN_NAME, \
    SUBSCRIBER_COLUMN_NAME
from .function_def import check_dialer_setting, dialer_setting_limit, \
    user_dialer_setting, get_subscriber_status, get_subscriber_disposition
from .tasks import collect_subscriber
from dialer_contact.models import Phonebook
from survey.models import Survey_template
from user_profile.constants import NOTIFICATION_NAME
from mod_utils.helper import Export_choice

redirect_url_to_campaign_list = '/campaign/'


@login_required
def update_campaign_status_admin(request, pk, status):
    """Campaign Status (e.g. start|stop|pause|abort) can be changed from
    admin interface (via campaign list)"""
    obj_campaign = Campaign.objects.get(id=pk)
    obj_campaign.status = status
    obj_campaign.save()
    frontend_send_notification(request, status, recipient=request.user)
    return HttpResponseRedirect(reverse("admin:dialer_campaign_campaign_changelist"))


@login_required
def update_campaign_status_cust(request, pk, status):
    """Campaign Status (e.g. start|stop|pause|abort) can be changed from
    customer interface (via dialer_campaign/campaign list)"""
    obj_campaign = Campaign.objects.get(id=pk)
    obj_campaign.status = status
    if int(status) != CAMPAIGN_STATUS.START:
        obj_campaign.stoppeddate = datetime.utcnow().replace(tzinfo=utc)
    obj_campaign.save()

    pagination_path = redirect_url_to_campaign_list
    if request.session.get('pagination_path'):
        pagination_path = request.session.get('pagination_path')

    # Check if no phonebook attached
    if int(status) == CAMPAIGN_STATUS.START and obj_campaign.phonebook.all().count() == 0:
        request.session['error_msg'] = _('you must assign a phonebook to your campaign before starting it')
        return HttpResponseRedirect(pagination_path)
    elif int(status) == CAMPAIGN_STATUS.START:
        request.session['info_msg'] = _('campaign global settings cannot be edited when the campaign is started')

    # Ensure the content_type become "survey" when campagin starts
    if int(status) == CAMPAIGN_STATUS.START and not obj_campaign.has_been_started:
        # change has_been_started flag
        obj_campaign.has_been_started = True
        obj_campaign.save()

        if obj_campaign.content_type.model == 'survey_template':
            # Copy survey
            survey_template = Survey_template.objects.get(user=request.user, pk=obj_campaign.object_id)
            survey_template.copy_survey_template(obj_campaign.id)
        collect_subscriber.delay(obj_campaign.id)

    # Notify user while campaign Start
    frontend_send_notification(request, status, request.user)
    return HttpResponseRedirect(pagination_path)


@login_required
def notify_admin(request):
    """
    Url to notify the administrators regarding the user dialer settings configuration via mail
    """
    # Get all the admin users - admin superuser
    all_admin_user = User.objects.filter(is_superuser=True)
    for user in all_admin_user:
        recipient = user
        if 'has_notified' not in request.session:
            frontend_send_notification(
                request, NOTIFICATION_NAME.dialer_setting_configuration, recipient)
            # Send mail to ADMINS
            subject = _('Dialer Setting Configuration')
            message = _('Notification - User Dialer Setting. The user "%(user)s" - "%(user_id)s" is not properly '
                        'configured to use the system, please configure their dialer settings.') % \
                {'user': request.user, 'user_id': request.user.id}
            # mail_admins() is a shortcut for sending an email to the site admins,
            # as defined in the ADMINS setting
            mail_admins(subject, message)
            request.session['has_notified'] = True

    return HttpResponseRedirect('/dashboard/')


@permission_required('dialer_campaign.view_campaign', login_url='/')
@login_required
def campaign_list(request):
    """List all campaigns for the logged in user

    **Attributes**:

        * ``template`` - dialer_campaign/campaign/list.html

    **Logic Description**:

        * List all campaigns belonging to the logged in user
    """
    form = CampaignSearchForm(request.user, request.POST or None)
    request.session['pagination_path'] = request.META['PATH_INFO'] + '?' + request.META['QUERY_STRING']
    sort_col_field_list = ['id', 'name', 'startingdate', 'status', 'totalcontact']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    phonebook_id = ''
    status = 'all'
    post_var_with_page = 0

    if form.is_valid():
        field_list = ['phonebook_id', 'status']
        unset_session_var(request, field_list)
        phonebook_id = getvar(request, 'phonebook_id', setsession=True)
        status = getvar(request, 'status', setsession=True)
        post_var_with_page = 1

    # This logic to retain searched result set while accessing pagination or sorting on column
    # post_var_with_page will check following thing
    # 1) if page has previously searched value, then post_var_with_page become 1
    # 2) if not then post_var_with_page remain 0 & flush the session variables' value
    if request.GET.get('page') or request.GET.get('sort_by'):
        post_var_with_page = 1
        phonebook_id = request.session.get('session_phonebook_id')
        status = request.session.get('session_status')
        form = CampaignSearchForm(request.user, initial={'status': status, 'phonebook_id': phonebook_id})

    if post_var_with_page == 0:
        # default / unset session var
        field_list = ['status', 'phonebook_id']
        unset_session_var(request, field_list)

    # Set search on user as default
    kwargs = {'user': request.user}
    if phonebook_id and phonebook_id != '0':
        kwargs['phonebook__id__in'] = [int(phonebook_id)]
    if status and status != 'all':
        kwargs['status'] = status

    all_campaign_list = Campaign.objects.filter(**kwargs).order_by(pag_vars['sort_order'])
    campaign_list = all_campaign_list[pag_vars['start_page']:pag_vars['end_page']]
    campaign_count = all_campaign_list.count()

    data = {
        'form': form,
        'all_campaign_list': all_campaign_list,
        'campaign_list': campaign_list,
        'total_campaign': campaign_count,
        'CAMPAIGN_COLUMN_NAME': CAMPAIGN_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
        'msg': request.session.get('msg'),
        'error_msg': request.session.get('error_msg'),
        'info_msg': request.session.get('info_msg'),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    request.session['info_msg'] = ''
    return render_to_response('dialer_campaign/campaign/list.html', data, context_instance=RequestContext(request))


def get_content_type(object_string):
    """
    Retrieve ContentType and Object ID from a string
    It is used by campaign_add & campaign_change

    #get_content_type("type:38-id:1")
    #{'object_type': <ContentType: Phonebook>, 'object_id': '1'}
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
        * ``template`` - dialer_campaign/campaign/change.html

    **Logic Description**:

        * Before adding a campaign, check dialer setting limit if
          applicable to the user.
        * Add the new campaign which will belong to the logged in user
          via CampaignForm & get redirected to campaign list
    """
    # If dialer setting is not attached with user, redirect to campaign list
    if not user_dialer_setting(request.user):
        request.session['error_msg'] = _("your settings aren't configured properly, please contact the admin.")
        return HttpResponseRedirect(redirect_url_to_campaign_list)

    # Check dialer setting limit
    if request.user and request.method != 'POST':
        # check Max Number of running campaign
        if check_dialer_setting(request, check_for="campaign"):
            msg = _("you have too many campaigns. Max allowed %(limit)s") % \
                {'limit': dialer_setting_limit(request, limit_for="campaign")}
            request.session['msg'] = msg

            # campaign limit reached
            frontend_send_notification(request, NOTIFICATION_NAME.campaign_limit_reached)
            return HttpResponseRedirect(redirect_url_to_campaign_list)

    form = CampaignForm(request.user, request.POST or None)
    # Add campaign
    if form.is_valid():
        obj = form.save(commit=False)
        contenttype = get_content_type(form.cleaned_data['content_object'])
        obj.content_type = contenttype['object_type']
        obj.object_id = contenttype['object_id']
        obj.user = request.user
        obj.stoppeddate = obj.expirationdate
        obj.save()
        form.save_m2m()
        request.session["msg"] = _('"%(name)s" added.') % {'name': request.POST['name']}
        return HttpResponseRedirect(redirect_url_to_campaign_list)

    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('dialer_campaign/campaign/change.html', data, context_instance=RequestContext(request))


@permission_required('dialer_campaign.delete_campaign', login_url='/')
@login_required
def campaign_del(request, object_id):
    """Delete/Stop campaign for the logged in user

    **Attributes**:

        * ``object_id`` - Selected campaign object
        * ``object_list`` - Selected campaign objects

    **Logic Description**:

        * Delete/Stop the selected campaign from the campaign list
    """
    stop_campaign = request.GET.get('stop_campaign', False)
    if int(object_id) != 0:
        # When object_id is not 0
        campaign = get_object_or_404(Campaign, pk=object_id, user=request.user)
        if stop_campaign:
            campaign.status = CAMPAIGN_STATUS.END
            campaign.save()
            request.session["msg"] = _('the campaign "%(name)s" has been stopped.') % {'name': campaign.name}
        else:
            request.session["msg"] = _('the campaign "%(name)s" has been deleted.') % {'name': campaign.name}
            campaign.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        try:
            campaign_list = Campaign.objects.filter(user=request.user).extra(where=['id IN (%s)' % values])
            if campaign_list:
                if stop_campaign:
                    campaign_list.update(status=CAMPAIGN_STATUS.END)
                    request.session["msg"] = _('%(count)s campaign(s) have been stopped.') % \
                        {'count': campaign_list.count()}
                else:
                    request.session["msg"] = _('%(count)s campaign(s) have been deleted.') % \
                        {'count': campaign_list.count()}
                    campaign_list.delete()
        except:
            raise Http404
    return HttpResponseRedirect(redirect_url_to_campaign_list)


@permission_required('dialer_campaign.change_campaign', login_url='/')
@login_required
def campaign_change(request, object_id):
    """
    Update/Delete campaign for the logged in user

    **Attributes**:

        * ``object_id`` - Selected campaign object
        * ``form`` - CampaignForm
        * ``template`` - dialer_campaign/campaign/change.html

    **Logic Description**:

        * Update/delete selected campaign from the campaign list
          via CampaignForm & get redirected to the campaign list

    """
    # If dialer setting is not attached with user, redirect to campaign list
    if not user_dialer_setting(request.user):
        return HttpResponseRedirect(redirect_url_to_campaign_list)

    campaign = get_object_or_404(Campaign, pk=object_id, user=request.user)
    content_object = "type:%s-id:%s" % (campaign.content_type_id, campaign.object_id)
    form = CampaignForm(request.user, request.POST or None, instance=campaign,
                        initial={'content_object': content_object})

    if campaign.status == CAMPAIGN_STATUS.START:
        request.session['info_msg'] = _('Started campaign can only edit the dialer settings and the scheduler')

    if request.method == 'POST':
        # Delete campaign
        if request.POST.get('delete'):
            return HttpResponseRedirect('%sdel/%s/' % (redirect_url_to_campaign_list, object_id))
        # Update campaign
        elif form.is_valid():
            newcpg = form.save(commit=False)

            selected_content_object = form.cleaned_data['content_object']
            if not selected_content_object:
                selected_content_object = form.cleaned_data['selected_content_object']
            # while campaign status is running
            if campaign.status == CAMPAIGN_STATUS.START and request.POST.get('selected_phonebook'):
                selected_phonebook = str(request.POST.get('selected_phonebook')).split(',')
                # TODO: Add user in filter
                newcpg.phonebook = Phonebook.objects.filter(id__in=selected_phonebook)
            else:
                newcpg.phonebook = form.cleaned_data['phonebook']

            contenttype = get_content_type(selected_content_object)
            newcpg.content_type = contenttype['object_type']
            newcpg.object_id = contenttype['object_id']

            # Ugly hack: Solve problem when editing campaign
            newcpg.has_been_started = campaign.has_been_started
            newcpg.has_been_duplicated = campaign.has_been_duplicated
            newcpg.created_date = campaign.created_date
            newcpg.totalcontact = campaign.totalcontact
            newcpg.imported_phonebook = campaign.imported_phonebook
            newcpg.completed = campaign.completed
            # Save the updated Campaign
            newcpg.save()

            request.session["msg"] = _('the campaign "%(name)s" is updated.') % {'name': request.POST['name']}
            request.session['error_msg'] = ''
            return HttpResponseRedirect(redirect_url_to_campaign_list)

    data = {
        'form': form,
        'action': 'update',
        'error_msg': request.session.get('error_msg'),
        'info_msg': request.session.get('info_msg'),
    }
    request.session['error_msg'] = ''
    request.session['info_msg'] = ''
    return render_to_response('dialer_campaign/campaign/change.html', data, context_instance=RequestContext(request))


@login_required
def campaign_duplicate(request, id):
    """
    Duplicate campaign via DuplicateCampaignForm

    **Attributes**:

        * ``id`` - Selected campaign object
        * ``form`` - DuplicateCampaignForm
        * ``template`` - dialer_campaign/campaign/campaign_duplicate.html
    """
    form = DuplicateCampaignForm(request.user, request.POST or None)
    request.session['error_msg'] = ''
    if request.method == 'POST':
        if form.is_valid():
            original_camp = campaign_obj = Campaign.objects.get(pk=id)
            # Make duplicate campaign/survey
            new_survey_id = campaign_obj.object_id

            campaign_obj.pk = None
            campaign_obj.campaign_code = request.POST.get('campaign_code')
            campaign_obj.name = request.POST.get('name')
            campaign_obj.status = CAMPAIGN_STATUS.PAUSE
            campaign_obj.totalcontact = 0
            campaign_obj.completed = 0
            campaign_obj.startingdate = datetime.utcnow().replace(tzinfo=utc)
            campaign_obj.expirationdate = datetime.utcnow().replace(tzinfo=utc) + relativedelta(days=+1)
            campaign_obj.stoppeddate = datetime.utcnow().replace(tzinfo=utc) + relativedelta(days=+1)
            campaign_obj.imported_phonebook = ''
            campaign_obj.has_been_started = False
            campaign_obj.has_been_duplicated = True
            campaign_obj.save()

            if campaign_obj.content_type.model == 'survey':
                survey_obj = original_camp.content_type.model_class().objects.get(pk=original_camp.object_id)
                new_survey_id = survey_obj.create_duplicate_survey(original_camp, campaign_obj)

            campaign_obj.object_id = new_survey_id
            campaign_obj.save()

            # Many to many field
            for pb in request.POST.getlist('phonebook'):
                campaign_obj.phonebook.add(pb)

            return HttpResponseRedirect(redirect_url_to_campaign_list)
        else:
            request.session['error_msg'] = True

    data = {
        'campaign_id': id,
        'form': form,
        'err_msg': request.session.get('error_msg'),
    }
    request.session['error_msg'] = ''
    return render_to_response('dialer_campaign/campaign/campaign_duplicate.html',
                              data, context_instance=RequestContext(request))


@permission_required('dialer_campaign.view_subscriber', login_url='/')
@login_required
def subscriber_list(request):
    """
    Subscriber list for the logged in user

    **Attributes**:

        * ``template`` - dialer_campaign/subscriber/list.html
        * ``form`` - SubscriberSearchForm

    **Logic Description**:

        * List all subscribers belonging to the logged in user & their campaign
    """
    sort_col_field_list = ['contact', 'updated_date', 'count_attempt', 'completion_count_attempt',
                           'status', 'disposition', 'collected_data', 'agent']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    form = SubscriberSearchForm(request.user, request.POST or None)
    campaign_id = ''
    agent_id = ''
    status = 'all'
    start_date = end_date = None
    post_var_with_page = 0
    if form.is_valid():
        post_var_with_page = 1
        field_list = ['start_date', 'end_date', 'status', 'campaign_id', 'agent_id']
        unset_session_var(request, field_list)
        campaign_id = getvar(request, 'campaign_id', setsession=True)
        agent_id = getvar(request, 'agent_id', setsession=True)

        from_date = getvar(request, 'from_date')
        to_date = getvar(request, 'to_date')
        start_date = ceil_strdate(str(from_date), 'start')
        end_date = ceil_strdate(str(to_date), 'end')

        converted_start_date = start_date.strftime('%Y-%m-%d')
        converted_end_date = end_date.strftime('%Y-%m-%d')
        request.session['session_start_date'] = converted_start_date
        request.session['session_end_date'] = converted_end_date

        status = getvar(request, 'status', setsession=True)

    if request.GET.get('page') or request.GET.get('sort_by'):
        post_var_with_page = 1
        start_date = request.session.get('session_start_date')
        end_date = request.session.get('session_end_date')

        start_date = ceil_strdate(str(start_date), 'start')
        end_date = ceil_strdate(str(end_date), 'end')

        campaign_id = request.session.get('session_campaign_id')
        agent_id = request.session.get('session_agent_id')
        status = request.session.get('session_status')
        form = SubscriberSearchForm(
            request.user,
            initial={'from_date': start_date.strftime('%Y-%m-%d'),
                     'to_date': end_date.strftime('%Y-%m-%d'),
                     'campaign_id': campaign_id,
                     'agent_id': agent_id,
                     'status': status})

    if post_var_with_page == 0:
        # default
        tday = datetime.utcnow().replace(tzinfo=utc)
        from_date = tday.strftime('%Y-%m-%d')
        to_date = tday.strftime('%Y-%m-%d')
        start_date = datetime(tday.year, tday.month, tday.day, 0, 0, 0, 0).replace(tzinfo=utc)
        end_date = datetime(tday.year, tday.month, tday.day, 23, 59, 59, 999999).replace(tzinfo=utc)

        form = SubscriberSearchForm(request.user, initial={'from_date': from_date, 'to_date': to_date})
        # unset session var
        request.session['session_start_date'] = start_date
        request.session['session_end_date'] = end_date
        request.session['session_status'] = ''
        request.session['session_campaign_id'] = ''
        request.session['session_agent_id'] = ''

    kwargs = {}
    # updated_date might be replaced with last_attempt
    if start_date and end_date:
        kwargs['updated_date__range'] = (start_date, end_date)
    if start_date and end_date == '':
        kwargs['updated_date__gte'] = start_date
    if start_date == '' and end_date:
        kwargs['updated_date__lte'] = end_date

    if campaign_id and campaign_id != '0':
        kwargs['campaign_id'] = campaign_id

    # if agent_id and agent_id != '0':
    #    kwargs['agent_id'] = agent_id

    if status and status != 'all':
        kwargs['status'] = status

    subscriber_list = []
    all_subscriber_list = []
    subscriber_count = 0

    if request.user.is_superuser:
        subscriber_list = Subscriber.objects.all()
    else:
        subscriber_list = Subscriber.objects.filter(campaign__user=request.user)

    if kwargs:
        subscriber_list = subscriber_list.filter(**kwargs)
        request.session['subscriber_list_kwargs'] = kwargs

    all_subscriber_list = subscriber_list.order_by(pag_vars['sort_order'])
    subscriber_list = all_subscriber_list[pag_vars['start_page']:pag_vars['end_page']]
    subscriber_count = all_subscriber_list.count()

    data = {
        'subscriber_list': subscriber_list,
        'all_subscriber_list': all_subscriber_list,
        'total_subscribers': subscriber_count,
        'SUBSCRIBER_COLUMN_NAME': SUBSCRIBER_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
        'msg': request.session.get('msg'),
        'error_msg': request.session.get('error_msg'),
        'form': form,
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('dialer_campaign/subscriber/list.html', data, context_instance=RequestContext(request))


@login_required
def subscriber_export(request):
    """Export CSV file of subscriber record

    **Important variable**:

        * ``request.session['subscriber_list_kwargs']`` - stores subscriber_list kwargs

    **Exported fields**: ['contact', 'updated_date', 'count_attempt',
                          'completion_count_attempt', 'status', 'disposition',
                          'collected_data', 'agent']
    """
    format_type = request.GET['format']
    # get the response object, this can be used as a stream.
    response = HttpResponse(content_type='text/%s' % format_type)

    # force download.
    response['Content-Disposition'] = 'attachment;filename=export.%s' % format_type

    if request.session.get('subscriber_list_kwargs'):
        kwargs = request.session['subscriber_list_kwargs']
        if request.user.is_superuser:
            subscriber_list = Subscriber.objects.all()
        else:
            subscriber_list = Subscriber.objects.filter(campaign__user=request.user)

        if kwargs:
            subscriber_list = subscriber_list.filter(**kwargs)

        headers = ('contact', 'updated_date', 'count_attempt', 'completion_count_attempt',
                   'status', 'disposition', 'collected_data', )  # 'agent',

        list_val = []
        for i in subscriber_list:
            updated_date = i.updated_date
            if format_type == Export_choice.JSON or Export_choice.XLS:
                updated_date = str(i.updated_date)

            list_val.append((
                i.contact.contact,
                updated_date,
                i.count_attempt,
                i.completion_count_attempt,
                get_subscriber_status(i.status),
                get_subscriber_disposition(i.campaign_id, i.disposition),
                i.collected_data,
                # i.agent,
            ))

        data = tablib.Dataset(*list_val, headers=headers)

        if format_type == Export_choice.XLS:
            response.write(data.xls)
        elif format_type == Export_choice.CSV:
            response.write(data.csv)
        elif format_type == Export_choice.JSON:
            response.write(data.json)

    return response
