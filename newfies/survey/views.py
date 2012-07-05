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
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.db.models import *
from django.conf import settings
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

from dialer_campaign.models import Campaign
from dialer_campaign.views import current_view, notice_count, update_style, \
    delete_style, grid_common_function
from survey.models import *
from survey.forms import *
from dialer_cdr.models import Callrequest
from audiofield.models import AudioFile

from datetime import *
import time
import os.path


@csrf_exempt
def survey_finestatemachine(request):
    """Survey Fine State Machine

    **Model**: SurveyQuestion

    """
    initial_state = None
    default_transition = None
    current_state = None
    next_state = None
    testdebug = False

    #Load Plivo Post parameters
    opt_ALegRequestUUID = request.POST.get('ALegRequestUUID')
    opt_CallUUID = request.POST.get('CallUUID')
    DTMF = request.POST.get('Digits')
    #print "DTMF=%s - opt_CallUUID=%s" % (DTMF, opt_CallUUID)

    if testdebug:
        #implemented to test in browser
        if not opt_ALegRequestUUID:
            opt_ALegRequestUUID = request.GET.get('ALegRequestUUID')
        if not opt_CallUUID:
            opt_CallUUID = request.GET.get('CallUUID')
        if not opt_CallUUID:
            opt_CallUUID = opt_ALegRequestUUID
        if not DTMF:
            DTMF = request.GET.get('Digits')
        #print "DTMF=%s - opt_CallUUID=%s" % (DTMF, opt_CallUUID)

    if not opt_ALegRequestUUID:
        return HttpResponse(content="Error : missing parameter ALegRequestUUID", status=400)

    #Create the keys to store the cache
    key_state = "%s_state" % opt_CallUUID
    key_surveyapp = "%s_surveyapp_id" % opt_CallUUID

    #Retrieve the values of the keys
    current_state = cache.get(key_state)
    surveyapp_id = cache.get(key_surveyapp)

    if not current_state:
        cache.set(key_state, 0, 21600)  # 21600 seconds = 6 hours
        current_state = 0

    try:
        obj_callrequest = Callrequest.objects.get(request_uuid=opt_ALegRequestUUID)
    except:
        return HttpResponse(content="Error : retrieving Callrequest with the ALegRequestUUID", status=400)

    surveyapp_id = obj_callrequest.object_id
    cache.set(key_surveyapp, surveyapp_id, 21600)  # 21600 seconds = 6 hours

    #TODO : use constant
    obj_callrequest.status = 8  # IN-PROGRESS
    obj_callrequest.aleg_uuid = opt_CallUUID
    obj_callrequest.save()

    #Load the questions
    list_question = SurveyQuestion.objects\
                    .filter(surveyapp=surveyapp_id).order_by('order')

    #Check if we receive a DTMF for the previous question then store the result
    if DTMF and len(DTMF) > 0 and current_state > 0:
        #find the response for this key pressed
        try:
            surveyresponse = SurveyResponse.objects.get(
                            key=DTMF,
                            surveyquestion=list_question[current_state - 1])
            if not surveyresponse.keyvalue:
                response_value = DTMF
            else:
                response_value = surveyresponse.keyvalue
        except:
            #It's possible that this response is not accepted
            response_value = DTMF

        new_surveycampaignresult = SurveyCampaignResult(
                    campaign=obj_callrequest.campaign,
                    surveyapp_id=surveyapp_id,
                    callid=opt_CallUUID,
                    question=list_question[current_state - 1].question,
                    response=response_value)
        new_surveycampaignresult.save()

    #Transition go to next state
    next_state = current_state + 1
    cache.set(key_state, next_state, 21600)
    #print "Saved state in Cache (%s = %s)" % (key_state, next_state)

    try:
        list_question[current_state]
    except IndexError:
        html = '<Response><Hangup/></Response>'
        return HttpResponse(html)

    #retrieve the basename of the url
    url = settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL
    slashparts = url.split('/')
    url_basename = '/'.join(slashparts[:3])

    if list_question[current_state].message_type == 1 and \
        hasattr(list_question[current_state], 'audio_message') and \
        list_question[current_state].audio_message.audio_file.url:
        #Audio file
        question = "<Play>%s%s</Play>" % (
                    url_basename,
                    list_question[current_state].audio_message.audio_file.url)
    else:
        #Text2Speech
        question = "<Speak>%s</Speak>" % list_question[current_state].question

    #return the question
    html = '<Response>\n\
                <GetDigits action="%s" method="GET" numDigits="1" retries="1" validDigits="0123456789" timeout="10" finishOnKey="#">\n\
                    %s\n\
                </GetDigits>\
            </Response>' % (settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL, question)
    return HttpResponse(html)


