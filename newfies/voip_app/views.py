# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.db.models import *
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from voip_app.models import VoipApp, get_voipapp_type_name
from voip_app.forms import VoipAppForm
from dialer_campaign.views import current_view, notice_count
from dialer_campaign.function_def import user_dialer_setting_msg
from dialer_campaign.function_def import *
from datetime import *


# voip_app
@login_required
def voipapp_grid(request):
    """VoIP App list in json format for flexigrid

    **Model**: VoipApp

    **Fields**: [id, name, user, description, type, gateway__name,
                 updated_date]
    """
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

    sortorder_sign = ''
    if sortorder == 'desc':
        sortorder_sign = '-'

    voipapp_list = VoipApp.objects\
                   .values('id', 'name', 'user', 'description', 'type',
                           'data', 'gateway__name',
                           'updated_date').filter(user=request.user)

    count = voipapp_list.count()
    voipapp_list = \
        voipapp_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    update_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/page_edit.png);"'
    delete_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/delete.png);"'

    rows = [{'id': row['id'],
             'cell': ['<input type="checkbox" name="select" class="checkbox"\
                      value="' + str(row['id']) + '" />',
                      row['id'],
                      row['name'],
                      row['description'],
                      get_voipapp_type_name(row['type']),
                      row['gateway__name'],
                      row['data'],
                      row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
                      '<a href="' + str(row['id']) + '/" class="icon" ' \
                      + update_style + ' title="Update VoIP App">&nbsp;</a>' +
                      '<a href="del/' + str(row['id']) + '/" class="icon" ' \
                      + delete_style + ' onClick="return get_alert_msg(' +
                      str(row['id']) +
                      ');"  title="Delete VoIP App">&nbsp;</a>'
                      ]} for row in voipapp_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@login_required
def voipapp_list(request):
    """VoIP App list for logged in user

    **Attributes**:

        * ``template`` - frontend/voipapp/list.html

    **Logic Description**:

        * List all voip app which are belong to logged in user
    """
    template = 'frontend/voipapp/list.html'
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
def voipapp_add(request):
    """Add new VoIP App for logged in user

    **Attributes**:

        * ``form`` - VoipAppForm
        * ``template`` - frontend/voipapp/change.html

    **Logic Description**:

        * Add new voip app which will belong to logged in user
          via VoipAppForm form & get redirect to voipapp list
    """
    form = VoipAppForm()
    if request.method == 'POST':
        form = VoipAppForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.save()
            request.session["msg"] = _('"%(name)s" is added successfully.') %\
            request.POST['name']
            return HttpResponseRedirect('/voipapp/')
    template = 'frontend/voipapp/change.html'
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
def voipapp_del(request, object_id):
    """Delete phonebook for logged in user

    **Attributes**:

        * ``object_id`` - Selected voipapp object
        * ``object_list`` - Selected voipapp objects

    **Logic Description**:

        * Delete voipapp from voipapp list
    """
    try:
        # When object_id is not 0
        voipapp_list = VoipApp.objects.get(pk=object_id)
        if object_id:
            # 2) delete voipapp
            request.session["msg"] = _('"%(name)s" is deleted successfully.') \
                                        % voipapp_list.name
            voipapp_list.delete()
            return HttpResponseRedirect('/voipapp/')
    except:
        # When object_id is 0 (Multiple recrod delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        # 2) delete phonebook
        voipapp_list = VoipApp.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] =\
        _('%(count)s voipapp(s) are deleted successfully.' \
        % {'count': voipapp_list.count()})
        voipapp_list.delete()
        return HttpResponseRedirect('/voipapp/')


@login_required
def voipapp_change(request, object_id):
    """Update/Delete VoIP app for logged in user

    **Attributes**:

        * ``object_id`` - Selected phonebook object
        * ``form`` - VoipAppForm
        * ``template`` - frontend/voipapp/change.html

    **Logic Description**:

        * Update/delete selected voipapp from voipapp list
          via VoipAppForm form & get redirect to voip list
    """
    voipapp = VoipApp.objects.get(pk=object_id)
    form = VoipAppForm(instance=voipapp)
    if request.method == 'POST':
        if request.POST.get('delete'):
            voipapp_del(request, object_id)
            return HttpResponseRedirect('/voipapp/')
        else:
            form = VoipAppForm(request.POST, instance=voipapp)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%(name)s" is updated successfully.' \
                % {'name': request.POST['name']})
                return HttpResponseRedirect('/voipapp/')

    template = 'frontend/voipapp/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'update',
       'notice_count': notice_count(request),
       'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))
