# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import password_reset, password_reset_done,\
password_reset_confirm, password_reset_complete
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.db.models import *
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.db.models import Q
from notification import models as notification
from dialer_campaign.models import *
from dialer_campaign.forms import *
from dialer_campaign.function_def import *
from inspect import stack, getmodule
from datetime import *
import operator
import urllib
import string
import csv
import ast
import os
from dialer_campaign.tasks import collect_subscriber


def current_view(request):
    name = getmodule(stack()[1][0]).__name__
    return stack()[1][3]


@login_required
def customer_dashboard(request, on_index=None):
    """ Customer dashboard which gives the information like how many campaign
    are running, total of contacts, amount of contact reached today etc.

    **Attributes**:

        * ``template`` - frontend/dashboard.html
    """
    # Active campaign for logged in User
    running_campaign_count = \
    Campaign.objects.filter(user=request.user, status=1).count()
    running_campaign = Campaign.objects.filter(user=request.user, status=1)

    # Contacts count which are active and belong to those phonebook(s) which is
    # associated with running campaign
    campaign_phonebbok_active_contact_count = 0
    for i in running_campaign:
        campaign_phonebbok_active_contact_count +=\
        Contact.objects.filter(phonebook__campaign=i.id, status=1).count()

    # Phonebook list for logged in user
    phonebook_id_list = ''
    phonebook_objs = Phonebook.objects.filter(user=request.user)
    for i in phonebook_objs:
        phonebook_id_list += str(i.id) + ","
    phonebook_id_list = phonebook_id_list[:-1]

    # Total count of contacts for logged in user
    total_of_phonebook_contacts = 0
    if phonebook_id_list:
        total_of_phonebook_contacts = \
        Contact.objects\
        .extra(where=['phonebook_id IN (%s) ' % phonebook_id_list]).count()

    # Total records for graph
    total_record = []

    today = datetime.today()
    start_date = datetime(today.year, today.month, today.day, 0, 0, 0, 0)
    end_date = datetime(today.year, today.month, today.day, 23, 59, 59, 999999)

    # Contacts which are successfully called for running campaign
    reached_contact = 0
    for i in running_campaign:
        campaign_subscriber = CampaignSubscriber.objects\
        .filter(campaign=i.id, status=5,
                updated_date__range=(start_date, end_date)).count()

        total_record.append((i.id, int(campaign_subscriber)))
        reached_contact += campaign_subscriber    


    template = 'frontend/dashboard.html'
    data = {
        'module': current_view(request),
        'running_campaign_count': running_campaign_count,
        'total_of_phonebook_contacts': total_of_phonebook_contacts,
        'campaign_phonebbok_active_contact_count': \
        campaign_phonebbok_active_contact_count,
        'reached_contact': reached_contact,
        'total_record':sorted(total_record, key=lambda total: total[0]),
        'notice_count': notice_count(request),
    }
    if on_index == 'yes':
        return data
    return render_to_response(template, data,
           context_instance=RequestContext(request))


def login_view(request):
    """Check User credentials

    **Attributes**:

        * ``form`` - LoginForm
        * ``template`` - frontend/index.html

    **Logic Description**:

        * Submitted user credentials need to be checked. If it is not valid
          then system will redirect to login page again.
        * Submitted user credentials are valid then system will redirect to
          dashboard page of system.
    """
    template = 'frontend/index.html'
    errorlogin = ''
    if request.method == 'POST':
        try:
            action = request.POST['action']
        except (KeyError):
            action = "login"

        if action == "logout":
            logout(request)
        else:
            loginform = LoginForm(request.POST)
            if loginform.is_valid():
                cd = loginform.cleaned_data
                user = authenticate(username=cd['user'],
                                    password=cd['password'])
                if user is not None:
                    if user.is_active:                        
                        login(request, user)                        
                        # Redirect to a success page (dashboard).
                        return \
                        HttpResponseRedirect('/dashboard/')
                    else:
                        # Return a 'disabled account' error message
                        errorlogin = _('Disabled Account') #True
                else:
                    # Return an 'invalid login' error message.
                    errorlogin = _('Invalid Login.') #True
            else:
                # Return an 'Valid User Credentials' error message.
                errorlogin = _('Enter Valid User Credentials.') #True
    else:
        loginform = LoginForm()

    data = {
        'module': current_view(request),
        'loginform': loginform,
        'errorlogin': errorlogin,
        'is_authenticated': request.user.is_authenticated(),
        'news' : get_news(),
    }

    return render_to_response(template, data,
           context_instance=RequestContext(request))


