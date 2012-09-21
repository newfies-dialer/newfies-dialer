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
from django.http import HttpResponseRedirect, HttpResponse, \
    Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.db.models import Q
from django.db.models import Count
from frontend.views import notice_count
from dialer_contact.models import Phonebook, Contact
from dialer_contact.forms import ContactSearchForm, Contact_fileImport, \
    PhonebookForm, ContactForm
from dialer_campaign.function_def import check_dialer_setting,\
    dialer_setting_limit, \
    contact_search_common_fun,\
    user_dialer_setting_msg
from dialer_campaign.views import common_send_notification
from common.common_functions import striplist, current_view
from utils.helper import grid_common_function, get_grid_update_delete_link,\
    update_style, delete_style
import urllib
import csv
import ast


def get_phonebook_link(request, row_id, link_style, title, action):
    """Function to check user permission to change or delete phonebook

        ``request`` - to check request.user.has_perm() attribute
        ``row_id`` - to pass record id in link
        ``link_style`` - update / delete link style
        ``title`` - alternate name of link
        ``action`` - link to update or delete
    """
    link = ''
    if action == 'update'\
            and request.user.has_perm('dialer_contact.change_phonebook'):
        link = '<a href="' + str(row_id) + '/" class="icon" '\
               + link_style + ' title="' + title + '">&nbsp;</a>'

    if action == 'delete'\
            and request.user.has_perm('dialer_contact.delete_phonebook'):
        link = '<a href="del/' + str(row_id) + '/" class="icon" ' + \
               link_style + ' onClick="return get_alert_msg_for_phonebook('\
               + str(row_id) + ');" title="' + title + '">&nbsp;</a>'
    return link


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
                  get_phonebook_link(request, row['id'], update_style,
                                     _('Update phonebook'), 'update') +
                  get_phonebook_link(request, row['id'], delete_style,
                                     _('Delete phonebook'), 'delete'),
                  ]} for row in phonebook_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@permission_required('dialer_contact.view_phonebook', login_url='/')
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
    request.session['error_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('dialer_contact.add_phonebook', login_url='/')
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
    contact_list = Contact.objects.filter(user=request.user)\
        .extra(where=['phonebook_id IN (%s)'
                      % request.GET['pb_ids']])
    data = contact_list.count()
    return HttpResponse(data)


@permission_required('dialer_contact.delete_phonebook', login_url='/')
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
    if int(object_id) != 0:
        # When object_id is not 0
        phonebook = get_object_or_404(
            Phonebook, pk=object_id, user=request.user)

        # 1) delete all contacts belonging to a phonebook
        contact_list = Contact.objects.filter(phonebook=phonebook)
        contact_list.delete()

        # 2) delete phonebook
        request.session["msg"] = _('"%(name)s" is deleted.')\
            % {'name': phonebook.name}
        phonebook.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        try:
            # 1) delete all contacts belonging to a phonebook
            contact_list = Contact.objects\
                .filter(phonebook__user=request.user)\
                .extra(where=['phonebook_id IN (%s)'
                              % values])
            if contact_list:
                contact_list.delete()

            # 2) delete phonebook
            phonebook_list = Phonebook.objects\
                .filter(user=request.user)\
                .extra(where=['id IN (%s)' % values])
            if phonebook_list:
                request.session["msg"] =\
                    _('%(count)s phonebook(s) are deleted.')\
                    % {'count': phonebook_list.count()}
                phonebook_list.delete()
        except:
            raise Http404

    return HttpResponseRedirect('/phonebook/')


@permission_required('dialer_contact.change_phonebook', login_url='/')
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
    phonebook = get_object_or_404(Phonebook, pk=object_id, user=request.user)
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
                  get_grid_update_delete_link(request, row['id'],
                                              'dialer_contact.change_contact',
                                              _('Update contact'), 'update') +
                  get_grid_update_delete_link(request, row['id'],
                                              'dialer_contact.delete_contact',
                                              _('Delete contact'), 'delete'),
                  ]} for row in contact_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@permission_required('dialer_contact.view_contact', login_url='/')
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
    request.session['error_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('dialer_contact.add_contact', login_url='/')
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


@permission_required('dialer_contact.delete_contact', login_url='/')
@login_required
def contact_del(request, object_id):
    """Delete contact for the logged in user

    **Attributes**:

        * ``object_id`` - Selected contact object
        * ``object_list`` - Selected contact objects

    **Logic Description**:

        * Delete selected contact from the contact list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        contact = get_object_or_404(Contact,
                                    pk=object_id,
                                    phonebook__user=request.user)

        # Delete contact
        request.session["msg"] = _('"%(name)s" is deleted.')\
            % {'name': contact.first_name}
        contact.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        try:
            #TODO : checked with filter(phonebook__user=request.user) but not working
            contact_list = Contact.objects.extra(where=['id IN (%s)' % values])
            if contact_list:
                request.session["msg"] =\
                    _('%(count)s contact(s) are deleted.')\
                    % {'count': contact_list.count()}
                contact_list.delete()
        except:
            raise Http404
    return HttpResponseRedirect('/contact/')


@permission_required('dialer_contact.change_contact', login_url='/')
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
    contact = get_object_or_404(Contact, pk=object_id,
                                phonebook__user=request.user)
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
    contact_cnt = 0
    err_contact_cnt = 0
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
            #Get Phonebook Obj
            phonebook = get_object_or_404(
                Phonebook, pk=request.POST['phonebook'],
                user=request.user)
            # Read each Row
            for row in rdr:
                row = striplist(row)
                if not row or str(row[0]) == 0:
                    continue
                # check field type
                if not int(row[5]):
                    error_msg = _("Invalid value for import! Please check the import samples or phonebook is not valid")
                    type_error_import_list.append(row)
                    break
                #Create new Contact if errors add into a list to display to the user
                try:
                    Contact.objects.create(
                        phonebook=phonebook,
                        contact=row[0],
                        last_name=row[1],
                        first_name=row[2],
                        email=row[3],
                        description=row[4],
                        status=int(row[5]),
                        additional_vars=row[6])

                    contact_cnt = contact_cnt + 1
                    if contact_cnt < 100:
                        success_import_list.append(row)
                except:
                    err_contact_cnt = err_contact_cnt + 1
                    if err_contact_cnt < 100:
                        error_import_list.append(row)

    #check if get any errors during the import
    if err_contact_cnt > 0:
        error_msg = _('%(err_contact_cnt)s Contact(s) already exists!') \
            % {'err_contact_cnt': err_contact_cnt}

    #check if there is contact imported
    if contact_cnt > 0:
        msg = _('%(contact_cnt)s Contact(s) are uploaded successfully out of %(total_rows)s row(s) !!') \
            % {'contact_cnt': contact_cnt,
               'total_rows': total_rows}

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
