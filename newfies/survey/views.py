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
from django.contrib.auth.decorators import login_required,\
                                           permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.db.models import Sum, Avg, Count
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from dialer_campaign.models import Campaign
from dialer_campaign.views import notice_count
from survey.models import SurveyApp, SurveyQuestion,\
                          SurveyResponse, SurveyCampaignResult
from survey.forms import SurveyForm,\
                         SurveyQuestionForm,\
                         SurveyResponseForm,\
                         SurveyDetailReportForm
from survey.function_def import export_question_result
from utils.helper import grid_common_function, get_grid_update_delete_link
from dialer_cdr.models import Callrequest, VoIPCall
from common.common_functions import variable_value, current_view
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv
import os.path


@csrf_exempt
def survey_finestatemachine(request):
    """Survey Fine State Machine

    **Model**: SurveyQuestion

    """
    current_state = None
    next_state = None
    testdebug = False
    delcache = False

    #Load Plivo Post parameters
    opt_ALegRequestUUID = request.POST.get('ALegRequestUUID')
    opt_CallUUID = request.POST.get('CallUUID')
    DTMF = request.POST.get('Digits')
    #print "DTMF=%s - opt_CallUUID=%s" % (DTMF, opt_CallUUID)

    if testdebug:
        #implemented to test in browser
        #usage :
        #http://127.0.0.1:8000/survey_finestatemachine/?ALegRequestUUID=df8a8478-cc57-11e1-aa17-00231470a30c&Digits=1&RecordFile=tesfilename.mp3
        if not opt_ALegRequestUUID:
            opt_ALegRequestUUID = request.GET.get('ALegRequestUUID')
        if not opt_CallUUID:
            opt_CallUUID = request.GET.get('CallUUID')
        if not opt_CallUUID:
            opt_CallUUID = opt_ALegRequestUUID
        if not DTMF:
            DTMF = request.GET.get('Digits')
        delcache = request.GET.get('delcache')
        #print "DTMF=%s - opt_CallUUID=%s" % (DTMF, opt_CallUUID)

    if not opt_ALegRequestUUID:
        return HttpResponse(
            content="Error : missing parameter ALegRequestUUID",
            status=400)

    #Create the keys to store the cache
    key_state = "%s_state" % opt_CallUUID
    key_prev_qt = "%s_prev_qt" % opt_CallUUID  # Previous question
    key_surveyapp = "%s_surveyapp_id" % opt_CallUUID

    if testdebug and delcache:
        cache.delete(key_state)
        cache.delete(key_surveyapp)

    #Retrieve the values of the keys
    current_state = cache.get(key_state)
    surveyapp_id = cache.get(key_surveyapp)
    obj_prev_qt = False

    if not current_state:
        cache.set(key_state, 0, 21600)  # 21600 seconds = 6 hours
        cache.set(key_prev_qt, 0, 21600)  # 21600 seconds = 6 hours
        current_state = 0
    else:
        prev_qt = cache.get(key_prev_qt)
        if prev_qt:
            #print "\nPREVIOUS QUESTION ::> %d" % prev_qt
            #Get previous Question
            try:
                obj_prev_qt = SurveyQuestion.objects.get(id=prev_qt)
            except:
                obj_prev_qt = False
    try:
        obj_callrequest = Callrequest.objects\
            .get(request_uuid=opt_ALegRequestUUID)
    except:
        return HttpResponse(
               content="Error : retrieving Callrequest with the ALegRequestUUID",
               status=400)

    surveyapp_id = obj_callrequest.object_id
    cache.set(key_surveyapp, surveyapp_id, 21600)  # 21600 seconds = 6 hours

    if current_state == 0:
        #TODO : use constant
        obj_callrequest.status = 8  # IN-PROGRESS
        obj_callrequest.aleg_uuid = opt_CallUUID
        obj_callrequest.save()

    #print "current_state = %s" % str(current_state)

    #Load the questions
    list_question = SurveyQuestion.objects\
        .filter(surveyapp=surveyapp_id).order_by('order')

    if obj_prev_qt and obj_prev_qt.type == 3:
        #Previous Recording
        if testdebug:
            RecordFile = request.GET.get('RecordFile')
            RecordingDuration = request.GET.get('RecordingDuration')
        else:
            RecordFile = request.POST.get('RecordFile')
            RecordingDuration = request.POST.get('RecordingDuration')
        try:
            RecordFile = os.path.split(RecordFile)[1]
        except:
            RecordFile = ''
        new_surveycampaignresult = SurveyCampaignResult(
                campaign=obj_callrequest.campaign,
                surveyapp_id=surveyapp_id,
                callid=opt_CallUUID,
                question=obj_prev_qt,
                record_file=RecordFile,
                recording_duration=RecordingDuration,
                callrequest=obj_callrequest)
        new_surveycampaignresult.save()
    #Check if we receive a DTMF for the previous question then store the result
    elif DTMF and len(DTMF) > 0 and current_state > 0:
        #find the response for this key pressed
        try:
            #Get list of responses of the previous Question
            surveyresponse = SurveyResponse.objects.get(
                                key=DTMF,
                                surveyquestion=obj_prev_qt)
            if not surveyresponse or not surveyresponse.keyvalue:
                response_value = DTMF
            else:
                response_value = surveyresponse.keyvalue

            #if there is a response for this DTMF then reset the current_state
            if surveyresponse and surveyresponse.goto_surveyquestion:
                l = 0
                for question in list_question:
                    if question.id == surveyresponse.goto_surveyquestion.id:
                        current_state = l
                        #print "Found it (%d) (l=%d)!" % (question.id, l)
                        break
                    l = l + 1
        except:
            #It's possible that this response is not accepted
            response_value = DTMF
        try:
            new_surveycampaignresult = SurveyCampaignResult(
                    campaign=obj_callrequest.campaign,
                    surveyapp_id=surveyapp_id,
                    callid=opt_CallUUID,
                    question=obj_prev_qt,
                    response=response_value,
                    callrequest=obj_callrequest)
            new_surveycampaignresult.save()

        except IndexError:
            # error index
            html = '<Response><Hangup/></Response>'
            return HttpResponse(html)

    #Transition go to next state
    next_state = current_state + 1

    cache.set(key_state, next_state, 21600)
    #print "Saved state in Cache (%s = %s)" % (key_state, next_state)

    try:
        list_question[current_state]
        #set previous question
        prev_qt = list_question[current_state].id
        cache.set(key_prev_qt, prev_qt, 21600)
    except IndexError:
        html = '<Response><Hangup/></Response>'
        return HttpResponse(html)

    #retrieve the basename of the url
    url = settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL
    slashparts = url.split('/')
    url_basename = '/'.join(slashparts[:3])

    audio_file_url = False
    if list_question[current_state].message_type == 1:
        try:
            audio_file_url = list_question[current_state]\
                .audio_message.audio_file.url
        except:
            audio_file_url = False

    if audio_file_url:
        #Audio file
        question = "<Play>%s%s</Play>" % (
            url_basename,
            list_question[current_state].audio_message.audio_file.url)
    else:
        #Text2Speech
        question = "<Speak>%s</Speak>" % list_question[current_state].question

    #Menu
    if list_question[current_state].type == 1:
        html =\
            '<Response>\n'\
            '   <GetDigits action="%s" method="GET" numDigits="1" '\
            'retries="1" validDigits="0123456789" timeout="%s" '\
            'finishOnKey="#">\n'\
            '       %s\n'\
            '   </GetDigits>\n'\
            '   <Redirect>%s</Redirect>\n'\
            '</Response>' % (
                settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL,
                settings.MENU_TIMEOUT,
                question,
                settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL)
    #Recording
    elif list_question[current_state].type == 3:
        html =\
            '<Response>\n'\
            '   %s\n'\
            '   <Record maxLength="120" finishOnKey="*#" action="%s" '\
            'method="GET" filePath="%s" timeout="%s"/>'\
            '</Response>' % (
                question,
                settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL,
                settings.FS_RECORDING_PATH,
                settings.MENU_TIMEOUT)
    # Hangup
    else:
        html =\
            '<Response>\n'\
            '   %s\n'\
            '   <Hangup />'\
            '</Response>' % (question)
        next_state = current_state
        cache.set(key_state, next_state, 21600)

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
    survey_list =\
    survey_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    rows = [{'id': row['id'],
             'cell': ['<input type="checkbox" name="select" class="checkbox"\
                      value="' + str(row['id']) + '" />',
                      row['name'],
                      row['description'],
                      row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
                      get_grid_update_delete_link(request, row['id'],
                          'survey.change_surveyapp',
                          _('Update survey'), 'update')+\
                      get_grid_update_delete_link(request, row['id'],
                          'survey.delete_surveyapp',
                          _('Delete survey'), 'delete'),
                      ]} for row in survey_list]
    data = {'rows': rows,
            'page': page,
            'total': count}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
        content_type="application/json")