def notice_count(request):
    try:
        notice_count = \
        notification.Notice.objects.filter(recipient=request.user,
                                           unseen=1).count()
    except:
        notice_count = ''    
    return notice_count


def index(request):
    """Index view of Customer Interface

    **Attributes**:

        * ``form`` - LoginForm
        * ``template`` - frontend/index.html
    """
    template = 'frontend/index.html'
    errorlogin = ''
    loginform = LoginForm()    
    data = {'module': current_view(request),
            'user': request.user,
            'notice_count': notice_count(request),
            'loginform': loginform,
            'errorlogin': errorlogin,
            'news' : get_news(),
    }

    return render_to_response(template, data,
           context_instance=RequestContext(request))


def pleaselog(request):
    template = 'frontend/index.html'
    loginform = LoginForm()

    data = {
        'loginform' : loginform,
        'notlogged' : True,
        'news' : get_news(),
    }
    return render_to_response(template, data,
           context_instance = RequestContext(request))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def cust_password_reset(request):
    """Used django.contrib.auth.views.password_reset view method for
    forgotten password on Customer UI

    This method will send an e-mail to user's email-id which is entered in
    password_reset_form
    """

    if not request.user.is_authenticated():
        return password_reset(request,
        template_name='frontend/registration/password_reset_form.html',
        email_template_name=\
        'frontend/registration/password_reset_email.html',
        post_reset_redirect='/password_reset/done/',
        from_email='newfies_admin@localhost.com')
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_done(request):
    """Used django.contrib.auth.views.password_reset_done view method for
    forgotten password on Customer UI

    This will show acknowledge message to user who is seeking to reset his/her
    password.
    """

    if not request.user.is_authenticated():
        return password_reset_done(request,
        template_name='frontend/registration/password_reset_done.html')
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_confirm(request, uidb36=None, token=None):
    """Used django.contrib.auth.views.password_reset_confirm view method for
    forgotten password on Customer UI
    
    This will allow user to reset his/her password for the system
    """

    if not request.user.is_authenticated():
        return password_reset_confirm(request, uidb36=uidb36, token=token,
        template_name=\
        'frontend/registration/password_reset_confirm.html',
        post_reset_redirect='/reset/done/')
    else:
        return HttpResponseRedirect("/")


def cust_password_reset_complete(request):
    """Used django.contrib.auth.views.password_reset_complete view method for
    forgotten password on Customer UI

    This will show acknowledge message to user after successfully resetting
    his/her password for the system.
    """

    if not request.user.is_authenticated():
        return password_reset_complete(request,
        template_name=\
        'frontend/registration/password_reset_complete.html')
    else:
        return HttpResponseRedirect("/")


def common_send_notification(request, status, recipient=None):
    """User Notification (e.g. start|stop|pause) need to be saved.
    It is a common function for admin and customer UI

    **Attributes**:

        * ``pk`` - primary key of campaign record
        * ``status`` - get label for notification

    **Logic Description**:

    """    
    if not recipient:
        recipient = request.user
        sender = User.objects.get(is_superuser=1)
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
    """Campaign Status (e.g. start|stop|pause) need to be change.
    It is a common function for admin and customer UI

    **Attributes**:

        * ``pk`` - primary key of campaign record
        * ``status`` - selected status for campaign record

    **Logic Description**:

        * Selected Campaign's status need to be changed.
          Changed status can be start or stop or pause.
    """
    campaign = Campaign.objects.get(pk=pk)
    previous_status = campaign.status
    campaign.status = status
    campaign.save()

    #Start tasks to import subscriber
    if status == "1" and previous_status != "1":
        print "Launch Task : collect_subscriber(%s)" % str(pk)
        collect_subscriber.delay(pk)

    return campaign.user


@login_required
def update_campaign_status_admin(request, pk, status):
    """Campaign Status (e.g. start|stop|pause) can be changed from
    admin interface (via campaign list)"""
    recipient = common_campaign_status(pk, status)
    common_send_notification(request, status, recipient)
    return HttpResponseRedirect(reverse(
                                "admin:dialer_campaign_campaign_changelist"))


