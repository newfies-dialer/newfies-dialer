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
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_reset, password_reset_done,\
                        password_reset_confirm, password_reset_complete
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.db.models import Sum, Avg, Count
from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.conf import settings
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from notification import models as notification
from dialer_campaign.models import Phonebook, Contact, Campaign, \
                        CampaignSubscriber
from dialer_campaign.forms import ContactSearchForm, Contact_fileImport, \
                        LoginForm, PhonebookForm, ContactForm, CampaignForm, \
                        DashboardForm
from dialer_campaign.function_def import user_attached_with_dialer_settings, \
                        check_dialer_setting, dialer_setting_limit, \
                        contact_search_common_fun,\
                        calculate_date, date_range, \
                        get_campaign_status_name, user_dialer_setting_msg
from dialer_campaign.tasks import collect_subscriber
from dialer_cdr.models import VoIPCall
from common.common_functions import variable_value, striplist, current_view
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
import urllib
import time
import csv
import ast
import re
from frontend.views import notice_count


update_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/page_edit.png);"'
delete_style = 'style="text-decoration:none;background-image:url(' + \
                settings.STATIC_URL + 'newfies/icons/delete.png);"'



def cust_password_reset(request):
    """Use ``django.contrib.auth.views.password_reset`` view method for
    forgotten password on the Customer UI

    This method sends an e-mail to the user's email-id which is entered in
    ``password_reset_form``
    """
    if not request.user.is_authenticated():
        data = {'loginform': LoginForm()}
        return password_reset(request,
        template_name='frontend/registration/password_reset_form.html',
        email_template_name='frontend/registration/password_reset_email.html',
        post_reset_redirect='/password_reset/done/',
        from_email='newfies_admin@localhost.com',
        extra_context=data)
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_done(request):
    """Use ``django.contrib.auth.views.password_reset_done`` view method for
    forgotten password on the Customer UI

    This will show a message to the user who is seeking to reset their
    password.
    """
    if not request.user.is_authenticated():
        data = {'loginform': LoginForm()}
        return password_reset_done(request,
        template_name='frontend/registration/password_reset_done.html',
        extra_context=data)
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_confirm(request, uidb36=None, token=None):
    """Use ``django.contrib.auth.views.password_reset_confirm`` view method for
    forgotten password on the Customer UI

    This will allow a user to reset their password.
    """
    if not request.user.is_authenticated():
        data = {'loginform': LoginForm()}
        return password_reset_confirm(request, uidb36=uidb36, token=token,
        template_name='frontend/registration/password_reset_confirm.html',
        post_reset_redirect='/reset/done/',
        extra_context=data)
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_complete(request):
    """Use ``django.contrib.auth.views.password_reset_complete`` view method
    for forgotten password on theCustomer UI

    This shows an acknowledgement to the user after successfully resetting
    their password for the system.
    """
    if not request.user.is_authenticated():
        data = {'loginform': LoginForm()}
        return password_reset_complete(request,
        template_name='frontend/registration/password_reset_complete.html',
        extra_context=data)
    else:
        return HttpResponseRedirect("/")


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


def grid_common_function(request):
    """To get common flexigrid variable"""
    grid_data = {}

    grid_data['page'] = variable_value(request, 'page')
    grid_data['rp'] = variable_value(request, 'rp')
    grid_data['sortname'] = variable_value(request, 'sortname')
    grid_data['sortorder'] = variable_value(request, 'sortorder')
    grid_data['query'] = variable_value(request, 'query')
    grid_data['qtype'] = variable_value(request, 'qtype')

    # page index
    if int(grid_data['page']) > 1:
        grid_data['start_page'] = (int(grid_data['page']) - 1) * \
                                    int(grid_data['rp'])
        grid_data['end_page'] = grid_data['start_page'] + int(grid_data['rp'])
    else:
        grid_data['start_page'] = int(0)
        grid_data['end_page'] = int(grid_data['rp'])

    grid_data['sortorder_sign'] = ''
    if grid_data['sortorder'] == 'desc':
        grid_data['sortorder_sign'] = '-'

    return grid_data