@permission_required('survey.view_survey', login_url='/')
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


@permission_required('survey.add_survey', login_url='/')
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


@permission_required('survey.delete_survey', login_url='/')
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
            request.session["msg"] = _('"%(name)s" is deleted.')\
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
            _('%(count)s survey(s) are deleted.')\
                % {'count': survey_list.count()}
        survey_list.delete()
        return HttpResponseRedirect('/survey/')


@login_required
def survey_question_list(request):
    """Get survey question list from AJAX request"""
    que_list = SurveyQuestion.objects\
        .filter(surveyapp_id=request.GET['surveyapp_id'],
                user=request.user).order_by('order')
    result_string = ''
    rec_count = 1
    for i in que_list:
        if len(que_list) == rec_count:
            result_string += str(i.id) + '-|-' + str(i.question)
        else:
            result_string += str(i.id) + '-|-' + str(i.question) + '-|-'

        rec_count += 1

    return HttpResponse(result_string)


@login_required
def survey_question_add(request):
    """Add new Survey for the logged in user

    **Attributes**:

        * ``form`` - SurveyQuestionForm
        * ``template`` - frontend/survey/survey_question_change.html

    **Logic Description**:

        * Add a new survey which will belong to the logged in user
          via the SurveyForm & get redirected to the survey list
    """
    surveyapp_id = request.GET.get('surveyapp_id')
    survey = SurveyApp.objects.get(pk=surveyapp_id)

    form = SurveyQuestionForm(request.user, initial={'surveyapp': survey})
    request.session['err_msg'] = ''
    if request.method == 'POST':
        form = SurveyQuestionForm(request.user, request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.save()
            request.session["msg"] = _('"%(question)s" is added.') %\
                                     {'question': request.POST['question']}
            return HttpResponseRedirect('/survey/%s/#row%s'\
                % (obj.surveyapp_id, obj.id))
        else:
            request.session["err_msg"] = _('Question is not added.')
            #surveyapp_id = request.POST['surveyapp']

    template = 'frontend/survey/survey_question_change.html'

    data = {
        'form': form,
        'surveyapp_id': surveyapp_id,
        'err_msg': request.session.get('err_msg'),
        'action': 'add'
    }
    request.session['err_msg'] = ''
    return render_to_response(template, data,
        context_instance=RequestContext(request))


@login_required
def survey_question_change(request, id):
    """Update survey question for the logged in user

    **Attributes**:

        * ``form`` - SurveyQuestionForm
        * ``template`` - frontend/survey/survey_question_change.html

    **Logic Description**:

        *
    """
    survey_que = SurveyQuestion.objects.get(pk=int(id))
    form = SurveyQuestionForm(request.user, instance=survey_que)
    request.session['err_msg'] = ''
    if request.GET.get('delete'):
        # perform delete
        surveyapp_id = survey_que.surveyapp_id
        survey_response_list = SurveyResponse.objects\
            .filter(surveyquestion=survey_que)
        for survey_resp in survey_response_list:
            survey_resp.delete()

        survey_que.delete()
        return HttpResponseRedirect('/survey/%s/' % (surveyapp_id))

    if request.method == 'POST':
        form = SurveyQuestionForm(request.user,
                                  request.POST,
                                  instance=survey_que)
        if form.is_valid():
            obj = form.save()
            return HttpResponseRedirect('/survey/%s/#row%s'\
                % (obj.surveyapp_id, obj.id))
        else:
            request.session["err_msg"] = _('Question is not added.')

    template = 'frontend/survey/survey_question_change.html'
    data = {
        'form': form,
        'surveyapp_id': survey_que.surveyapp_id,
        'survey_question_id': id,
        'module': current_view(request),
        'err_msg': request.session.get('err_msg'),
        'action': 'update',
    }
    request.session['err_msg'] = ''
    return render_to_response(template, data,
        context_instance=RequestContext(request))


@login_required
def survey_response_add(request):
    """Add new Survey for the logged in user

    **Attributes**:

        * ``form`` - SurveyResponseForm
        * ``template`` - frontend/survey/survey_response_change.html

    **Logic Description**:

        * Add a new survey response which will belong to the logged in user
          via the SurveyResponseForm & get redirected to the selected survey
    """
    surveyquestion_id = request.GET.get('surveyquestion_id')
    survey_que = SurveyQuestion.objects.get(pk=int(surveyquestion_id))
    form = SurveyResponseForm(request.user, survey_que.surveyapp_id,
                              initial={'surveyquestion': survey_que})
    request.session['err_msg'] = ''
    if request.method == 'POST':
        form = SurveyResponseForm(request.user,
            survey_que.surveyapp_id,
            request.POST)
        if form.is_valid():
            obj = form.save()
            request.session["msg"] = _('"%(key)s" is added.') %\
                                     {'key': request.POST['key']}
            return HttpResponseRedirect('/survey/%s/#row%s'\
                                % (obj.surveyquestion.surveyapp_id,
                                   obj.surveyquestion.id))
        else:
            form._errors["key"] = _("duplicate record key !")
            request.session["err_msg"] = _('Response is not added.')

    template = 'frontend/survey/survey_response_change.html'
    data = {
        'form': form,
        'surveyquestion_id': surveyquestion_id,
        'surveyapp_id': survey_que.surveyapp_id,
        'err_msg': request.session.get('err_msg'),
        'action': 'add'
    }
    request.session['err_msg'] = ''
    return render_to_response(template, data,
        context_instance=RequestContext(request))


@login_required
def survey_response_change(request, id):
    """Update survey question for the logged in user

    **Attributes**:

        * ``form`` - SurveyQuestionForm
        * ``template`` - frontend/survey/survey_question.html

    **Logic Description**:

        *
    """
    survey_resp = SurveyResponse.objects.get(pk=int(id))
    form = SurveyResponseForm(request.user,
        survey_resp.surveyquestion.surveyapp_id,
        instance=survey_resp)
    request.session['err_msg'] = ''
    if request.GET.get('delete'):
        # perform delete
        surveyapp_id = survey_resp.surveyquestion.surveyapp_id
        survey_resp.delete()
        return HttpResponseRedirect('/survey/%s/' % str(surveyapp_id))

    if request.method == 'POST':
        form = SurveyResponseForm(request.user,
                                  survey_resp.surveyquestion.surveyapp_id,
                                  request.POST,
                                  instance=survey_resp)
        if form.is_valid():
            obj = form.save()
            return HttpResponseRedirect('/survey/%s/#row%s'\
                            % (obj.surveyquestion.surveyapp_id,
                               obj.surveyquestion.id))
        else:
            duplicate_count =\
            SurveyResponse.objects.filter(key=request.POST['key'],
                surveyquestion=survey_resp.surveyquestion).count()
            if request.POST['key'] == survey_resp.key:
                if duplicate_count >= 1:
                    form._errors["key"] = _("duplicate record key !")
            request.session["err_msg"] = _('Response is not added.')

    template = 'frontend/survey/survey_response_change.html'
    data = {
        'form': form,
        'surveyquestion_id': survey_resp.surveyquestion_id,
        'surveyapp_id': survey_resp.surveyquestion.surveyapp_id,
        'survey_response_id': id,
        'module': current_view(request),
        'action': 'update',
        'err_msg': request.session.get('err_msg'),
    }
    request.session['err_msg'] = ''
    return render_to_response(template, data,
        context_instance=RequestContext(request))


@permission_required('survey.change_survey', login_url='/')
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

    survey_response_list = {}
    for survey_que in survey_que_list:
        res_list = SurveyResponse.objects\
            .filter(surveyquestion=survey_que).order_by('key')
        if res_list:
            # survey question response
            survey_response_list['%s' % survey_que.id] = res_list

    form = SurveyForm(instance=survey)

    if request.method == 'POST':
        if request.POST.get('delete'):
            survey_del(request, object_id)
            return HttpResponseRedirect('/survey/')
        else:
            form = SurveyForm(request.POST, request.user, instance=survey)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%(name)s" is updated.')\
                    % {'name': request.POST['name']}
                return HttpResponseRedirect('/survey/')

    template = 'frontend/survey/survey_change.html'

    data = {
        'survey_obj_id': object_id,
        'survey_que_list': survey_que_list,
        'survey_response_list': survey_response_list,
        'module': current_view(request),
        'action': 'update',
        'form': form,
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
        context_instance=RequestContext(request))


def survey_cdr_daily_report(kwargs, from_query, select_group_query):
    """Get survey voip call daily report"""
    max_duration = 0
    total_duration = 0
    total_calls = 0
    total_avg_duration = 0

    # Daily Survey VoIP call report
    select_data =\
        {"starting_date": "SUBSTR(CAST(starting_date as CHAR(30)),1,10)"}

    # Get Total from VoIPCall table for Daily Call Report
    total_data = VoIPCall.objects.extra(select=select_data)\
        .values('starting_date')\
        .filter(**kwargs).annotate(Count('starting_date'))\
        .annotate(Sum('duration'))\
        .annotate(Avg('duration'))\
        .order_by('-starting_date')\
        .extra(
            select={
                'question_response': select_group_query + from_query,
                },
        )

    # Following code will count total voip calls, duration
    if total_data.count() != 0:
        max_duration =\
            max([x['duration__sum'] for x in total_data])
        total_duration =\
            sum([x['duration__sum'] for x in total_data])
        total_calls =\
            sum([x['starting_date__count'] for x in total_data])
        total_avg_duration =\
            (sum([x['duration__avg']\
                for x in total_data])) / total_data.count()

    survey_cdr_daily_data = {
        'total_data': total_data,
        'total_duration': total_duration,
        'total_calls': total_calls,
        'total_avg_duration': total_avg_duration,
        'max_duration': max_duration,
    }

    return survey_cdr_daily_data


def get_survey_result(survey_result_kwargs):
    """Get survey result report from selected survey campaign"""
    survey_result = SurveyCampaignResult.objects\
        .filter(**survey_result_kwargs)\
        .values('question', 'response', 'record_file')\
        .annotate(Count('response'))\
        .annotate(Count('record_file'))\
        .distinct()\
        .order_by('question')

    return survey_result


def survey_audio_recording(audio_file):
    """audio player tag for frontend for survey recording

    >>> survey_audio_recording('')
    u'<br/><span class="label label-important">No recording</span>'
    """
    if audio_file:
        file_url = settings.MEDIA_URL + 'recording/' + str(audio_file)
        player_string = '<ul class="playlist"><li style="width:auto;">\
            <a href="%s">%s</a></li></ul>' % (file_url,
                                              os.path.basename(file_url))
        return player_string
    else:
        return '<br/><span class="label label-important">%s</span>' %\
               _('No recording')


@permission_required('survey.view_survey_report', login_url='/')
@login_required
def survey_report(request):
    """Survey detail report for the logged in user

    **Attributes**:

        * ``template`` - frontend/survey/survey_report.html

    **Logic Description**:

        * List all survey_report which belong to the logged in user.
    """
    tday = datetime.today()
    from_date = tday.strftime("%Y-%m-%d")
    to_date = tday.strftime("%Y-%m-%d")
    form = SurveyDetailReportForm(request.user,
        initial={'from_date': from_date,
                 'to_date': to_date})
    search_tag = 1
    survey_result = ''
    col_name_with_order = []
    survey_cdr_daily_data = {
        'total_data': '',
        'total_duration': '',
        'total_calls': '',
        'total_avg_duration': '',
        'max_duration': '',
    }
    PAGE_SIZE = settings.PAGE_SIZE
    action = 'tabs-1'

    if request.method == 'POST':
        #search_tag = 1
        form = SurveyDetailReportForm(request.user, request.POST)
        if form.is_valid():
            # set session var value
            request.session['session_from_date'] = ''
            request.session['session_to_date'] = ''
            request.session['session_campaign_id'] = ''
            request.session['session_surveycalls'] = ''
            request.session['session_survey_result'] = ''
            request.session['session_survey_cdr_daily_data'] = {}

            if "from_date" in request.POST:
                # From
                from_date = request.POST['from_date']
                start_date = datetime(int(from_date[0:4]),
                    int(from_date[5:7]),
                    int(from_date[8:10]),
                    0, 0, 0, 0)
                request.session['session_from_date'] = from_date

            if "to_date" in request.POST:
                # To
                to_date = request.POST['to_date']
                end_date = datetime(int(to_date[0:4]),
                    int(to_date[5:7]),
                    int(to_date[8:10]),
                    23, 59, 59, 999999)
                request.session['session_to_date'] = to_date

            campaign_id = variable_value(request, 'campaign')
            if campaign_id:
                request.session['session_campaign_id'] = campaign_id
    else:
        rows = []
        campaign_id = ''

    try:
        if request.GET.get('page') or request.GET.get('sort_by'):
            from_date = request.session.get('session_from_date')
            to_date = request.session.get('session_to_date')
            campaign_id = request.session.get('session_campaign_id')
            search_tag = request.session.get('session_search_tag')
        else:
            from_date
    except NameError:
        tday = datetime.today()
        from_date = tday.strftime('%Y-%m-01')
        last_day = ((datetime(tday.year, tday.month, 1, 23, 59, 59, 999999) +\
                     relativedelta(months=1)) -\
                    relativedelta(days=1)).strftime('%d')
        to_date = tday.strftime('%Y-%m-' + last_day)
        search_tag = 0

        # unset session var value
        request.session['session_from_date'] = from_date
        request.session['session_to_date'] = to_date
        request.session['session_campaign_id'] = ''
        request.session['session_surveycalls'] = ''
        request.session['session_survey_result'] = ''
        request.session['session_search_tag'] = search_tag

    start_date = datetime(int(from_date[0:4]),
        int(from_date[5:7]),
        int(from_date[8:10]),
        0, 0, 0, 0)
    end_date = datetime(int(to_date[0:4]),
        int(to_date[5:7]),
        int(to_date[8:10]),
        23, 59, 59, 999999)

    kwargs = {}
    kwargs['user'] = request.user
    kwargs['disposition__exact'] = 'ANSWER'

    survey_result_kwargs = {}
    survey_result_kwargs['callrequest__user'] = request.user

    if start_date and end_date:
        kwargs['starting_date__range'] = (start_date, end_date)
        survey_result_kwargs['created_date__range'] = (start_date, end_date)
    if start_date and end_date == '':
        kwargs['starting_date__gte'] = start_date
        survey_result_kwargs['created_date__gte'] = start_date
    if start_date == '' and end_date:
        kwargs['starting_date__lte'] = end_date
        survey_result_kwargs['created_date__lte'] = end_date

    try:
        campaign_id = int(campaign_id)
        campaign_obj = Campaign.objects.get(id=campaign_id)
        survey_result_kwargs['campaign'] = campaign_obj
        survey_result_kwargs['callrequest__status'] = 4

        # Get survey result report from session
        # while using pagination & sorting
        if request.GET.get('page') or request.GET.get('sort_by'):
            survey_result = request.session['session_survey_result']
        else:
            survey_result = get_survey_result(survey_result_kwargs)
            request.session['session_survey_result'] = survey_result

        kwargs['callrequest__campaign'] = campaign_obj

        # sorting on column
        col_name_with_order = {}
        sort_field = variable_value(request, 'sort_by')
        if not sort_field:
            sort_field = '-starting_date'  # default sort field
        else:
            if "-" in sort_field:
                col_name_with_order['sort_field'] = sort_field[1:]
            else:
                col_name_with_order['sort_field'] = sort_field

        # List of Survey VoIP call report
        from_query =\
            'FROM survey_surveycampaignresult '\
            'WHERE survey_surveycampaignresult.callrequest_id = '\
            'dialer_callrequest.id '
        select_group_query = 'SELECT group_concat(CONCAT_WS("*|*", question, response, record_file) SEPARATOR "-|-") '

        rows = VoIPCall.objects\
            .only('starting_date', 'phone_number', 'duration', 'disposition')\
            .filter(**kwargs)\
            .extra(
                select={
                    'question_response': select_group_query + from_query
                },
            ).order_by(sort_field)

        request.session['session_surveycalls'] = rows

        # Get daily report from session while using pagination & sorting
        if request.GET.get('page') or request.GET.get('sort_by'):
            survey_cdr_daily_data =\
            request.session['session_survey_cdr_daily_data']
        else:
            survey_cdr_daily_data = survey_cdr_daily_report(kwargs,
                from_query,
                select_group_query)
            request.session['session_survey_cdr_daily_data'] =\
            survey_cdr_daily_data
    except:
        rows = []
        if request.method == 'POST':
            request.session["err_msg"] =\
                _('No campaign attached with survey.')

    template = 'frontend/survey/survey_report.html'

    data = {
        'rows': rows,
        'PAGE_SIZE': PAGE_SIZE,
        'col_name_with_order': col_name_with_order,
        'total_data': survey_cdr_daily_data['total_data'],
        'total_duration': survey_cdr_daily_data['total_duration'],
        'total_calls': survey_cdr_daily_data['total_calls'],
        'total_avg_duration': survey_cdr_daily_data['total_avg_duration'],
        'max_duration': survey_cdr_daily_data['max_duration'],
        'module': current_view(request),
        'msg': request.session.get('msg'),
        'err_msg': request.session.get('err_msg'),
        'notice_count': notice_count(request),
        'form': form,
        'survey_result': survey_result,
        'action': action,
        'search_tag': search_tag,
        'start_date': start_date,
        'end_date': end_date,
    }
    request.session['msg'] = ''
    request.session['err_msg'] = ''
    return render_to_response(template, data,
        context_instance=RequestContext(request))


@login_required
def export_surveycall_report(request):
    """Export CSV file of Survey VoIP call record

    **Important variable**:

        * ``request.session['surveycall_record_qs']`` - stores survey voipcall
            query set

    **Exported fields**: ['starting_date', 'phone_number', 'duration',
                          'disposition', 'survey results']
    """

    # get the response object, this can be used as a stream.
    response = HttpResponse(mimetype='text/csv')
    # force download.
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    # the csv writer
    writer = csv.writer(response)

    qs = request.session['session_surveycalls']

    campaign_id = request.session['session_campaign_id']
    campaign_obj = Campaign.objects.get(pk=campaign_id)
    column_list = ['starting_date', 'destination', 'duration',
                   'disposition']

    survey_qst = False
    if str(campaign_obj.content_type) == 'Survey':
        survey_qst = SurveyQuestion.objects\
            .filter(surveyapp_id=int(campaign_obj.object_id))
        for i in survey_qst:
            column_list.append(str(i.question.replace(',', ' ')))
    writer.writerow(column_list)

    for i in qs:
        result_row_list = [
            i.starting_date,
            i.phone_number,
            i.duration,
            i.disposition,
            ]
        if survey_qst:
            for qst in survey_qst:
                result_row_list.append(
                    export_question_result(i.question_response,
                        qst.question))
        writer.writerow(result_row_list)
    return response