@login_required
def update_campaign_status_cust(request, pk, status):
    """Campaign Status (e.g. start|stop|pause) can be changed from
    customer interface (via dialer_campaign/campaign list)"""
    recipient = common_campaign_status(pk, status)
    common_send_notification(request, status, recipient)
    return HttpResponseRedirect('/campaign/')


# Phonebook
@login_required
def phonebook_grid(request):
    """Phonebook list in json format for flexigrid"""
    page = variable_value(request, 'page')
    rp = variable_value(request, 'rp')
    sortname = variable_value(request, 'sortname')
    sortorder = variable_value(request, 'sortorder')
    query = variable_value(request, 'query')
    qtype = variable_value(request, 'qtype')

    # page index
    if int(page) > 1:
        start_page = (int(page) - 1) * int(rp)
        end_page = start_page + int(rp)
    else:
        start_page = int(0)
        end_page = int(rp)


    #phonebook_list = []
    sortorder_sign = ''
    if sortorder == 'desc':
        sortorder_sign = '-'

    phonebook_list = Phonebook.objects\
                     .values('id', 'name', 'description', 'updated_date')\
                     .annotate(contact_count=Count('contact'))\
                     .filter(user=request.user)

    count = phonebook_list.count()
    phonebook_list = \
        phonebook_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    update_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/page_edit.png);"'
    delete_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/delete.png);"'

    rows = [{'id': row['id'],
             'cell':  ['<input type="checkbox" name="select" class="checkbox"\
                      value="' + str(row['id']) + '" />',
                      row['id'],
                      row['name'],
                      row['description'],
                      row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
                      row['contact_count'],
                      '<a href="' + str(row['id']) + '/" class="icon" ' \
                      + update_style + ' title="Update phonebook">&nbsp;</a>' +
                      '<a href="del/' + str(row['id']) + '/" class="icon" ' \
                      + delete_style + ' onClick="return get_alert_msg(' +
                      str(row['id']) + ');"  title="Delete phonebook">&nbsp;</a>'
             ]}for row in phonebook_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    #print data
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@login_required
def phonebook_list(request):
    """Phonebook list for logged in user

    **Attributes**:

        * ``template`` - frontend/phonebook/list.html

    **Logic Description**:

        * List all phonebooks which are belong to logged in user
    """
    phonebook_id_list = ''
    phonebook_list = Phonebook.objects.filter(user=request.user)
    for i in phonebook_list:
        phonebook_id_list += str(i.id) + ","
    phonebook_id_list = phonebook_id_list[:-1]
    template = 'frontend/phonebook/list.html'
    data = {
        'module': current_view(request),
        'phonebook_id_list': phonebook_id_list,
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def phonebook_add(request):
    """Add new Phonebook for logged in user

    **Attributes**:

        * ``form`` - PhonebookForm
        * ``template`` - frontend/phonebook/change.html

    **Logic Description**:

        * Add new phonebook which will belong to logged in user
          via PhonebookForm form & get redirect to phonebook list
    """
    form = PhonebookForm()
    if request.method == 'POST':
        form = PhonebookForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.save()
            request.session["msg"] = _('"%s" is added successfully.' %\
            request.POST['name'])
            return HttpResponseRedirect('/phonebook/')
    template = 'frontend/phonebook/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'add',
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def get_contact_count(request):
    """To get total no of contacts which are belong to phonebook list"""
    contact_list = Contact.objects.extra(where=['phonebook_id IN (%s)'\
                       % request.GET['pb_ids']])
    data = contact_list.count()
    return HttpResponse(data)


@login_required
def phonebook_del(request, object_id):
    """Delete phonebook for logged in user

    **Attributes**:

        * ``object_id`` - Selected phonebook object
        * ``object_list`` - Selected phonebook objects

    **Logic Description**:

        * Delete contacts from contact list which are belong to phonebook list
        * Delete selected phonebook from phonebook list
    """
    try:
        # When object_id is not 0
        phonebook = Phonebook.objects.get(pk=object_id)
        if object_id:
            # 1) delete all contacts which are belong to phonebook
            contact_list = Contact.objects.filter(phonebook=object_id)            
            contact_list.delete()

            # 2) delete phonebook
            request.session["msg"] = _('"%s" is deleted successfully.' \
                                        % phonebook.name)
            phonebook.delete()            
            return HttpResponseRedirect('/phonebook/')
    except:
        # When object_id is 0 (Multiple recrod delete)
        values = request.POST.getlist('select')
        values  = ", ".join(["%s" % el for el in values])

        # 1) delete all contacts which are belong to phonebook
        contact_list = Contact.objects.extra(where=['phonebook_id IN (%s)'\
                       % values])
        contact_list.delete()

        # 2) delete phonebook
        phonebook_list = Phonebook.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] =\
        _('%d phonebook(s) are deleted successfully.' % phonebook_list.count())
        phonebook_list.delete()
        return HttpResponseRedirect('/phonebook/')


@login_required
def phonebook_change(request, object_id):
    """Update/Delete Phonebook for logged in user

    **Attributes**:

        * ``object_id`` - Selected phonebook object
        * ``form`` - PhonebookForm
        * ``template`` - dialer_campaign/phonebook/change.html

    **Logic Description**:

        * Update/delete selected phonebook from phonebook list
          via PhonebookForm form & get redirect to phonebook list
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
                request.session["msg"] = _('"%s" is updated successfully.' \
                % request.POST['name'])
                return HttpResponseRedirect('/phonebook/')

    template = 'frontend/phonebook/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'update',
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_grid(request):
    """Contact list in json format for flexigrid"""
    page = variable_value(request, 'page')
    rp = variable_value(request, 'rp')
    sortname = variable_value(request, 'sortname')
    sortorder = variable_value(request, 'sortorder')
    query = variable_value(request, 'query')
    qtype = variable_value(request, 'qtype')

    # page index
    if int(page) > 1:
        start_page = (int(page) - 1) * int(rp)
        end_page = start_page + int(rp)
    else:
        start_page = int(0)
        end_page = int(rp)

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
        #print decoded_string
        temp_list = list(decoded_string.split('&'))
        for i in range(0, len(temp_list)):
            if temp_list[i].find('='):
                kwargs_list = list(temp_list[i].split('='))
                if kwargs_list[0] == 'kwargs':
                    kwargs = kwargs_list[1]
                if kwargs_list[0] == 'name':
                    name = kwargs_list[1]

    phonebook_id_list = ''
    phonebook_objs = Phonebook.objects.filter(user=request.user)
    for i in phonebook_objs:
        phonebook_id_list += str(i.id) + ","
    phonebook_id_list = phonebook_id_list[:-1]

    contact_list = []
    sortorder_sign = ''
    if sortorder == 'desc':
        sortorder_sign = '-'

    if phonebook_id_list:
        select_data = \
        {"status": "(CASE status WHEN 1 THEN 'ACTIVE' ELSE 'INACTIVE' END)"}
        contact_list = Contact.objects\
        .extra(select=select_data,
               where=['phonebook_id IN (%s) ' % phonebook_id_list])\
        .values('id', 'phonebook__name', 'contact', 'last_name',
                'first_name', 'description', 'status', 'additional_vars',
                'updated_date').all()

        # Search option on grid but not working
        #if str(query) and str(qtype):
            #grid_search_kwargs = {}
            #grid_search_kwargs[qtype] = query
            #contact_list = contact_list.filter(**grid_search_kwargs)
            #print contact_list

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

    update_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/page_edit.png);"'
    delete_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/delete.png);"'

    rows = [{'id': row['id'],
             'cell':  ['<input type="checkbox" name="select" class="checkbox"\
                      value="' + str(row['id']) + '" />',
                      row['id'], row['phonebook__name'], row['contact'],
                      row['last_name'], row['first_name'], row['status'],
                      row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
                      '<a href="' + str(row['id']) + '/" class="icon" ' \
                      + update_style + ' title="Update contact">&nbsp;</a>' +
                      '<a href="del/' + str(row['id']) + '/" class="icon" ' \
                      + delete_style + ' onClick="return get_alert_msg(' +
                      str(row['id']) + ');" title="Delete contact">&nbsp;</a>'
             ]}for row in contact_list]


    data = {'rows': rows,
            'page': page,
            'total': count}
    #print data
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")
    

# Subscriber
@login_required
def contact_list(request):
    """Contact list for logged in user

    **Attributes**:

        * ``template`` - frontend/contact/list.html

    **Logic Description**:

        * List all contacts from phonebooks which are belong to logged in user
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
        #'contact_list': contact_list,
        'msg': request.session.get('msg'),
        'form': form,
        'user': request.user,
        'kwargs': kwargs,
        'name': name,
        'notice_count': notice_count(request),
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_add(request):
    """Add new contact in selected phonbook for logged in user

    **Attributes**:

        * ``form`` - ContactForm
        * ``template`` - frontend/contact/change.html

    **Logic Description**:

        * Before adding contact, checked dialer setting limit if user is
          linked with it
        * Add new contact which will belong to logged in user
          via ContactForm form & get redirect to contact list
    """
    # Check dialer setting limit
    if request.user and request.method == 'POST':
        # check  Max Number of subscriber per campaign
        if check_dialer_setting(request, check_for="contact"):
            request.session['msg'] = \
            _("You have too many contacts per campaign.\
            You are allowed a maximum of %s" % \
            dialer_setting_limit(request, limit_for="contact"))

            # campaign limit reached
            common_send_notification(request, '3')
            return HttpResponseRedirect("/contact/")

    form = ContactForm(request.user)
    # Add contact
    if request.method == 'POST':
        form = ContactForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            request.session["msg"] = _('"%s" is added successfully.' %\
            request.POST['last_name'])
            return HttpResponseRedirect('/contact/')
    template = 'frontend/contact/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'add',
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_del(request, object_id):
    """Delete contact for logged in user

    **Attributes**:

        * ``object_id`` - Selected contact object
        * ``object_list`` - Selected contact objects

    **Logic Description**:

        * Delete selected contact from contact list
    """
    try:
        # When object_id is not 0
        contact = Contact.objects.get(pk=object_id)
        # Delete phonebook
        if object_id:
            request.session["msg"] = _('"%s" is deleted successfully.' \
            % contact.first_name)
            contact.delete()
            return HttpResponseRedirect('/contact/')
    except:
        # When object_id is 0 (Multiple recrod delete)
        values = request.POST.getlist('select')
        values  = ", ".join(["%s" % el for el in values])
        contact_list = Contact.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] =\
        _('%d contact(s) are deleted successfully.' % contact_list.count())
        contact_list.delete()
        return HttpResponseRedirect('/contact/')


