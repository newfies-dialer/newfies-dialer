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
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from dnc.models import DNC, DNCContact
from dnc.forms import DNCListForm, DNCContactSearchForm, DNCContactForm,\
    DNCContact_fileImport, DNCContact_fileExport
from dnc.constants import DNC_COLUMN_NAME, DNC_CONTACT_COLUMN_NAME
from django_lets_go.common_functions import get_pagination_vars, striplist, source_desti_field_chk,\
    getvar
from mod_utils.helper import Export_choice
import tablib
import csv

dnc_list_redirect_url = '/module/dnc_list/'
dnc_contact_redirect_url = '/module/dnc_contact/'


@permission_required('dnc.view_dnc', login_url='/')
@login_required
def dnc_list(request):
    """DNC list for the logged in user

    **Attributes**:

        * ``template`` - dnc/dnc_list/list.html

    **Logic Description**:

        * List all dnc which belong to the logged in user.
    """
    sort_col_field_list = ['id', 'name', 'updated_date']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    dnc_list = DNC.objects.filter(user=request.user).order_by(pag_vars['sort_order'])
    data = {
        'msg': request.session.get('msg'),
        'dnc_list': dnc_list,
        'total_dnc': dnc_list.count(),
        'DNC_COLUMN_NAME': DNC_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('dnc/dnc_list/list.html', data, context_instance=RequestContext(request))


@permission_required('dnc.add_dnc', login_url='/')
@login_required
def dnc_add(request):
    """Add new DNC for the logged in user

    **Attributes**:

        * ``form`` - DNCListForm
        * ``template`` - dnc/dnc_list/change.html

    **Logic Description**:

        * Add a new DNC which will belong to the logged in user
          via the DNCListForm & get redirected to the dnc list
    """
    form = DNCListForm(request.POST or None)
    if form.is_valid():
        form.save(user=request.user)
        request.session["msg"] = _('"%(name)s" added.') % {'name': request.POST['name']}
        return HttpResponseRedirect(dnc_list_redirect_url)
    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('dnc/dnc_list/change.html', data, context_instance=RequestContext(request))


@login_required
def get_dnc_contact_count(request):
    """To get total no of dnc contacts belonging to a dnc list"""
    values = request.GET.getlist('ids')
    values = ", ".join(["%s" % el for el in values])
    contact_count = DNCContact.objects.filter(dnc__user=request.user).extra(where=['dnc_id IN (%s)' % values]).count()
    return HttpResponse(contact_count)


@permission_required('dnc.delete_dnc', login_url='/')
@login_required
def dnc_del(request, object_id):
    """Delete a DNC for a logged in user

    **Attributes**:

        * ``object_id`` - Selected DNC object
        * ``object_list`` - Selected DNC objects

    **Logic Description**:

        * Delete contacts from a contact list belonging to a DNC list.
        * Delete the selected the selected DNC list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        dnc = get_object_or_404(DNC, pk=object_id, user=request.user)

        # 1) delete all contacts belonging to a dnc
        dnc_contact_list = DNCContact.objects.filter(dnc=dnc)
        dnc_contact_list.delete()

        # 2) delete dnc
        request.session["msg"] = _('"%(name)s" is deleted.') % {'name': dnc.name}
        dnc.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        try:
            # 1) delete all dnc contacts belonging to a dnc list
            dnc_contact_list = DNCContact.objects.filter(dnc__user=request.user)\
                .extra(where=['dnc_id IN (%s)' % values])
            if dnc_contact_list:
                dnc_contact_list.delete()

            # 2) delete dnc
            dnc_list = DNC.objects.filter(user=request.user).extra(where=['id IN (%s)' % values])
            if dnc_list:
                request.session["msg"] = _('%(count)s DNC list(s) are deleted.') % {'count': dnc_list.count()}
                dnc_list.delete()
        except:
            raise Http404

    return HttpResponseRedirect(dnc_list_redirect_url)


@permission_required('dnc.change_dnc', login_url='/')
@login_required
def dnc_change(request, object_id):
    """Update/Delete DNC for the logged in user

    **Attributes**:

        * ``object_id`` - Selected dnc object
        * ``form`` - DNCListForm
        * ``template`` - dnc/dnc_list/change.html

    **Logic Description**:

        * Update/delete selected dnc from the dnc list
          via DNCListForm & get redirected to dnc list
    """
    dnc = get_object_or_404(DNC, pk=object_id, user=request.user)
    form = DNCListForm(request.POST or None, instance=dnc)
    if form.is_valid():
        if request.POST.get('delete'):
            dnc_del(request, object_id)
            return HttpResponseRedirect(dnc_list_redirect_url)
        else:
            form.save()
            request.session["msg"] = _('"%(name)s" is updated.') % {'name': request.POST['name']}
            return HttpResponseRedirect(dnc_list_redirect_url)
    data = {
        'form': form,
        'action': 'update',
    }
    return render_to_response('dnc/dnc_list/change.html', data, context_instance=RequestContext(request))


@permission_required('dnc.view_dnc_contact', login_url='/')
@login_required
def dnc_contact_list(request):
    """DNC Contact list for the logged in user

    **Attributes**:

        * ``template`` - dnc/dnc_contact/list.html
        * ``form`` - ContactSearchForm

    **Logic Description**:

        * List all dnc contacts from dnc lists belonging to the logged in user
    """
    sort_col_field_list = ['id', 'dnc', 'phone_number', 'updated_date']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    form = DNCContactSearchForm(request.user, request.POST or None)
    dnc_id_list = DNC.objects.values_list('id', flat=True).filter(user=request.user)
    phone_number = ''
    dnc = ''
    post_var_with_page = 0
    if form.is_valid():
        request.session['session_phone_number'] = ''
        request.session['session_dnc'] = ''
        post_var_with_page = 1
        phone_number = getvar(request, 'phone_number', setsession=True)
        dnc = getvar(request, 'dnc', setsession=True)

    if request.GET.get('page') or request.GET.get('sort_by'):
        post_var_with_page = 1
        phone_number = request.session.get('session_phone_number')
        dnc = request.session.get('session_dnc')
        form = DNCContactSearchForm(request.user, initial={'phone_number': phone_number, 'dnc': dnc})

    if post_var_with_page == 0:
        # default
        # unset session var
        request.session['session_phone_number'] = ''
        request.session['session_dnc'] = ''

    kwargs = {'dnc__in': dnc_id_list}
    if dnc and dnc != '0':
        kwargs['dnc_id'] = dnc

    phone_number_type = '1'
    phone_number = source_desti_field_chk(phone_number, phone_number_type, 'phone_number')
    for i in phone_number:
        kwargs[i] = phone_number[i]

    phone_number_list = []
    all_phone_number_list = []
    phone_number_count = 0

    if dnc_id_list:
        all_phone_number_list = DNCContact.objects.values(
            'id', 'dnc__name', 'phone_number', 'updated_date').filter(**kwargs).order_by(pag_vars['sort_order'])

        phone_number_list = all_phone_number_list[pag_vars['start_page']:pag_vars['end_page']]
        phone_number_count = all_phone_number_list.count()

    data = {
        'phone_number_list': phone_number_list,
        'all_phone_number_list': all_phone_number_list,
        'total_phone_numbers': phone_number_count,
        'DNC_CONTACT_COLUMN_NAME': DNC_CONTACT_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
        'msg': request.session.get('msg'),
        'error_msg': request.session.get('error_msg'),
        'form': form,
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('dnc/dnc_contact/list.html', data, context_instance=RequestContext(request))


@permission_required('dnc.add_dnccontact', login_url='/')
@login_required
def dnc_contact_add(request):
    """Add a new dnc contact into the selected dnc for the logged in user

    **Attributes**:

        * ``form`` - DNCContactForm
        * ``template`` - dnc/dnc_contact/change.html

    **Logic Description**:

        * Add new dnc contact belonging to the logged in user
          via DNCContactForm & get redirected to the contact list
    """
    form = DNCContactForm(request.user, request.POST or None)
    # Add dnc contact
    if form.is_valid():
        form.save()
        request.session["msg"] = _('"%(name)s" added.') % {'name': request.POST['phone_number']}
        return HttpResponseRedirect(dnc_contact_redirect_url)
    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('dnc/dnc_contact/change.html', data, context_instance=RequestContext(request))


@permission_required('dnc.delete_dnccontact', login_url='/')
@login_required
def dnc_contact_del(request, object_id):
    """Delete dnc contact for the logged in user

    **Attributes**:

        * ``object_id`` - Selected dnc contact object
        * ``object_list`` - Selected dnc contact objects

    **Logic Description**:

        * Delete selected dnc contact from the dnc contact list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        dnc_contact = get_object_or_404(DNCContact, pk=object_id, dnc__user=request.user)

        # Delete dnc contact
        request.session["msg"] = _('"%(name)s" is deleted.') % {'name': dnc_contact.phone_number}
        dnc_contact.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        try:
            dnc_contact_list = DNCContact.objects.extra(where=['id IN (%s)' % values])
            if dnc_contact_list:
                request.session["msg"] = _('%(count)s contact(s) are deleted.') % {'count': dnc_contact_list.count()}
                dnc_contact_list.delete()
        except:
            raise Http404
    return HttpResponseRedirect(dnc_contact_redirect_url)


@permission_required('dnc.change_dnccontact', login_url='/')
@login_required
def dnc_contact_change(request, object_id):
    """Update/Delete dnc contact for the logged in user

    **Attributes**:

        * ``object_id`` - Selected dnc contact object
        * ``form`` - DNCContactForm
        * ``template`` - dnc/dnc_contact/change.html

    **Logic Description**:

        * Update/delete selected dnc contact from the dnc contact list
          via DNCContactForm & get redirected to the dnc contact list
    """
    dnc_contact = get_object_or_404(DNCContact, pk=object_id, dnc__user=request.user)
    form = DNCContactForm(request.user, request.POST or None, instance=dnc_contact)
    if form.is_valid():
        # Delete dnc contact
        if request.POST.get('delete'):
            dnc_contact_del(request, object_id)
            return HttpResponseRedirect(dnc_contact_redirect_url)
        else:
            # Update dnc contact
            form.save()
            request.session["msg"] = _('"%(name)s" is updated.') % {'name': request.POST['phone_number']}
            return HttpResponseRedirect(dnc_contact_redirect_url)

    data = {
        'form': form,
        'action': 'update',
    }
    return render_to_response('dnc/dnc_contact/change.html', data, context_instance=RequestContext(request))


@login_required
def dnc_contact_import(request):
    """Import CSV file of DNC Contacts for the logged in user

    **Attributes**:

        * ``form`` - DNCContact_fileImport
        * ``template`` - dnc/dnc_contact/import_contact.html

    **Logic Description**:

        * Add new dnc contacts which will belong to the logged in user
          via csv file & get the result (upload success and failure
          statistics)

    **Important variable**:

        * total_rows - Total no. of records in the CSV file
        * retail_record_count - No. of records imported from the CSV file
    """
    form = DNCContact_fileImport(request.user, request.POST or None, request.FILES or None)
    csv_data = ''
    msg = ''
    error_msg = ''
    success_import_list = []
    type_error_import_list = []
    contact_cnt = 0
    dup_contact_cnt = 0
    bulk_record = []

    if form.is_valid():
        # col_no - field name
        #  0     - contact
        # To count total rows of CSV file
        # Get DNC Obj
        dnc = get_object_or_404(DNC, pk=request.POST['dnc_list'], user=request.user)

        records = csv.reader(request.FILES['csv_file'])
        total_rows = len(list(records))
        BULK_SIZE = 1000
        csv_data = csv.reader(request.FILES['csv_file'])

        # Read each Row
        for row in csv_data:
            row = striplist(row)
            if not row or str(row[0]) == 0:
                continue

            # Check field type
            try:
                int(row[0])
            except ValueError:
                error_msg = _("Some of the imported data was invalid!")
                type_error_import_list.append(row)
                continue

            bulk_record.append(
                DNCContact(
                    dnc_id=dnc.id,
                    phone_number=row[0])
            )
            contact_cnt = contact_cnt + 1
            if contact_cnt < 100:
                # We want to display only 100 lines of the success import
                success_import_list.append(row)

            if contact_cnt % BULK_SIZE == 0:
                # Bulk insert
                DNCContact.objects.bulk_create(bulk_record)
                bulk_record = []

        if bulk_record:
            # Remaining record
            DNCContact.objects.bulk_create(bulk_record)
            bulk_record = []

    # check if there is contact imported
    if contact_cnt > 0:
        msg = _('%(contact_cnt)s DNC contact(s) have been uploaded successfully out of %(total_rows)s row(s)!') \
            % {'contact_cnt': contact_cnt,
               'total_rows': total_rows}

    if dup_contact_cnt > 0:
        error_msg = _('Duplicate DNC contact(s) %(dup_contact_cnt)s are not inserted!!') \
            % {'dup_contact_cnt': dup_contact_cnt}

    data = {
        'form': form,
        'msg': msg,
        'error_msg': error_msg,
        'success_import_list': success_import_list,
        'type_error_import_list': type_error_import_list,
    }
    return render_to_response('dnc/dnc_contact/import_dnc_contact.html', data, context_instance=RequestContext(request))


@login_required
def dnc_contact_export(request):
    """Export CSV file of DNC contact"""
    format_type = request.GET['format']
    dnc_list_id = ''
    if request.GET.get('dnc_list_id'):
        dnc_list_id = request.GET.get('dnc_list_id')

    # get the response object, this can be used as a stream.
    response = HttpResponse(content_type='text/%s' % format_type)
    # force download.
    response['Content-Disposition'] = 'attachment;filename=export.%s' % format_type

    headers = ('phone_number',)

    if dnc_list_id:
        dnc_contact = DNCContact.objects.filter(dnc_id=dnc_list_id)
    else:
        dnc_contact = DNCContact.objects.filter(dnc__user=request.user)

    list_val = []
    for i in dnc_contact:
        list_val.append((i.phone_number,))

    data = tablib.Dataset(*list_val, headers=headers)

    if format_type == Export_choice.XLS:
        response.write(data.xls)
    elif format_type == Export_choice.CSV:
        response.write(data.csv)
    elif format_type == Export_choice.JSON:
        response.write(data.json)

    return response


@login_required
def dnc_contact_export_view(request):
    """Export CSV file of dnc contact form view

    **Attributes**:

        * ``form`` - DNCContact_fileExport
        * ``template`` - dnc/dnc_contact/export_dnc_contact.html

    **Logic Description**:

        * DNC contacts export form will be redirected to ``/dnc_contact/export/`` view
          with format & dnc_list_id parameters
    """
    form = DNCContact_fileExport(request.user, request.POST or None, initial={'export_to': Export_choice.CSV})
    if form.is_valid():
        dnc_list_id = request.POST['dnc_list']
        export_to = request.POST['export_to']
        return HttpResponseRedirect(dnc_contact_redirect_url + 'export/?format=' + export_to + '&dnc_list_id=' + dnc_list_id)

    template = 'dnc/dnc_contact/export_dnc_contact.html'
    data = {
        'form': form,
        'action': 'update',
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))
