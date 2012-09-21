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

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required, \
                                           permission_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404

from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from utils.helper import grid_common_function, get_grid_update_delete_link
from dialer_campaign.views import notice_count
from dialer_audio.forms import DialerAudioFileForm
from audiofield.models import AudioFile
from common.common_functions import current_view
import os.path


def audio_file_player(audio_file):
    """audio player tag for frontend

    >>> audio_file_player('xyz.mp3')
    '<ul class="playlist"><li style="width:220px;"><a href="/mediafiles/xyz.mp3">xyz.mp3</a></li></ul>'
    """
    if audio_file:
        file_url = settings.MEDIA_URL + str(audio_file)
        player_string = \
            '<ul class="playlist"><li style="width:220px;"><a href="%s">%s</a></li></ul>'\
                % (file_url, os.path.basename(file_url))
        return player_string


@login_required
def audio_grid(request):
    """Audio list in json format for flexigrid.

    **Model**: AudioFile

    **Fields**: [id, name, description, updated_date]
    """
    grid_data = grid_common_function(request)
    page = int(grid_data['page'])
    start_page = int(grid_data['start_page'])
    end_page = int(grid_data['end_page'])
    sortorder_sign = grid_data['sortorder_sign']
    sortname = grid_data['sortname']

    audio_list = AudioFile.objects\
                     .values('id', 'name', 'audio_file', 'updated_date')\
                     .filter(user=request.user)

    count = audio_list.count()
    audio_list = audio_list\
            .order_by(sortorder_sign + sortname)[start_page:end_page]

    link_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/link.png);"'
    domain = Site.objects.get_current().domain

    rows = [{'id': row['id'],
            'cell': ['<input type="checkbox" name="select" class="checkbox"\
                value="' + str(row['id']) + '" />',
                row['name'],
                audio_file_player(row['audio_file']),
                '<input type="text" value="' + domain + \
                settings.MEDIA_URL + str(row['audio_file']) + '">',
                row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
                '<a href="' + settings.MEDIA_URL + \
                str(row['audio_file']) + '" class="icon" ' \
                + link_style + ' title="' + _('Download audio') + \
                '">&nbsp;</a>' +
                get_grid_update_delete_link(request, row['id'],
                    'dialer_audio.change_audio', _('Update audio'), 'update')+\
                get_grid_update_delete_link(request, row['id'],
                    'dialer_audio.delete_audio', _('Delete audio'), 'delete'),
                ]} for row in audio_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@permission_required('dialer_audio.view_audio', login_url='/')
@login_required
def audio_list(request):
    """AudioFile list for the logged in user

    **Attributes**:

        * ``template`` - frontend/audio/audio_list.html

    **Logic Description**:

        * List all audios which belong to the logged in user.
    """
    template = 'frontend/audio/audio_list.html'
    data = {
        'module': current_view(request),
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
        'AUDIO_DEBUG': settings.AUDIO_DEBUG,
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@permission_required('dialer_audio.add_audio', login_url='/')
@login_required
def audio_add(request):
    """Add new Audio for the logged in user

    **Attributes**:

        * ``form`` - SurveyCustomerAudioFileForm
        * ``template`` - frontend/audio/audio_change.html

    **Logic Description**:

        * Add a new audio which will belong to the logged in user
          via the CustomerAudioFileForm & get redirected to the audio list
    """
    form = DialerAudioFileForm()
    if request.method == 'POST':
        form = DialerAudioFileForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.save()
            request.session["msg"] = _('"%(name)s" is added.') %\
                {'name': request.POST['name']}
            return HttpResponseRedirect('/audio/')

    template = 'frontend/audio/audio_change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'add',
       'AUDIO_DEBUG': settings.AUDIO_DEBUG,
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@permission_required('dialer_audio.delete_audio', login_url='/')
@login_required
def audio_del(request, object_id):
    """Delete a audio for a logged in user

    **Attributes**:

        * ``object_id`` - Selected audio object
        * ``object_list`` - Selected audio objects

    **Logic Description**:

        * Delete selected the audio from the audio list
    """
    if int(object_id) != 0:
        audio = get_object_or_404(AudioFile, pk=int(object_id), user=request.user)

        # 1) delete survey
        request.session["msg"] = _('"%(name)s" is deleted.')\
                                 % {'name': audio.name}
        audio.delete()
    else:
        try:
            # When object_id is 0 (Multiple records delete)
            values = request.POST.getlist('select')
            values = ", ".join(["%s" % el for el in values])

            # 1) delete audio
            audio_list = AudioFile.objects\
                            .filter(user=request.user)\
                            .extra(where=['id IN (%s)' % values])
            request.session["msg"] =\
                _('%(count)s audio(s) are deleted.')\
                    % {'count': audio_list.count()}
            audio_list.delete()
        except:
            raise Http404

    return HttpResponseRedirect('/audio/')


@permission_required('dialer_audio.change_audio', login_url='/')
@login_required
def audio_change(request, object_id):
    """Update Audio for the logged in user

    **Attributes**:

        * ``form`` - SurveyCustomerAudioFileForm
        * ``template`` - frontend/audio/audio_change.html

    **Logic Description**:

        * Update audio which is belong to the logged in user
          via the CustomerAudioFileForm & get redirected to the audio list
    """
    obj = get_object_or_404(AudioFile, pk=object_id, user=request.user)
    form = DialerAudioFileForm(instance=obj)

    if request.GET.get('delete'):
        # perform delete
        if obj.audio_file:
            if os.path.exists(obj.audio_file.path):
                os.remove(obj.audio_file.path)
        obj.delete()
        return HttpResponseRedirect('/audio/')

    if request.method == 'POST':
        form = DialerAudioFileForm(request.POST,
                                   request.FILES,
                                   instance=obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/audio/')

    template = 'frontend/audio/audio_change.html'
    data = {
       'form': form,
       'module': current_view(request),
       'action': 'update',
       'AUDIO_DEBUG': settings.AUDIO_DEBUG,
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))