@login_required
def contact_change(request, object_id):
    """Update/Delete contact for logged in user

    **Attributes**:

        * ``object_id`` - Selected contact object
        * ``form`` - ContactForm
        * ``template`` - frontend/contact/change.html

    **Logic Description**:

        * Update/delete selected contact from contact list
          via ContactForm form & get redirect to contact list
    """
    contact = Contact.objects.get(pk=object_id)
    form = ContactForm(request.user, instance=contact)
    if request.method == 'POST':
        # Delete contact
        if request.POST.get('delete'):
            contact_del(request, object_id)
            return HttpResponseRedirect('/contact/')
        else: # Update contact
            form = ContactForm(request.user, request.POST,
                                  instance=contact)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%s" is updated successfully.' \
                % request.POST['last_name'])
                return HttpResponseRedirect('/contact/')

    template = 'frontend/contact/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'update',
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def contact_import(request):
    """Import CSV file of Contact for logged in user

    **Attributes**:

        * ``form`` - Contact_fileImport
        * ``template`` - frontend/contact/import_contact.html

    **Logic Description**:

        * Before adding contact, checked dialer setting limit if user is
          linked with it
        * Add new contact which will belong to logged in user
          via csv file & get the result (how many recrods are uploaded
          successfully & which are not)

    **Important variable**:

        * total_rows - Total no. of records of CSV file
        * retail_record_count - No. of records which are imported from CSV file
    """
    # Check dialer setting limit
    if request.user and request.method == 'POST':
        # check  Max Number of subscriber per campaign
        if check_dialer_setting(request, check_for="contact"):
            request.session['msg'] = \
            _("You have too many contacts per campaign.\
            You are allowed a maximum of %s" % \
            dialer_setting_limit(request, limit_for="contact"))

            # campaign limit reached
            common_send_notification(request, '3')
            return HttpResponseRedirect("/contact/")

    form = Contact_fileImport(request.user)
    file_exts = ('.csv', )
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
                if (row and str(row[0].strip("\t")) > 0):
                    try:
                        # check field type
                        int(row[5].strip("\t"))

                        phonebook = \
                        Phonebook.objects.get(pk=request.POST['phonebook'])
                        try:
                            # check if prefix is alredy
                            # exist with retail plan or not
                            contact = Contact.objects.get(
                                 phonebook_id=phonebook.id,
                                 contact=row[0].strip("\t"))
                            error_msg = _('Subscriber is already exist !!')
                            error_import_list.append(row)
                        except:
                            # if not, insert record
                            Contact.objects.create(
                                  phonebook=phonebook,
                                  contact=row[0].strip("\t"),
                                  last_name=row[1].strip("\t"),
                                  first_name=row[2].strip("\t"),
                                  email=row[3].strip("\t"),
                                  description=row[4].strip("\t"),
                                  status=int(row[5].strip("\t")),
                                  additional_vars=row[6].strip("\t"))
                            contact_record_count = \
                                contact_record_count + 1
                            msg = \
                            '%d Contact(s) are uploaded  \
                             successfully out of %d row(s) !!'\
                             % (contact_record_count, total_rows)
                            success_import_list.append(row)
                    except:
                        error_msg = _("Invalid value for import! \
                               Please look at the import samples.")
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
    })
    template = 'frontend/contact/import_contact.html'
    return render_to_response(template, data,
           context_instance=RequestContext(request))