@login_required
def survey_grid(request):
    """Survey list in json format for flexigrid.

    **Model**: SurveyApp

    **Fields**: [id, name, description, updated_date]
    """
    grid_data = grid_common_function(request)
    page = int(grid_data['page'])
    start_page = int(grid_data['start_page'])
    end_page = int(grid_data['end_page'])
    sortorder_sign = grid_data['sortorder_sign']
    sortname = grid_data['sortname']

    survey_list = SurveyApp.objects\
                     .values('id', 'name', 'description', 'updated_date')\
                     .filter(user=request.user)

    count = survey_list.count()
    survey_list = \
        survey_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    rows = [{'id': row['id'],
            'cell': ['<input type="checkbox" name="select" class="checkbox"\
                value="' + str(row['id']) + '" />',
                row['name'],
                row['description'],
                row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
                '<a href="' + str(row['id']) + '/" class="icon" ' \
                + update_style + ' title="' + \
                _('Update survey') + '">&nbsp;</a>' +
                '<a href="del/' + str(row['id']) + '/" class="icon" ' \
                + delete_style + ' onClick="return get_alert_msg(' +
                str(row['id']) +
                ');"  title="' + _('Delete survey') + '">&nbsp;</a>']}\
                for row in survey_list]
    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@login_required
def survey_list(request):
    """SurveyApp list for the logged in user

    **Attributes**:

        * ``template`` - frontend/survey/list.html

    **Logic Description**:

        * List all surveys which belong to the logged in user.
    """
    template = 'frontend/survey/survey_list.html'
    data = {
        'module': current_view(request),
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def survey_add(request):
    """Add new Survey for the logged in user

    **Attributes**:

        * ``form`` - SurveyAppForm
        * ``template`` - frontend/survey/change.html

    **Logic Description**:

        * Add a new survey which will belong to the logged in user
          via the SurveyForm & get redirected to the survey list
    """
    form = SurveyForm()
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.save()
            request.session["msg"] = _('"%(name)s" is added.') %\
            {'name': request.POST['name']}
            return HttpResponseRedirect('/survey/%s/' % (obj.id))
    template = 'frontend/survey/survey_change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'add',
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def survey_del(request, object_id):
    """Delete a survey for a logged in user

    **Attributes**:

        * ``object_id`` - Selected survey object
        * ``object_list`` - Selected survey objects

    **Logic Description**:

        * Delete selected the survey from the survey list
    """
    try:
        # When object_id is not 0
        survey = SurveyApp.objects.get(pk=object_id)
        if object_id:
            # 1) delete survey
            request.session["msg"] = _('"%(name)s" is deleted.') \
                                        % {'name': survey.name}
            survey.delete()
            return HttpResponseRedirect('/survey/')
    except:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        # 1) delete survey
        survey_list = SurveyApp.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] =\
        _('%(count)s survey(s) are deleted.') \
        % {'count': survey_list.count()}
        survey_list.delete()
        return HttpResponseRedirect('/survey/')


@login_required
def survey_change(request, object_id):
    """Update/Delete Survey for the logged in user

    **Attributes**:

        * ``object_id`` - Selected survey object
        * ``form`` - SurveyForm
        * ``template`` - frontend/survey/change.html

    **Logic Description**:

        * Update/delete selected survey from the survey list
          via SurveyForm & get redirected to survey list
    """
    survey = SurveyApp.objects.get(pk=object_id)
    survey_que_list = SurveyQuestion.objects\
                        .filter(surveyapp=survey).order_by('order')

    form = SurveyForm(instance=survey)
    new_survey_que_form = SurveyQuestionNewForm(
                            request.user,
                            initial={'surveyapp': survey})
    new_survey_res_form = SurveyResponseForm()

    survey_que_form_collection = {}
    survey_res_form_collection = {}

    for survey_que in survey_que_list:
        f = SurveyQuestionForm(instance=survey_que)
        survey_que_form_collection['%s' % survey_que.id] = f

        # survey question response
        survey_response_list = SurveyResponse.objects\
                                .filter(surveyquestion=survey_que)
        for survey_res in sorted(survey_response_list):
            r = SurveyResponseForm(instance=survey_res)
            survey_res_form_collection['%s' % survey_res.id] = {'form': r, 'que_id': survey_res.surveyquestion_id}

    if request.method == 'POST':
        if request.POST.get('delete'):
            survey_del(request, object_id)
            return HttpResponseRedirect('/survey/')
        else:
            form = SurveyForm(request.POST, request.user, instance=survey)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%(name)s" is updated.') \
                % {'name': request.POST['name']}
                return HttpResponseRedirect('/survey/')

    template = 'frontend/survey/survey_change.html'

    data = {
       'module': current_view(request),
       'action': 'update',
       'form': form,
       'survey_que_list': survey_que_list,
       'survey_que_forms': survey_que_form_collection,
       'new_survey_que_form': new_survey_que_form,
       'survey_res_form_collection': survey_res_form_collection,
       'new_survey_res_form': new_survey_res_form,
       'msg': request.session.get('msg'),
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


def audio_file_player(audio_file):
    """audio player tag for frontend"""
    if audio_file:
        file_url = settings.MEDIA_URL + str(audio_file)
        player_string = '<ul class="playlist"><li style="width:220px;">\
        <a href="%s">%s</a></li></ul>' % (file_url, os.path.basename(file_url))
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
                '<a href="' + str(row['id']) + '/" class="icon" ' \
                + update_style + ' title="' + _('Update audio') + \
                '">&nbsp;</a>' +
                '<a href="del/' + str(row['id']) + '/" class="icon" ' \
                + delete_style + ' onClick="return get_alert_msg(' +
                str(row['id']) +
                ');"  title="' + _('Delete audio') + '">&nbsp;</a>']}\
                for row in audio_list]

    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")


