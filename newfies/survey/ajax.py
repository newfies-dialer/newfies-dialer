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

from django.contrib.auth.models import User
from django.utils import simplejson
from django.utils import simplejson
from django.contrib.auth.decorators import login_required

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from survey.models import *
from survey.forms import SurveyQuestionForm, SurveyQuestionNewForm, SurveyResponseForm


def audio_msg_type(audio_message):
    if audio_message is None:
        return 2 # Text2Speech
    else:
        return 1 # Audio File


@login_required
@dajaxice_register
def survey_question_add_update(request, id, data, form_type, after_initial_save, record_id):
    """ Ajax method to update the question """
    dajax = Dajax()

    if form_type == 'old_form':
        form = SurveyQuestionForm(data)

        if after_initial_save == 1 and record_id:
            survey_question = SurveyQuestion.objects.get(pk=int(record_id))            
        else:            
            survey_question = SurveyQuestion.objects.get(pk=int(id))

        form = SurveyQuestionForm(data, instance=survey_question)

    if form_type == 'new_form':
        form = SurveyQuestionNewForm(request.user, data)

    if form.is_valid():
        if form_type == 'old_form':
            object = form.save(commit=False)
            audio_message = form.cleaned_data.get('audio_message')
            object.message_type = audio_msg_type(audio_message)
            object.save()
            
        if form_type == 'new_form':            
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user)
            obj.surveyapp = form.cleaned_data.get('surveyapp')
            audio_message = form.cleaned_data.get('audio_message')
            obj.message_type = audio_msg_type(audio_message)
            obj.type = form.cleaned_data.get('type')
            obj.save()
            dajax.assign('#id', 'value', obj.id)
        #dajax.alert("%s is successfully saved !!" % form.cleaned_data.get('question'))
    else:
        if form_type == 'new_form':
            dajax.remove_css_class('#new_survey_que_form_'+id+' input','error')
        if form_type == 'old_form':
            dajax.remove_css_class('#que_form_'+id+' input','error')
        dajax.alert("error")
    return dajax.json()


@login_required
@dajaxice_register
def survey_response_add_update(request, id, que_id, data, form_type, new_response_id):
    """ Ajax method to update the response """
    dajax = Dajax()
    
    # 1st check survey question id
    if int(que_id) != 0:
        try:
            SurveyQuestion.objects.get(pk=que_id)
        except:
            #dajax.alert("error : First Save your survey question !!")
            return dajax.json()

    if int(que_id) == 0:
        #dajax.alert("error : First Save your survey question !!")
        return dajax.json()

    if form_type == 'old_form':
        form = SurveyResponseForm(data)
        survey_response = SurveyResponse.objects.get(pk=int(id))
        form = SurveyResponseForm(data, instance=survey_response)

    if form_type == 'new_form':
        form = SurveyResponseForm(data)

        if int(new_response_id) != 0:
            survey_response = SurveyResponse.objects.get(pk=int(new_response_id))
            form = SurveyResponseForm(data, instance=survey_response)

    if form.is_valid():
        key = form.cleaned_data.get("key")
        keyvalue = form.cleaned_data.get('keyvalue')

        duplicate_count = 0
        # start checking of duplicate key
        if form_type == 'old_form':
            resp_obj = SurveyResponse.objects.get(pk=id)
            if resp_obj.key != key:
                duplicate_count = SurveyResponse.objects.filter(key=key,
                                                    surveyquestion=resp_obj.surveyquestion).count()

        if form_type == 'new_form':
            if que_id == 0: # without que id
                # get last inserted record
                surveyquestion = SurveyQuestion.objects.all().order_by('-id')[0]
            else: # with que id
                surveyquestion = SurveyQuestion.objects.get(pk=que_id)
            duplicate_count = SurveyResponse.objects.filter(key=key,
                                                    surveyquestion=surveyquestion).count()

        if duplicate_count >= 1 and form_type == 'old_form':
            #dajax.alert("error : (%s) duplicate record key & previous key (%s) is not changed!" % (key,
            #                                                                                       resp_obj.key))
            return dajax.json()

        if duplicate_count >= 1 and form_type == 'new_form' and int(new_response_id) == 0:
            #dajax.alert("error : (%s) duplicate record key !" % (key))
            return dajax.json()

        # end checking of duplicate key

        if form_type == 'old_form':
            form.save()
        if form_type == 'new_form':
            obj = form.save(commit=False)
            obj.surveyquestion = surveyquestion
            obj.save()
            dajax.assign('#new_response_id', 'value', obj.id)

        #dajax.alert("(%s - %s) is successfully saved !!" % (form.cleaned_data.get('key'),
        #                                                   form.cleaned_data.get('keyvalue')))
    else:
        if form_type == 'new_form':
            dajax.remove_css_class('#new_survey_que_form_'+id+' input','error')
        if form_type == 'old_form':
            dajax.remove_css_class('#que_form_'+id+' input','error')
        dajax.alert("error")
        for error in form.errors:
            dajax.add_css_class('#id_%s' % error,'error')

    return dajax.json()


@login_required
@dajaxice_register
def survey_question_delete(request, id):
    """Method to delete the question & its responses"""
    dajax = Dajax()
    try:
        survey_question = SurveyQuestion.objects.get(pk=int(id))
        que = survey_question.question
        survey_response_list = SurveyResponse.objects.filter(surveyquestion=survey_question)
        for survey_resp in survey_response_list:
            survey_resp.delete()
        survey_question.delete()
        #dajax.alert("(%s) is successfully deleted !!" % (que))
    except:
        dajax.alert("%s is not exist !!" % (id))
        for error in form.errors:
            dajax.add_css_class('#id_%s' % error,'error')
    return dajax.json()


@login_required
@dajaxice_register
def survey_response_delete(request, id):
    """Method to delete responses"""
    dajax = Dajax()
    try:
        survey_response = SurveyResponse.objects.get(pk=int(id))
        key = survey_response.key
        keyvalue = survey_response.keyvalue
        survey_response.delete()
        #dajax.alert("(%s - %s) is successfully deleted !!" % (key, keyvalue))
    except:
        dajax.alert("%s is not exist !!" % (id))
        for error in form.errors:
            dajax.add_css_class('#id_%s' % error,'error')
    return dajax.json()


@login_required
@dajaxice_register
def survey_question_sort(request, id, sort_order):
    dajax = Dajax()
    
    try:
        survey_question = SurveyQuestion.objects.get(pk=int(id))
        survey_question.order = sort_order
        survey_question.save()
        #dajax.alert("(%s) has been successfully sorted !!" % (survey_question.question))
    except:
        #dajax.alert("%s is not exist !!" % (id))
        for error in form.errors:
            dajax.add_css_class('#id_%s' % error,'error')
    return dajax.json()