def count_contact_of_campaign(campaign_id):
    """Count no of Contacts from phonebook belong to campaign"""
    count_contact = \
    Contact.objects.filter(phonebook__campaign=campaign_id).count()
    if not count_contact:
        return str("Phonebook Empty")
    return count_contact


def get_url_campaign_status(id, status):

    control_play_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL\
    + 'newfies/icons/control_play.png);"'
    control_pause_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL \
    + 'newfies/icons/control_pause.png);"'
    control_stop_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL\
    + 'newfies/icons/control_stop.png);"'


    control_play_blue_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL \
    + 'newfies/icons/control_play_blue.png);"'
    control_pause_blue_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL \
    + 'newfies/icons/control_pause_blue.png);"'
    control_stop_blue_style = \
    'style="text-decoration:none;background-image:url(' + settings.STATIC_URL \
    + 'newfies/icons/control_stop_blue.png);"'
    
    if status == 1:
        url_str = str("<a href='#' class='icon' title='campaign is running' " +
                  control_play_style + ">&nbsp;</a>\
                  <a href='update_campaign_status_cust/" + str(id) +
                  "/2/' class='icon' title='Pause' " +
                  control_pause_blue_style +
                  ">&nbsp;</a><a href='update_campaign_status_cust/"
                  + str(id) + "/4/' class='icon' title='Stop' " +
                  control_stop_blue_style + ">&nbsp;</a>")
    if status == 2:
        url_str = str("<a href='update_campaign_status_cust/" + str(id) +
                      "/1/' class='icon' title='Start' " +
                      control_play_blue_style +
                      ">&nbsp;</a><a href='#' class='icon' \
                      title='campaign is paused' " + control_pause_style +
                      ">&nbsp;</a>" +
                      "<a href='update_campaign_status_cust/"+ str(id) +
                      "/4/' class='icon' title='Stop' " +
                      control_stop_blue_style +
                      ">&nbsp;</a>")
    if status == 4:
        url_str = str("<a href='update_campaign_status_cust/" + str(id) +
                      "/1/' class='icon' title='Start' " +
                      control_play_blue_style +
                      ">&nbsp;</a>" +
                      "<a href='update_campaign_status_cust/" + str(id) +
                      "/2/' class='icon' title='Pause' " +
                      control_pause_blue_style +
                      ">&nbsp;</a>" +
                      "<a href='#' class='icon' title='campaign is stopped' " +
                      control_stop_style + ">&nbsp;</a>")

    return url_str


