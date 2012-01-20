# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.db.models import *
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from voice_app.models import VoiceApp, get_voiceapp_type_name
from voice_app.forms import VoiceAppForm
from dialer_campaign.views import current_view, notice_count, update_style, delete_style, \
    grid_common_function
from dialer_campaign.function_def import user_dialer_setting_msg
from dialer_campaign.function_def import *
from datetime import *


# voice_app
@login_required
def voiceapp_grid(request):
    """Voce App list in json format for flexigrid

    **Model**: VoiceApp

    **Fields**: [id, name, user, description, type, gateway__name,
                 updated_date]
    """
    grid_data = grid_common_function(request)
    page = int(grid_data['page'])
    start_page = int(grid_data['start_page'])
    end_page = int(grid_data['end_page'])
    sortorder_sign = grid_data['sortorder_sign']
    sortname = grid_data['sortname']

    voiceapp_list = VoiceApp.objects\
                   .values('id', 'name', 'user', 'description', 'type',
                           'data', 'gateway__name',
                           'updated_date').filter(user=request.user)

    count = voiceapp_list.count()
    voiceapp_list = \
        voiceapp_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    rows = [{'id': row['id'],
             'cell': ['<input type="checkbox" name="select" class="checkbox"\
                      value="' + str(row['id']) + '" />',
                      row['name'],
                      row['description'],
                      get_voiceapp_type_name(row['type']),
                      row['gateway__name'],
                      row['data'],
                      row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
                      '<a href="' + str(row['id']) + '/" class="icon" ' \
                      + update_style + ' title="' + _('Update Voice App') + '">&nbsp;</a>' +\
                      '<a href="del/' + str(row['id']) + '/" class="icon" ' \
                      + delete_style + ' onClick="return get_alert_msg(' +\
                      str(row['id']) +\
                      ');"  title="' + _('Delete Voice App') + '">&nbsp;</a>'
                      ]} for row in voiceapp_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@login_required
def voiceapp_list(request):
    """Voce App list for logged in user

    **Attributes**:

        * ``template`` - frontend/voiceapp/list.html

    **Logic Description**:

        * List all voice app which are belong to logged in user
    """
    template = 'frontend/voiceapp/list.html'
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
def voiceapp_add(request):
    """Add new Voice App for logged in user

    **Attributes**:

        * ``form`` - VoiceAppForm
        * ``template`` - frontend/voiceapp/change.html

    **Logic Description**:

        * Add new voice app which will belong to logged in user
          via VoiceAppForm form & get redirect to voiceapp list
    """
    form = VoiceAppForm()
    if request.method == 'POST':
        form = VoiceAppForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.save()
            request.session["msg"] = _('"%(name)s" is added.') %\
            request.POST
            return HttpResponseRedirect('/voiceapp/')
    template = 'frontend/voiceapp/change.html'
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
def voiceapp_del(request, object_id):
    """Delete voiceapp for logged in user

    **Attributes**:

        * ``object_id`` - Selected voiceapp object
        * ``object_list`` - Selected voiceapp objects

    **Logic Description**:

        * Delete voiceapp from voiceapp list
    """
    try:
        # When object_id is not 0
        voiceapp_list = VoiceApp.objects.get(pk=object_id)
        if object_id:
            # 1) delete voiceapp
            request.session["msg"] = _('"%(name)s" is deleted.' \
            % {'name': voiceapp_list.name})
            voiceapp_list.delete()
            return HttpResponseRedirect('/voiceapp/')
    except:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        # 1) delete voiceapp
        voiceapp_list = VoiceApp.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] =\
        _('%(count)s voiceapp(s) are deleted.' \
        % {'count': voiceapp_list.count()})
        voiceapp_list.delete()
        return HttpResponseRedirect('/voiceapp/')


@login_required
def voiceapp_change(request, object_id):
    """Update/Delete Voice app for logged in user

    **Attributes**:

        * ``object_id`` - Selected voiceapp object
        * ``form`` - VoiceAppForm
        * ``template`` - frontend/voiceapp/change.html

    **Logic Description**:

        * Update/delete selected voiceapp from voiceapp list
          via VoiceAppForm form & get redirect to voice list
    """
    voiceapp = VoiceApp.objects.get(pk=object_id)
    form = VoiceAppForm(instance=voiceapp)
    if request.method == 'POST':
        if request.POST.get('delete'):
            voiceapp_del(request, object_id)
            return HttpResponseRedirect('/voiceapp/')
        else:
            form = VoiceAppForm(request.POST, instance=voiceapp)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%(name)s" is updated.' \
                % {'name': request.POST['name']})
                return HttpResponseRedirect('/voiceapp/')

    template = 'frontend/voiceapp/change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'update',
       'notice_count': notice_count(request),
       'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))
