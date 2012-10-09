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

# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required,\
                                           permission_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from voice_app.models import VoiceApp, VoiceApp_template, get_voiceapp_type_name
from voice_app.forms import VoiceAppForm
from dialer_campaign.views import notice_count
from utils.helper import grid_common_function, get_grid_update_delete_link
from dialer_campaign.function_def import user_dialer_setting_msg
from common.common_functions import current_view


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

    voiceapp_list = VoiceApp_template.objects\
                   .values('id', 'name', 'user', 'description', 'type',
                           'data', 'tts_language', 'gateway__name',
                           'updated_date').filter(user=request.user)

    count = voiceapp_list.count()
    voiceapp_list = \
        voiceapp_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    rows = [{'id': row['id'],
             'cell': ['<input type="checkbox" name="select" class="checkbox"\
                      value="%s" />' % (str(row['id']) ),
                      row['name'],
                      row['description'],
                      get_voiceapp_type_name(row['type']),
                      row['gateway__name'],
                      row['data'],
                      row['tts_language'],
                      row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
                      get_grid_update_delete_link(request, row['id'],
                          'voice_app.change_voiceapp',
                          _('Update Voice App'), 'update')+\
                      get_grid_update_delete_link(request, row['id'],
                          'voice_app.delete_voiceapp',
                                        _('Delete Voice App'), 'delete'),
                      ]} for row in voiceapp_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@permission_required('voice_app.view_voiceapp_template', login_url='/')
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
    request.session['error_msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@permission_required('voice_app.add_voiceapp_template', login_url='/')
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


@permission_required('voice_app.delete_voiceapp_template', login_url='/')
@login_required
def voiceapp_del(request, object_id):
    """Delete voiceapp for logged in user

    **Attributes**:

        * ``object_id`` - Selected voiceapp object
        * ``object_list`` - Selected voiceapp objects

    **Logic Description**:

        * Delete voiceapp from voiceapp list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        voiceapp = get_object_or_404(VoiceApp_template, pk=object_id, user=request.user)

        # 1) delete voiceapp
        request.session["msg"] = _('"%(name)s" is deleted.'\
                                   % {'name': voiceapp.name})
        voiceapp.delete()
    else:
        try:
            # When object_id is 0 (Multiple records delete)
            values = request.POST.getlist('select')
            values = ", ".join(["%s" % el for el in values])

            # 1) delete voiceapp
            voiceapp_list = VoiceApp_template.objects\
                                .filter(user=request.user)\
                                .extra(where=['id IN (%s)' % values])
            if voiceapp_list:
                request.session["msg"] = _('%(count)s voiceapp(s) are deleted.'\
                                           % {'count': voiceapp_list.count()})
                voiceapp_list.delete()
        except:
            raise Http404

    return HttpResponseRedirect('/voiceapp/')


@permission_required('voice_app.change_voiceapp_template', login_url='/')
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
    voiceapp = get_object_or_404(VoiceApp_template, pk=object_id, user=request.user)
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


@permission_required('voice_app.view_voiceapp_template', login_url='/')
@login_required
def voiceapp_view(request, object_id):
    """Update/Delete Voice app for logged in user

    **Attributes**:

        * ``object_id`` - Selected voiceapp object
        * ``form`` - VoiceAppForm
        * ``template`` - frontend/voiceapp/change.html

    **Logic Description**:

        * Update/delete selected voiceapp from voiceapp list
          via VoiceAppForm form & get redirect to voice list
    """
    voiceapp = get_object_or_404(VoiceApp, pk=object_id, user=request.user)
    form = VoiceAppForm(instance=voiceapp, voiceapp_view=True)

    template = 'frontend/voiceapp/change.html'
    data = {
        'form': form,
        'action': 'view',
        'module': current_view(request),
        'notice_count': notice_count(request),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
        context_instance=RequestContext(request))