# Campaign
@login_required
def campaign_grid(request):
    """Campaign list in json format for flexigrid"""
    page = variable_value(request, 'page')
    rp = variable_value(request, 'rp')
    sortname = variable_value(request, 'sortname')
    sortorder = variable_value(request, 'sortorder')
    query = variable_value(request, 'query')
    qtype = variable_value(request, 'qtype')

    # page index
    if int(page) > 1:
        start_page = (int(page) - 1) * int(rp)
        end_page = start_page + int(rp)
    else:
        start_page = int(0)
        end_page = int(rp)
    

    #campaign_list = []
    sortorder_sign = ''
    if sortorder == 'desc':
        sortorder_sign = '-'

    campaign_list = Campaign.objects\
                    .values('id', 'name', 'startingdate', 'expirationdate',
                            'aleg_gateway', 'aleg_gateway__name',
                            'answer_url', 'status').filter(user=request.user)
    count = campaign_list.count()
    campaign_list = \
        campaign_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    update_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/page_edit.png);"'
    delete_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/delete.png);"'

    rows = [{'id': row['id'],
             'cell':  ['<input type="checkbox" name="select" class="checkbox"\
                      value="' + str(row['id']) + '" />',
                      row['id'],
                      row['name'],
                      row['startingdate'].strftime('%Y-%m-%d %H:%M:%S'),
                      row['expirationdate'].strftime('%Y-%m-%d %H:%M:%S'),
                      row['aleg_gateway__name'],
                      row['answer_url'],
                      count_contact_of_campaign(row['id']),
                      str('<a href="' + str(row['id']) + '/" class="icon" ' \
                      + update_style + ' title="Update campaign">&nbsp;</a>' +
                      '<a href="del/' + str(row['id']) + '/" class="icon" ' \
                      + delete_style + ' onClick="return get_alert_msg(' +
                      str(row['id']) + ');" title="Delete campaign">&nbsp;</a>'+
                      get_url_campaign_status(row['id'], row['status'])),
             ]}for row in campaign_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    #print data
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@login_required
def campaign_list(request):
    """List all the campaigns for logged in user

    **Attributes**:

        * ``template`` - frontend/campaign/list.html

    **Logic Description**:

        * List all campaign which are belong to logged in user
    """
    campaign_list = Campaign.objects.filter(user=request.user)
    template = 'frontend/campaign/list.html'
    data = {
        'module': current_view(request),
        'campaign_list': campaign_list,
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def campaign_add(request):
    """Add new campaign for logged in user

    **Attributes**:

        * ``form`` - CampaignForm
        * ``template`` - frontend/campaign/change.html

    **Logic Description**:

        * Before adding campaign, checked dialer setting limit if user is
          linked with it
        * Add new campaign which will belong to logged in user
          via CampaignForm form & get redirect to campaign list
    """
    # Check dialer setting limit
    if request.user and request.method != 'POST':
        # check Max Number of running campaign
        if check_dialer_setting(request, check_for="campaign"):
            request.session['msg'] = msg = _("you have too many campaign.\
            Max allowed %s" \
            % dialer_setting_limit(request, limit_for="campaign"))

            # campaign limit reached
            common_send_notification(request, '3')
            return HttpResponseRedirect("/campaign/")

    form = CampaignForm()
    # Add campaign
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.save()
            request.session["msg"] = _('"%s" is added successfully.' %\
            request.POST['name'])
            return HttpResponseRedirect('/campaign/')

    template = 'frontend/campaign/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'add',
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def campaign_del(request, object_id):
    """Delete campaign for logged in user

    **Attributes**:

        * ``object_id`` - Selected campaign object
        * ``object_list`` - Selected campaign objects

    **Logic Description**:

        * Delete selected campaignt from campaign list
    """
    try:
        # When object_id is not 0
        campaign = Campaign.objects.get(pk=object_id)
        # Delete campaign
        if object_id:
            request.session["msg"] = _('"%s" is deleted successfully.' \
            % campaign.name)
            campaign.delete()
            return HttpResponseRedirect('/campaign/')
    except:
        # When object_id is 0 (Multiple recrod delete)
        values = request.POST.getlist('select')
        values  = ", ".join(["%s" % el for el in values])
        campaign_list = Campaign.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] = _('%d campaign(s) are deleted successfully.'\
        % campaign_list.count())
        campaign_list.delete()
        return HttpResponseRedirect('/campaign/')
    

@login_required
def campaign_change(request, object_id):
    """Update/Delete campaign for logged in user

    **Attributes**:

        * ``object_id`` - Selected campaign object
        * ``form`` - CampaignForm
        * ``template`` - frontend/campaign/change.html

    **Logic Description**:

        * Update/delete selected campaignt from campaign list
          via CampaignForm form & get redirect to campaign list
    """
    campaign = Campaign.objects.get(pk=object_id)
    form = CampaignForm(instance=campaign)
    if request.method == 'POST':
        # Delete campaign
        if request.POST.get('delete'):
            campaign_del(request, object_id)
            return HttpResponseRedirect('/campaign/')
        else: # Update campaign
            form = CampaignForm(request.POST, instance=campaign)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%s" is updated successfully.' \
                % request.POST['name'])
                return HttpResponseRedirect('/campaign/')

    template = 'frontend/campaign/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'update',
       'notice_count': notice_count(request),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))
