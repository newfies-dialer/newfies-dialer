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

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required, \
    permission_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from dialer_audio.constants import AUDIO_COLUMN_NAME
from dialer_audio.forms import DialerAudioFileForm
from audiofield.models import AudioFile
from common.common_functions import get_pagination_vars
import os.path

audio_redirect_url = '/module/audio/'


@permission_required('audiofield.view_audiofile', login_url='/')
@login_required
def audio_list(request):
    """AudioFile list for the logged in user

    **Attributes**:

        * ``template`` - frontend/audio/audio_list.html

    **Logic Description**:

        * List all audios which belong to the logged in user.
    """
    sort_col_field_list = ['id', 'name', 'updated_date']
    default_sort_field = 'id'
    pagination_data = get_pagination_vars(
        request, sort_col_field_list, default_sort_field)

    PAGE_SIZE = pagination_data['PAGE_SIZE']
    sort_order = pagination_data['sort_order']
    audio_list = AudioFile.objects.filter(user=request.user).order_by(sort_order)
    domain = Site.objects.get_current().domain

    template = 'frontend/audio/audio_list.html'
    data = {
        'audio_list': audio_list,
        'total_audio': audio_list.count(),
        'PAGE_SIZE': PAGE_SIZE,
        'AUDIO_COLUMN_NAME': AUDIO_COLUMN_NAME,
        'col_name_with_order': pagination_data['col_name_with_order'],
        'domain': domain,
        'msg': request.session.get('msg'),
        'AUDIO_DEBUG': settings.AUDIO_DEBUG,
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('audiofield.add_audiofile', login_url='/')
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
            obj.user = request.user
            obj.save()
            request.session["msg"] = _('"%(name)s" added.') % \
                {'name': request.POST['name']}
            return HttpResponseRedirect(audio_redirect_url)

    template = 'frontend/audio/audio_change.html'
    data = {
        'form': form,
        'action': 'add',
        'AUDIO_DEBUG': settings.AUDIO_DEBUG,
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


def delete_audio_file(obj):
    """Delete audio file from computer drive"""
    if obj.audio_file:
        if os.path.exists(obj.audio_file.path):
            os.remove(obj.audio_file.path)
    return True


@permission_required('audiofield.delete_audiofile', login_url='/')
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
        audio = get_object_or_404(
            AudioFile, pk=int(object_id), user=request.user)
        request.session["msg"] = _('"%(name)s" is deleted.') % {'name': audio.name}

        # 1) remove audio file from drive
        delete_audio_file(audio)
        # 2) delete audio
        audio.delete()
    else:
        try:
            # When object_id is 0 (Multiple records delete)
            values = request.POST.getlist('select')
            values = ", ".join(["%s" % el for el in values])

            audio_list = AudioFile.objects \
                .filter(user=request.user) \
                .extra(where=['id IN (%s)' % values])

            request.session["msg"] = _('%(count)s audio(s) are deleted.') \
                % {'count': audio_list.count()}

            # 1) remove audio file from drive
            for audio in audio_list:
                delete_audio_file(audio)

            # 2) delete audio
            audio_list.delete()
        except:
            raise Http404

    return HttpResponseRedirect(audio_redirect_url)


@permission_required('audiofield.change_audiofile', login_url='/')
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

    if request.method == 'POST':
        if request.POST.get('delete'):
            audio_change(request, object_id)
            return HttpResponseRedirect(audio_redirect_url)
        else:
            form = DialerAudioFileForm(
                request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(audio_redirect_url)

    template = 'frontend/audio/audio_change.html'
    data = {
        'form': form,
        'action': 'update',
        'AUDIO_DEBUG': settings.AUDIO_DEBUG,
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))