# Phonebook
@login_required
def phonebook_grid(request):
    """Phonebook list in json format for flexigrid.

    **Model**: Phonebook

    **Fields**: [id, name, description, updated_date]
    """
    grid_data = grid_common_function(request)
    page = int(grid_data['page'])
    start_page = int(grid_data['start_page'])
    end_page = int(grid_data['end_page'])
    sortorder_sign = grid_data['sortorder_sign']
    sortname = grid_data['sortname']

    phonebook_list = Phonebook.objects\
                     .values('id', 'name', 'description', 'updated_date')\
                     .annotate(contact_count=Count('contact'))\
                     .filter(user=request.user)

    count = phonebook_list.count()
    phonebook_list = phonebook_list\
                .order_by(sortorder_sign + sortname)[start_page:end_page]

    rows = [
        {'id': row['id'],
        'cell': ['<input type="checkbox" name="select" class="checkbox"\
        value="' + str(row['id']) + '" />',
        row['id'],
        row['name'],
        row['description'],
        row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
        row['contact_count'],
        '<a href="' + str(row['id']) + '/" class="icon" ' \
        + update_style + ' title="' + _('Update phonebook') + '">&nbsp;</a>' +
        '<a href="del/' + str(row['id']) + '/" class="icon" ' \
        + delete_style + ' onClick="return get_alert_msg_for_phonebook(' +
        str(row['id']) +
        ');"  title="' + _('Delete phonebook') + '">&nbsp;</a>']}\
        for row in phonebook_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@login_required
def phonebook_list(request):
    """Phonebook list for the logged in user

    **Attributes**:

        * ``template`` - frontend/phonebook/list.html

    **Logic Description**:

        * List all phonebooks which belong to the logged in user.
    """
    template = 'frontend/phonebook/list.html'
    data = {
        'module': current_view(request),
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def phonebook_add(request):
    """Add new Phonebook for the logged in user

    **Attributes**:

        * ``form`` - PhonebookForm
        * ``template`` - frontend/phonebook/change.html

    **Logic Description**:

        * Add a new phonebook which will belong to the logged in user
          via the phonebookForm & get redirected to the phonebook list
    """
    form = PhonebookForm()
    if request.method == 'POST':
        form = PhonebookForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.save()
            request.session["msg"] = _('"%(name)s" is added.') %\
                {'name': request.POST['name']}
            return HttpResponseRedirect('/phonebook/')
    template = 'frontend/phonebook/change.html'
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
def get_contact_count(request):
    """To get total no of contacts belonging to a phonebook list"""
    contact_list = Contact.objects.extra(where=['phonebook_id IN (%s)'\
                       % request.GET['pb_ids']])
    data = contact_list.count()
    return HttpResponse(data)


@login_required
def phonebook_del(request, object_id):
    """Delete a phonebook for a logged in user

    **Attributes**:

        * ``object_id`` - Selected phonebook object
        * ``object_list`` - Selected phonebook objects

    **Logic Description**:

        * Delete contacts from a contact list belonging to a phonebook list.
        * Delete selected the phonebook from the phonebook list
    """
    try:
        # When object_id is not 0
        phonebook = Phonebook.objects.get(pk=object_id)
        if object_id:
            # 1) delete all contacts belonging to a phonebook
            contact_list = Contact.objects.filter(phonebook=object_id)
            contact_list.delete()

            # 2) delete phonebook
            request.session["msg"] = _('"%(name)s" is deleted.') \
                                        % {'name': phonebook.name}
            phonebook.delete()
            return HttpResponseRedirect('/phonebook/')
    except:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        # 1) delete all contacts belonging to a phonebook
        contact_list = Contact.objects.extra(where=['phonebook_id IN (%s)'\
                       % values])
        contact_list.delete()

        # 2) delete phonebook
        phonebook_list = Phonebook.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] =\
        _('%(count)s phonebook(s) are deleted.') \
        % {'count': phonebook_list.count()}
        phonebook_list.delete()
        return HttpResponseRedirect('/phonebook/')


@login_required
def phonebook_change(request, object_id):
    """Update/Delete Phonebook for the logged in user

    **Attributes**:

        * ``object_id`` - Selected phonebook object
        * ``form`` - PhonebookForm
        * ``template`` - frontend/phonebook/change.html

    **Logic Description**:

        * Update/delete selected phonebook from the phonebook list
          via PhonebookForm & get redirected to phonebook list
    """
    phonebook = Phonebook.objects.get(pk=object_id)
    form = PhonebookForm(instance=phonebook)
    if request.method == 'POST':
        if request.POST.get('delete'):
            phonebook_del(request, object_id)
            return HttpResponseRedirect('/phonebook/')
        else:
            form = PhonebookForm(request.POST, instance=phonebook)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%(name)s" is updated.') \
                    % {'name': request.POST['name']}
                return HttpResponseRedirect('/phonebook/')

    template = 'frontend/phonebook/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'update',
       'notice_count': notice_count(request),
       'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_grid(request):
    """Contact list in json format for flexigrid

    **Model**: Contact

    **Fields**: [id, phonebook__name, contact, last_name, first_name,
                 description, status, additional_vars, updated_date]
    """
    grid_data = grid_common_function(request)
    page = int(grid_data['page'])
    start_page = int(grid_data['start_page'])
    end_page = int(grid_data['end_page'])
    sortorder_sign = grid_data['sortorder_sign']
    sortname = grid_data['sortname']

    kwargs = {}
    name = ''

    # get querystring from URL
    q_arr = list(request.get_full_path().split('?'))
    j = 0
    q_para = ''

    # get para from querystring
    for i in q_arr:
        if j == 1:
            q_para = i
        j = j + 1

    if "kwargs" in q_para:
        # decode query string
        decoded_string = urllib.unquote(q_para.decode("utf8"))
        temp_list = list(decoded_string.split('&'))
        for i in range(0, len(temp_list)):
            if temp_list[i].find('='):
                kwargs_list = list(temp_list[i].split('='))
                if kwargs_list[0] == 'kwargs':
                    kwargs = kwargs_list[1]
                if kwargs_list[0] == 'name':
                    name = kwargs_list[1]

    phonebook_id_list = ''
    phonebook_id_list = Phonebook.objects\
                            .values_list('id', flat=True)\
                            .filter(user=request.user)
    contact_list = []

    if phonebook_id_list:
        select_data = {"status":
                    "(CASE status WHEN 1 THEN 'ACTIVE' ELSE 'INACTIVE' END)"}
        contact_list = Contact.objects\
            .extra(select=select_data)\
            .values('id', 'phonebook__name', 'contact', 'last_name',
                'first_name', 'description', 'status', 'additional_vars',
                'updated_date').filter(phonebook__in=phonebook_id_list)

        if kwargs:
            kwargs = ast.literal_eval(kwargs)
            contact_list = contact_list.filter(**kwargs)

        if name:
            # Search on contact name
            q = (Q(last_name__icontains=name) |
                 Q(first_name__icontains=name))
            if q:
                contact_list = contact_list.filter(q)

    count = contact_list.count()
    contact_list = \
        contact_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    rows = [
        {'id': row['id'],
        'cell': ['<input type="checkbox" name="select" class="checkbox"\
        value="' + str(row['id']) + '" />',
        row['id'], row['phonebook__name'], row['contact'],
        row['last_name'], row['first_name'], row['status'],
        row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
        '<a href="' + str(row['id']) + '/" class="icon" ' \
        + update_style + ' title="' + _('Update contact') + '">&nbsp;</a>' +
        '<a href="del/' + str(row['id']) + '/" class="icon" ' \
        + delete_style + ' onClick="return get_alert_msg(' +
        str(row['id']) +
        ');" title="' + _('Delete contact') + '">&nbsp;</a>']
        } for row in contact_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


# Subscriber
@login_required
def contact_list(request):
    """Contact list for the logged in user

    **Attributes**:

        * ``template`` - frontend/contact/list.html
        * ``form`` - ContactSearchForm

    **Logic Description**:

        * List all contacts from phonebooks belonging to the logged in user
    """
    form = ContactSearchForm(request.user)
    kwargs = {}
    name = ''
    if request.method == 'POST':
        form = ContactSearchForm(request.user, request.POST)
        kwargs = contact_search_common_fun(request)
        if request.POST['name'] != '':
            name = request.POST['name']

    template = 'frontend/contact/list.html'
    data = {
        'module': current_view(request),
        'msg': request.session.get('msg'),
        'error_msg': request.session.get('error_msg'),
        'form': form,
        'user': request.user,
        'kwargs': kwargs,
        'name': name,
        'notice_count': notice_count(request),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_add(request):
    """Add a new contact into the selected phonebook for the logged in user

    **Attributes**:

        * ``form`` - ContactForm
        * ``template`` - frontend/contact/change.html

    **Logic Description**:

        * Before adding a contact, check dialer setting limit if applicable
          to the user.
        * Add new contact belonging to the logged in user
          via ContactForm & get redirected to the contact list
    """
    # Check dialer setting limit
    if request.user and request.method == 'POST':
        # check  Max Number of subscriber per campaign
        if check_dialer_setting(request, check_for="contact"):
            request.session['msg'] = \
                _("You have too many contacts per campaign. You are allowed a maximum of %(limit)s") % \
                {'limit': dialer_setting_limit(request, limit_for="contact")}

            # contact limit reached
            common_send_notification(request, '6')
            return HttpResponseRedirect("/contact/")

    form = ContactForm(request.user)
    error_msg = False
    # Add contact
    if request.method == 'POST':
        form = ContactForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            request.session["msg"] = _('"%(name)s" is added.') %\
                {'name': request.POST['contact']}
            return HttpResponseRedirect('/contact/')
        else:
            if len(request.POST['contact']) > 0:
                error_msg = _('"%(name)s" cannot be added.') %\
                    {'name': request.POST['contact']}

    phonebook_count = Phonebook.objects.filter(user=request.user).count()
    template = 'frontend/contact/change.html'
    data = {
        'module': current_view(request),
        'form': form,
        'action': 'add',
        'error_msg': error_msg,
        'phonebook_count': phonebook_count,
        'notice_count': notice_count(request),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_del(request, object_id):
    """Delete contact for the logged in user

    **Attributes**:

        * ``object_id`` - Selected contact object
        * ``object_list`` - Selected contact objects

    **Logic Description**:

        * Delete selected contact from the contact list
    """
    try:
        # When object_id is not 0
        contact = Contact.objects.get(pk=object_id)
        # Delete phonebook
        if object_id:
            request.session["msg"] = _('"%(name)s" is deleted.') \
                % {'name': contact.first_name}
            contact.delete()
            return HttpResponseRedirect('/contact/')
    except:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        contact_list = Contact.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] =\
            _('%(count)s contact(s) are deleted.') \
                % {'count': contact_list.count()}
        contact_list.delete()
        return HttpResponseRedirect('/contact/')


@login_required
def contact_change(request, object_id):
    """Update/Delete contact for the logged in user

    **Attributes**:

        * ``object_id`` - Selected contact object
        * ``form`` - ContactForm
        * ``template`` - frontend/contact/change.html

    **Logic Description**:

        * Update/delete selected contact from the contact list
          via ContactForm & get redirected to the contact list
    """
    contact = Contact.objects.get(pk=object_id)
    form = ContactForm(request.user, instance=contact)
    if request.method == 'POST':
        # Delete contact
        if request.POST.get('delete'):
            contact_del(request, object_id)
            return HttpResponseRedirect('/contact/')
        else:
            # Update contact
            form = ContactForm(request.user, request.POST,
                               instance=contact)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%(name)s" is updated.') \
                    % {'name': request.POST['contact']}
                return HttpResponseRedirect('/contact/')

    template = 'frontend/contact/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'update',
       'notice_count': notice_count(request),
       'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_import(request):
    """Import CSV file of Contacts for the logged in user

    **Attributes**:

        * ``form`` - Contact_fileImport
        * ``template`` - frontend/contact/import_contact.html

    **Logic Description**:

        * Before adding contacts, check dialer setting limit if applicable
          to the user.
        * Add new contacts which will belong to the logged in user
          via csv file & get the result (upload success and failure
          statistics)

    **Important variable**:

        * total_rows - Total no. of records in the CSV file
        * retail_record_count - No. of records imported from the CSV file
    """
    # Check dialer setting limit
    if request.user and request.method == 'POST':
        # check  Max Number of subscribers per campaign
        if check_dialer_setting(request, check_for="contact"):
            request.session['msg'] = \
                _("You have too many contacts per campaign. You are allowed a maximum of %(limit)s") % \
                {'limit': dialer_setting_limit(request, limit_for="contact")}

            # contact limit reached
            common_send_notification(request, '6')
            return HttpResponseRedirect("/contact/")

    form = Contact_fileImport(request.user)
    rdr = ''  # will contain CSV data
    msg = ''
    error_msg = ''
    success_import_list = []
    error_import_list = []
    type_error_import_list = []
    if request.method == 'POST':
        form = Contact_fileImport(request.user, request.POST, request.FILES)
        if form.is_valid():
            # col_no - field name
            #  0     - contact
            #  1     - last_name
            #  2     - first_name
            #  3     - email
            #  4     - description
            #  5     - status
            #  6     - additional_vars
            # To count total rows of CSV file
            records = csv.reader(request.FILES['csv_file'],
                             delimiter=',', quotechar='"')
            total_rows = len(list(records))

            rdr = csv.reader(request.FILES['csv_file'],
                             delimiter=',', quotechar='"')
            contact_record_count = 0
            # Read each Row
            for row in rdr:
                row = striplist(row)
                if (row and str(row[0]) > 0):
                    try:
                        # check field type
                        int(row[5])
                        phonebook = \
                            Phonebook.objects\
                            .get(pk=request.POST['phonebook'])
                        try:
                            # check if prefix is already
                            # exist with retail plan or not
                            contact = Contact.objects.get(
                                 phonebook_id=phonebook.id,
                                 contact=row[0])
                            error_msg = _('Subscriber already exists!')
                            error_import_list.append(row)
                        except:
                            # if not, insert record
                            Contact.objects.create(
                                  phonebook=phonebook,
                                  contact=row[0],
                                  last_name=row[1],
                                  first_name=row[2],
                                  email=row[3],
                                  description=row[4],
                                  status=int(row[5]),
                                  additional_vars=row[6])
                            contact_record_count = \
                                contact_record_count + 1
                            msg = _('%(contact_record_count)s Contact(s) are uploaded successfully out of %(total_rows)s row(s) !!') \
                                % {'contact_record_count': contact_record_count,
                                   'total_rows': total_rows}

                            success_import_list.append(row)
                    except:
                        error_msg = \
                            _("Invalid value for import! Please check the import samples.")
                        type_error_import_list.append(row)

    data = RequestContext(request, {
    'form': form,
    'rdr': rdr,
    'msg': msg,
    'error_msg': error_msg,
    'success_import_list': success_import_list,
    'error_import_list': error_import_list,
    'type_error_import_list': type_error_import_list,
    'module': current_view(request),
    'notice_count': notice_count(request),
    'dialer_setting_msg': user_dialer_setting_msg(request.user),
    })
    template = 'frontend/contact/import_contact.html'
    return render_to_response(template, data,
           context_instance=RequestContext(request))


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
    from django.db.models import get_model
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
