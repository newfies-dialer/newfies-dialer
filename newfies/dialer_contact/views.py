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
from django.contrib.auth.decorators import login_required, \
    permission_required
from django.http import HttpResponseRedirect, HttpResponse, \
    Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.db.models import Count
from dialer_contact.models import Phonebook, Contact
from dialer_contact.forms import ContactSearchForm, Contact_fileImport, \
    PhonebookForm, ContactForm
from dialer_contact.constants import PHONEBOOK_COLUMN_NAME, CONTACT_COLUMN_NAME
from dialer_contact.constants import STATUS_CHOICE
from dialer_campaign.function_def import check_dialer_setting,\
    dialer_setting_limit, user_dialer_setting_msg, type_field_chk
from user_profile.constants import NOTIFICATION_NAME
from frontend_notification.views import frontend_send_notification
from common.common_functions import striplist, getvar,\
    get_pagination_vars, unset_session_var
import csv
import json


@permission_required('dialer_contact.view_phonebook', login_url='/')
@login_required
def phonebook_list(request):
    """Phonebook list for the logged in user

    **Attributes**:

        * ``template`` - frontend/phonebook/list.html

    **Logic Description**:

        * List all phonebooks which belong to the logged in user.
    """
    sort_col_field_list = ['id', 'name', 'updated_date']
    default_sort_field = 'id'
    pagination_data = \
        get_pagination_vars(request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']

    phonebook_list = Phonebook.objects\
        .annotate(contact_count=Count('contact'))\
        .filter(user=request.user).order_by(sort_order)

    template = 'frontend/phonebook/list.html'
    data = {
        'msg': request.session.get('msg'),
        'phonebook_list': phonebook_list,
        'total_phonebook': phonebook_list.count(),
        'PAGE_SIZE': PAGE_SIZE,
        'PHONEBOOK_COLUMN_NAME': PHONEBOOK_COLUMN_NAME,
        'col_name_with_order': pagination_data['col_name_with_order'],
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
            obj.user = request.user
            obj.save()
            request.session["msg"] = _('"%(name)s" added.') %\
                {'name': request.POST['name']}
            return HttpResponseRedirect('/phonebook/')
    template = 'frontend/phonebook/change.html'
    data = {
        'form': form,
        'action': 'add',
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@login_required
def get_contact_count(request):
    """To get total no of contacts belonging to a phonebook list"""
    values = request.GET.getlist('ids')
    values = ", ".join(["%s" % el for el in values])
    contact_count = Contact.objects.filter(phonebook__user=request.user)\
        .extra(where=['phonebook_id IN (%s)' % values]).count()

    return HttpResponse(contact_count)


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
                .extra(where=['phonebook_id IN (%s)' % values])
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
            return HttpResponseRedirect('/phonebook/del/%s/' % object_id)
        else:
            form = PhonebookForm(request.POST, instance=phonebook)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%(name)s" is updated.') \
                    % {'name': request.POST['name']}
                return HttpResponseRedirect('/phonebook/')

    template = 'frontend/phonebook/change.html'
    data = {
        'form': form,
        'action': 'update',
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


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
    sort_col_field_list = ['id', 'phonebook', 'contact', 'status',
                           'first_name', 'last_name', 'email',
                           'updated_date']
    default_sort_field = 'id'
    pagination_data = get_pagination_vars(
        request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']
    start_page = pagination_data['start_page']
    end_page = pagination_data['end_page']

    form = ContactSearchForm(request.user)
    phonebook_id_list = Phonebook.objects.values_list('id', flat=True)\
        .filter(user=request.user)
    search_tag = 1
    contact_no = ''
    contact_name = ''
    phonebook = ''
    contact_status = STATUS_CHOICE.ALL
    if request.method == 'POST':
        form = ContactSearchForm(request.user, request.POST)
        if form.is_valid():
            field_list = ['contact_no', 'contact_name',
                          'contact_status', 'phonebook']
            unset_session_var(request, field_list)

            contact_no = getvar(request, 'contact_no', setsession=True)
            contact_name = getvar(request, 'contact_name', setsession=True)
            contact_status = getvar(request, 'contact_status', setsession=True)
            phonebook = getvar(request, 'phonebook', setsession=True)

    post_var_with_page = 0
    try:
        if request.GET.get('page') or request.GET.get('sort_by'):
            post_var_with_page = 1
            contact_no = request.session.get('session_contact_no')
            contact_name = request.session.get('session_contact_name')
            contact_status = request.session.get('session_contact_status')
            phonebook = request.session.get('session_phonebook')
            form = ContactSearchForm(request.user, initial={'contact_no': contact_no,
                                                            'contact_name': contact_name,
                                                            'status': contact_status,
                                                            'phonebook': phonebook})
        else:
            post_var_with_page = 1
            if request.method == 'GET':
                post_var_with_page = 0
    except:
        pass

    if post_var_with_page == 0:
        # default
        # unset session var
        field_list = ['contact_no', 'contact_name',
                      'contact_status', 'phonebook']
        unset_session_var(request, field_list)

    kwargs = {}
    if phonebook and phonebook != '0':
        kwargs['phonebook'] = phonebook

    if contact_status and int(contact_status) != STATUS_CHOICE.ALL:
        kwargs['status'] = contact_status

    contact_no_type = '1'
    contact_no = type_field_chk(contact_no, contact_no_type, 'contact')
    for i in contact_no:
        kwargs[i] = contact_no[i]

    contact_list = []
    all_contact_list = []
    contact_count = 0

    if phonebook_id_list:
        contact_list = Contact.objects.values('id', 'phonebook__name', 'contact',
            'last_name', 'first_name', 'email', 'status', 'updated_date')\
            .filter(phonebook__in=phonebook_id_list)

        if kwargs:
            contact_list = contact_list.filter(**kwargs)

        if contact_name:
            # Search on contact name
            q = (Q(last_name__icontains=contact_name) |
                 Q(first_name__icontains=contact_name))
            if q:
                contact_list = contact_list.filter(q)

        all_contact_list = contact_list.order_by(sort_order)
        contact_list = all_contact_list[start_page:end_page]
        contact_count = all_contact_list.count()

    template = 'frontend/contact/list.html'
    data = {
        'contact_list': contact_list,
        'all_contact_list': all_contact_list,
        'total_contacts': contact_count,
        'PAGE_SIZE': PAGE_SIZE,
        'CONTACT_COLUMN_NAME': CONTACT_COLUMN_NAME,
        'col_name_with_order': pagination_data['col_name_with_order'],
        'msg': request.session.get('msg'),
        'error_msg': request.session.get('error_msg'),
        'form': form,
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
        'search_tag': search_tag,
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
        if check_dialer_setting(request, check_for="contact"):
            request.session['msg'] = \
                _("you have too many contacts. you are allowed a maximum of %(limit)s") % \
                {'limit': dialer_setting_limit(request, limit_for="contact")}

            # contact limit reached
            frontend_send_notification(request, NOTIFICATION_NAME.contact_limit_reached)
            return HttpResponseRedirect("/contact/")

    form = ContactForm(request.user)
    error_msg = False
    # Add contact
    if request.method == 'POST':
        form = ContactForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            request.session["msg"] = _('"%s" is added.') % request.POST['contact']
            return HttpResponseRedirect('/contact/')
        else:
            if len(request.POST['contact']) > 0:
                error_msg = _('"%s" cannot be added.') % request.POST['contact']

    phonebook_count = Phonebook.objects.filter(user=request.user).count()
    template = 'frontend/contact/change.html'
    data = {
        'form': form,
        'action': 'add',
        'error_msg': error_msg,
        'phonebook_count': phonebook_count,
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
        contact = get_object_or_404(
            Contact, pk=object_id, phonebook__user=request.user)

        # Delete contact
        request.session["msg"] = _('"%s" is deleted.') % contact.contact
        contact.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        try:
            contact_list = Contact.objects.extra(where=['id IN (%s)' % values])
            if contact_list:
                request.session["msg"] =\
                    _('%s contact(s) are deleted.') % contact_list.count()
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
    contact = get_object_or_404(
        Contact, pk=object_id, phonebook__user=request.user)

    form = ContactForm(request.user, instance=contact)
    if request.method == 'POST':
        # Delete contact
        if request.POST.get('delete'):
            return HttpResponseRedirect('/contact/del/%s/' % object_id)
        else:
            # Update contact
            form = ContactForm(request.user, request.POST, instance=contact)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%s" is updated.') % request.POST['contact']
                return HttpResponseRedirect('/contact/')

    template = 'frontend/contact/change.html'
    data = {
        'form': form,
        'action': 'update',
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
        # check  Max Number of contacts
        if check_dialer_setting(request, check_for="contact"):
            request.session['msg'] = \
                _("you have too many contacts. you are allowed a maximum of %(limit)s") % \
                {'limit': dialer_setting_limit(request, limit_for="contact")}

            # contact limit reached
            frontend_send_notification(request, NOTIFICATION_NAME.contact_limit_reached)
            return HttpResponseRedirect("/contact/")

    form = Contact_fileImport(request.user)
    csv_data = ''
    msg = ''
    error_msg = ''
    success_import_list = []
    type_error_import_list = []
    contact_cnt = 0
    bulk_record = []
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
            #  6     - address
            #  7     - city
            #  8     - country
            #  9     - country
            # 10     - unit_number
            # 11     - additional_vars
            # To count total rows of CSV file
            records = csv.reader(request.FILES['csv_file'],
                                 delimiter='|', quotechar='"')
            total_rows = len(list(records))
            BULK_SIZE = 1000
            csv_data = csv.reader(request.FILES['csv_file'],
                             delimiter='|', quotechar='"')
            #Get Phonebook Obj
            phonebook = get_object_or_404(
                Phonebook, pk=request.POST['phonebook'],
                user=request.user)
            #Read each Row
            for row in csv_data:
                row = striplist(row)
                if not row or str(row[0]) == 0:
                    continue

                #Check field type
                if not int(row[5]):
                    error_msg = _("invalid value for import! please check the import samples or phonebook is not valid")
                    type_error_import_list.append(row)
                    break

                if len(row[9]) > 2:
                    error_msg = _("invalid value for country code, it needs to be a valid ISO 3166-1 alpha-2 codes (http://en.wikipedia.org/wiki/ISO_3166-1)")
                    type_error_import_list.append(row)
                    break

                row_11 = ''
                if row[11]:
                    try:
                        row_11 = json.loads(row[11])
                    except:
                        row_11 = ''

                bulk_record.append(
                    Contact(
                        phonebook=phonebook,
                        contact=row[0],
                        last_name=row[1],
                        first_name=row[2],
                        email=row[3],
                        description=row[4],
                        status=int(row[5]),
                        address=row[6],
                        city=row[7],
                        state=row[8],
                        country=row[9],  # Note: country needs to be a country code (CA, ES)
                        unit_number=row[10],
                        additional_vars=row_11)
                )

                contact_cnt = contact_cnt + 1

                if contact_cnt < 100:
                    #We want to display only 100 lines of the success import
                    success_import_list.append(row)

                if contact_cnt % BULK_SIZE == 0:
                    #Bulk insert
                    Contact.objects.bulk_create(bulk_record)
                    bulk_record = []

            # remaining record
            Contact.objects.bulk_create(bulk_record)
            bulk_record = []

    #check if there is contact imported
    if contact_cnt > 0:
        msg = _('%(contact_cnt)s contact(s) have been uploaded successfully out of %(total_rows)s row(s)!') \
            % {'contact_cnt': contact_cnt,
               'total_rows': total_rows}

    data = RequestContext(request, {
                          'form': form,
                          'csv_data': csv_data,
                          'msg': msg,
                          'error_msg': error_msg,
                          'success_import_list': success_import_list,
                          'type_error_import_list': type_error_import_list,
                          'dialer_setting_msg': user_dialer_setting_msg(request.user),
                          })
    template = 'frontend/contact/import_contact.html'
    return render_to_response(template, data,
                              context_instance=RequestContext(request))