@login_required
def audio_list(request):
    """AudioFile list for the logged in user

    **Attributes**:

        * ``template`` - frontend/survey/audio_list.html

    **Logic Description**:

        * List all audios which belong to the logged in user.
    """
    template = 'frontend/survey/audio_list.html'
    data = {
        'module': current_view(request),
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
        'audio_list': audio_list,
        'AUDIO_DEBUG': settings.AUDIO_DEBUG,
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def audio_add(request):
    """Add new Audio for the logged in user

    **Attributes**:

        * ``form`` - SurveyCustomerAudioFileForm
        * ``template`` - frontend/survey/audio_change.html

    **Logic Description**:

        * Add a new audio which will belong to the logged in user
          via the CustomerAudioFileForm & get redirected to the audio list
    """
    form = SurveyCustomerAudioFileForm()
    if request.method == 'POST':
        form = SurveyCustomerAudioFileForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.save()
            request.session["msg"] = _('"%(name)s" is added.') %\
            {'name': request.POST['name']}
            return HttpResponseRedirect('/audio/')

    template = 'frontend/survey/audio_change.html'
    data = {
       'module': current_view(request),
       'form': form,
       'action': 'add',
       'AUDIO_DEBUG': settings.AUDIO_DEBUG,
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def audio_del(request, object_id):
    """Delete a audio for a logged in user

    **Attributes**:

        * ``object_id`` - Selected audio object
        * ``object_list`` - Selected audio objects

    **Logic Description**:

        * Delete selected the audio from the audio list
    """
    try:
        # When object_id is not 0
        audio = AudioFile.objects.get(pk=object_id)
        if object_id:
            # 1) delete survey
            request.session["msg"] = _('"%(name)s" is deleted.') \
                                        % {'name': audio.name}
            audio.delete()
            return HttpResponseRedirect('/audio/')
    except:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        # 1) delete audio
        audio_list = AudioFile.objects.extra(where=['id IN (%s)' % values])
        request.session["msg"] =\
        _('%(count)s audio(s) are deleted.') \
        % {'count': audio_list.count()}
        audio_list.delete()
        return HttpResponseRedirect('/audio/')


@login_required
def audio_change(request, object_id):
    """Update Audio for the logged in user

    **Attributes**:

        * ``form`` - SurveyCustomerAudioFileForm
        * ``template`` - frontend/survey/audio_change.html

    **Logic Description**:

        * Update audio which is belong to the logged in user
          via the CustomerAudioFileForm & get redirected to the audio list
    """
    obj = AudioFile.objects.get(pk=object_id)
    form = CustomerAudioFileForm(instance=obj)

    if request.GET.get('delete'):
        # perform delete
        if obj.audio_file:
            if os.path.exists(obj.audio_file.path):
                os.remove(obj.audio_file.path)
        obj.delete()
        return HttpResponseRedirect('/audio/')

    if request.method == 'POST':
        form = CustomerAudioFileForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/audio/')

    template = 'frontend/survey/audio_change.html'
    data = {
       'form': form,
       'module': current_view(request),
       'action': 'update',
       'AUDIO_DEBUG': settings.AUDIO_DEBUG,
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


@login_required
def survey_report(request):
    """AudioFile list for the logged in user

    **Attributes**:

        * ``template`` - frontend/survey/survey_report.html

    **Logic Description**:

        * List all survey_report which belong to the logged in user.
    """
    form = SurveyReportForm(request.user)
    survey_result = ''
    if request.method == 'POST':
        form = SurveyReportForm(request.user, request.POST)
        if form.is_valid():
            try:
                campaign_obj = Campaign.objects\
                                .get(id=int(request.POST['campaign']))
                survey_result = SurveyCampaignResult.objects\
                                .filter(campaign=campaign_obj)\
                                .values('question', 'response')\
                                .annotate(Count('response'))\
                                .distinct()\
                                .order_by('question')

                if not survey_result:
                    request.session["err_msg"] = _('No record found!.')

            except:
                request.session["err_msg"] = _('No campaign attached with survey.')

    template = 'frontend/survey/survey_report.html'
    data = {
        'module': current_view(request),
        'msg': request.session.get('msg'),
        'err_msg': request.session.get('err_msg'),
        'notice_count': notice_count(request),
        'form': form,
        'survey_result': survey_result,
    }
    request.session['msg'] = ''
    request.session['err_msg'] = ''
    return render_to_response(template, data,
           context_instance=RequestContext(request))
