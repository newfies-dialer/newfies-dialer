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
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Sum, Avg, Count
from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.template.context import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from dialer_campaign.models import Campaign, Subscriber
from dialer_campaign.views import notice_count
from dialer_campaign.constants import SUBSCRIBER_STATUS
from dialer_cdr.models import Callrequest, VoIPCall, CALLREQUEST_STATUS
from dialer_cdr.constants import VOIPCALL_DISPOSITION
from survey2.models import Survey_template, Survey, Section_template, Section,\
    Branching_template, Branching,\
    Result, ResultAggregate
from survey2.forms import SurveyForm, VoiceSectionForm,\
    MultipleChoiceSectionForm, RatingSectionForm,\
    EnterNumberSectionForm, RecordMessageSectionForm,\
    PatchThroughSectionForm, BranchingForm, PhrasingForm,\
    SurveyDetailReportForm
from survey2.constants import SECTION_TYPE
from utils.helper import grid_common_function, get_grid_update_delete_link
from common.common_functions import variable_value, current_view, ceil_strdate
from datetime import datetime
from dateutil.relativedelta import relativedelta
import commands
import hashlib
import csv
import os


testdebug = False  # TODO: Change later


def templateformat(s, *args, **kwargs):
    while True:
        try:
            return s.format(*args, **kwargs)
        except KeyError as e:
            e = e.args[0]
            kwargs[e] = "{%s}" % e


def placeholder_replace(text, contact):
    """
    Replace place holders by tag value.
    This function will replace all the following tags :
        {last_name}
        {first_name}
        {email}
        {country}
        {city}
        {phone_number}
    as well as, get additional_vars, and replace json tags
    """
    text = str(text).lower()
    context = {'last_name': contact.last_name,
               'first_name': contact.first_name,
               'email': contact.email,
               'country': contact.country,
               'city': contact.city,
               'phone_number': contact.contact,
                }
    for index in contact.additional_vars:
        context[index] = contact.additional_vars[index]

    return templateformat(text, **context)


def getaudio_acapela(text, tts_language='en'):
    """
    Run Acapela Text2Speech and return audio url
    """
    import acapela
    DIRECTORY = settings.MEDIA_ROOT + '/tts/'
    if not tts_language:
        tts_language = 'en'
    domain = Site.objects.get_current().domain
    tts_acapela = acapela.Acapela(
        settings.ACCOUNT_LOGIN, settings.APPLICATION_LOGIN,
        settings.APPLICATION_PASSWORD, settings.SERVICE_URL,
        settings.QUALITY, DIRECTORY)
    tts_acapela.prepare(
        text, tts_language, settings.ACAPELA_GENDER,
        settings.ACAPELA_INTONATION)
    output_filename = tts_acapela.run()
    audiofile_url = domain + settings.MEDIA_URL +\
                    'tts/' + output_filename
    return audiofile_url


#TODO: Use find_branching
def find_branching(p_section, DTMF):
    """
    function help to find the next branching of a section based on the key pressed
    or result entered
    """
    print "find branching"


def set_aggregate_result(obj_callrequest, obj_p_section, response, RecordingDuration):
    """
    save the aggregate result for the campaign / survey
    """
    if RecordingDuration:
        try:
            # recording duration 0 - 20 seconds ; 20 - 40 seconds ; 40 - 60 seconds
            if int(RecordingDuration) > 0 and int(RecordingDuration) <= 20:
                response = 'recording 0 - 20 seconds'
            elif int(RecordingDuration) > 20 and int(RecordingDuration) <= 40:
                response = 'recording 21 - 40 seconds'
            elif int(RecordingDuration) > 40 and int(RecordingDuration) <= 60:
                response = 'recording 41 - 60 seconds'
            elif int(RecordingDuration) > 60 and int(RecordingDuration) <= 90:
                response = 'recording 61 - 90 seconds'
            elif int(RecordingDuration) > 90:
                response = 'recording > 90 seconds'
        except:
            response = 'error to detect recording duration'

    try:
        #Insert ResultAggregate
        result = ResultAggregate(
            campaign=obj_callrequest.campaign,
            survey_id=obj_callrequest.object_id,
            section=obj_p_section,
            response=response,
            count=1
            )
        result.save()
    except IntegrityError:
        #Update ResultAggregate
        result = ResultAggregate.objects.get(
            campaign=obj_callrequest.campaign,
            survey_id=obj_callrequest.object_id,
            section=obj_p_section,
            response=response,
            )
        result.count = result.count + 1
        result.save()


def save_section_result(request, obj_callrequest, obj_p_section, DTMF):
    """
    save the result of a section
    """
    if not obj_p_section:
        return False

    if obj_p_section.type == SECTION_TYPE.RECORD_MSG_SECTION:
        #RECORD_MSG_SECTION
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
        #TODO: Find more elegant way to do an UPSERT
        try:
            #Insert Result
            result = Result(
                callrequest=obj_callrequest,
                section=obj_p_section,
                record_file=RecordFile,
                recording_duration=RecordingDuration,
                )
            result.save()
            #Save aggregated result
            set_aggregate_result(obj_callrequest, obj_p_section, DTMF, RecordingDuration)

            return "Save new result RecordFile (section:%d - record_file:%s)\n" % \
                (obj_p_section.id, RecordFile)
        except IntegrityError:
            #Update Result
            result = Result.objects.get(
                callrequest=obj_callrequest,
                section=obj_p_section
                )
            result.record_file = RecordFile
            result.recording_duration = RecordingDuration
            result.save()
            #Save aggregated result
            set_aggregate_result(obj_callrequest, obj_p_section, DTMF, RecordingDuration)

            return "Update result RecordFile (section:%d - response:%s)\n" % \
                (obj_p_section.id, RecordFile)

    elif DTMF and len(DTMF) > 0 and \
        (obj_p_section.type == SECTION_TYPE.MULTI_CHOICE or \
        obj_p_section.type == SECTION_TYPE.RATING_SECTION or \
        obj_p_section.type == SECTION_TYPE.ENTER_NUMBER_SECTION):

        if obj_p_section.type == SECTION_TYPE.MULTI_CHOICE:
            #Get value for the DTMF from obj_p_section.key_X
            if DTMF == '0':
                if obj_p_section.key_0:
                    DTMF = obj_p_section.key_0
            elif DTMF == '1':
                if obj_p_section.key_1:
                    DTMF = obj_p_section.key_1
            elif DTMF == '2':
                if obj_p_section.key_2:
                    DTMF = obj_p_section.key_2
            elif DTMF == '3':
                if obj_p_section.key_3:
                    DTMF = obj_p_section.key_3
            elif DTMF == '4':
                if obj_p_section.key_4:
                    DTMF = obj_p_section.key_4
            elif DTMF == '5':
                if obj_p_section.key_5:
                    DTMF = obj_p_section.key_5
            elif DTMF == '6':
                if obj_p_section.key_6:
                    DTMF = obj_p_section.key_6
            elif DTMF == '7':
                if obj_p_section.key_7:
                    DTMF = obj_p_section.key_7
            elif DTMF == '8':
                if obj_p_section.key_8:
                    DTMF = obj_p_section.key_8
            elif DTMF == '9':
                if obj_p_section.key_9:
                    DTMF = obj_p_section.key_9
        try:
            #Save result
            result = Result(
                callrequest=obj_callrequest,
                section=obj_p_section,
                response=DTMF)
            result.save()
            #Save aggregated result
            set_aggregate_result(obj_callrequest, obj_p_section, DTMF, False)

            return "Save new result (section:%d - response:%s)\n" % \
                (obj_p_section.id, DTMF)
        except IntegrityError:
            #Update Result
            result = Result.objects.get(
                callrequest=obj_callrequest,
                section=obj_p_section
                )
            result.response = DTMF
            result.save()
            #Save aggregated result
            set_aggregate_result(obj_callrequest, obj_p_section, DTMF, False)

            return "Update result (section:%d - response:%s)\n" % \
                (obj_p_section.id, DTMF)


@csrf_exempt
def survey_finitestatemachine(request):
    """
    Survey Fine State Machine
    """
    current_state = None
    next_state = None
    delcache = False
    overstate = False
    debug_outp = ''

    #Load Plivo Post parameters
    opt_ALegRequestUUID = request.POST.get('ALegRequestUUID')
    opt_CallUUID = request.POST.get('CallUUID')
    DTMF = request.POST.get('Digits')
    #print "DTMF=%s - opt_CallUUID=%s" % (DTMF, opt_CallUUID)

    if testdebug:
        #implemented to test in browser
        #http://127.0.0.1:8000/survey_finitestatemachine/?ALegRequestUUID=1be691e0-1a47-11e2-b556-00231470a30c&Digits=1&RecordFile=tesfilename.mp3&RecordingDuration=20
        if not opt_ALegRequestUUID:
            opt_ALegRequestUUID = request.GET.get('ALegRequestUUID')
        if not opt_CallUUID:
            opt_CallUUID = request.GET.get('CallUUID')
        if not opt_CallUUID:
            opt_CallUUID = opt_ALegRequestUUID
        if not DTMF:
            DTMF = request.GET.get('Digits')
        delcache = request.GET.get('delcache')
        overstate = request.GET.get('overstate')
        #print "DTMF=%s - opt_CallUUID=%s" % (DTMF, opt_CallUUID)

    if not opt_ALegRequestUUID:
        return HttpResponse(content="Error: missing parameter ALegRequestUUID",
                            status=400)

    #Create the keys to store the cache
    key_state = "%s_state" % opt_CallUUID
    key_complete = "%s_complete" % opt_CallUUID
    key_p_section = "%s_p_section" % opt_CallUUID  # Previous section
    key_survey = "%s_survey_id" % opt_CallUUID

    #remove the current key state in debug mode by passing delcache setting
    if testdebug and delcache and delcache == '1':
        debug_outp += "delete state and key_survey = %s <br/>" % str(key_survey)
        cache.delete(key_state)
        cache.delete(key_survey)
        cache.delete(key_complete)

    #Retrieve the values of the keys
    current_state = cache.get(key_state)
    current_completion = cache.get(key_complete)
    debug_outp += "Get key_state:%s value current_state:%s \n" % \
        (key_state, str(current_state))
    #check if we defined an debug setting to overwrite current_state
    if overstate and len(overstate) > 0:
        debug_outp += "OVERSTATE ACTIVATED<br/>------------------<br/>\n"
        current_state = int(overstate)
    survey_id = cache.get(key_survey)
    obj_p_section = False

    #If there is no current state, it means we are starting the we set key_state and key_p_section to 0
    #key_p_section is the previous key section
    if not current_state:
        current_state = 0
        debug_outp += "** STARTING CALL **<br/>"
        debug_outp += "[INFO] - No current_state (%s) <br/>" % str(current_state)
        cache.set(key_state, 0, 21600)  # 21600 seconds = 6 hours
        cache.set(key_p_section, 0, 21600)  # 21600 seconds = 6 hours
    else:
        debug_outp += "** CALL IN PROCESS ** current_state (%s) <br/>" % str(current_state)
        p_section = cache.get(key_p_section)
        if p_section:
            #Get previous Section
            try:
                obj_p_section = Section.objects.get(id=p_section)
            except Section.DoesNotExist:
                html = '<Response><Hangup/></Response>'
                if testdebug:
                    return HttpResponse(escape(html))
                else:
                    return HttpResponse(html)

    try:
        obj_callrequest = Callrequest.objects.get(request_uuid=opt_ALegRequestUUID)
    except:
        return HttpResponse(content="Error: No Callrequest", status=400)

    survey_id = obj_callrequest.object_id
    cache.set(key_survey, survey_id, 21600)  # 21600 seconds = 6 hours

    if current_state == 0:
        obj_callrequest.status = CALLREQUEST_STATUS.IN_PROGRESS
        obj_callrequest.aleg_uuid = opt_CallUUID
        obj_callrequest.save()
        debug_outp += "Callrequest Saves (IN_PROGRESS) <br/>"

    debug_outp += "current_state = %s <br/>" % str(current_state)
    debug_outp += "Previous Section = %s <br/>" % str(obj_p_section)

    #Get list of Section
    list_section = Section.objects.filter(survey=survey_id).order_by('order')

    #Set default exist action
    exit_action = False

    #Save Result
    outp_result = save_section_result(request, obj_callrequest, obj_p_section, DTMF)
    if outp_result:
        debug_outp += outp_result

    if obj_p_section and \
        (obj_p_section.type == SECTION_TYPE.MULTI_CHOICE or \
        obj_p_section.type == SECTION_TYPE.RATING_SECTION or \
        obj_p_section.type == SECTION_TYPE.ENTER_NUMBER_SECTION):
        #Handle dtmf received, set the current state
        #Check if we receive a DTMF for the previous section then store the result

        exit_action = 'DTMF'
        #Get list of responses of the previous Section
        try:
            branching = Branching.objects.get(
                keys=DTMF,
                section=obj_p_section)
        except Branching.DoesNotExist:
            if DTMF and len(DTMF) > 0:
                #There is a DTMF so we can check if there is any
                try:
                    #DTMF doesn't have any branching so let's check for any
                    branching = Branching.objects.get(
                        keys='any',
                        section=obj_p_section)
                    exit_action = 'ANY'
                except Branching.DoesNotExist:
                    branching = False
            else:
                #No DTMF so it can be a timeout branching
                try:
                    #DTMF doesn't have any branching so let's check for timeout
                    branching = Branching.objects.get(
                        keys='timeout',
                        section=obj_p_section)
                    exit_action = 'TIMEOUT'
                except Branching.DoesNotExist:
                    branching = False

        #if there is a response for this DTMF then reset the current_state
        if branching and branching.goto:
            l = 0
            for section in list_section:
                #this is not very elegant mechanism, it allows us to know where we are
                #in the section list (order) and what should be the current state based
                #on what the user entered
                if section.id == branching.goto.id:
                    current_state = l
                    #print "Found it (%d) (l=%d)!" % (section.id, l)
                    break
                l = l + 1

    debug_outp += "EXIT ACTION ::> %s <br/>" % str(exit_action)
    #Transition go to next state
    next_state = current_state + 1

    cache.set(key_state, next_state, 21600)
    debug_outp += "Saved state in Cache - next_state (%s = %s) <br/>" % (key_state, next_state)

    try:
        list_section[current_state]
        #set previous section
        p_section = list_section[current_state].id
        cache.set(key_p_section, p_section, 21600)
    except IndexError:
        html = '<Response><Hangup/></Response>'
        if testdebug:
            return HttpResponse(escape(html))
        else:
            return HttpResponse(html)

    #retrieve the basename of the url
    url = settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL
    slashparts = url.split('/')
    url_basename = '/'.join(slashparts[:3])

    if list_section[current_state].audiofile and list_section[current_state].audiofile.audio_file.url:
        #Audio file
        audio_file_url = url_basename + list_section[current_state].audiofile.audio_file.url
        html_play = "<Play>%s</Play>" % audio_file_url
    else:
        #Replace place holders by tag value
        phrasing = placeholder_replace(list_section[current_state].phrasing,
                                       obj_callrequest.subscriber.contact)
        #Text2Speech
        if settings.TTS_ENGINE != 'ACAPELA':
            html_play = "<Speak>%s</Speak>" % phrasing
        else:
            audio_url = getaudio_acapela(phrasing,
                                         obj_callrequest.content_object.tts_language)
            html_play = "<Play>%s</Play>" % audio_url

    #Invalid Audio URL
    if list_section[current_state].invalid_audiofile \
        and list_section[current_state].invalid_audiofile.audio_file.url:
        #Audio file
        invalid_audiourl = url_basename + list_section[current_state].invalid_audiofile.audio_file.url
        invalid_input = ' invalidDigitsSound="%s"' % invalid_audiourl
    else:
        invalid_input = ''

    #Get timeout
    try:
        timeout = int(list_section[current_state].timeout / 1000)
    except:
        timeout = settings.MENU_TIMEOUT
    #Get number of retries
    retries = list_section[current_state].retries
    if not retries:
        retries = 1

    debug_outp += "Check section state (%d) <br/>" % (list_section[current_state].type)

    #
    #We will now produce the restXML to power the IVR
    #for instance if it's a RECORD_MSG_SECTION, we will render an XML command output.
    #

    #Check if it's a completed section
    if list_section[current_state].completed \
        and (not current_completion or current_completion == 0):
        cache.set(key_complete, 1, 21600)  # 21600 seconds = 6 hours
        #Flag subscriber
        subscriber = Subscriber.objects.get(pk=obj_callrequest.subscriber.id)
        subscriber.status = SUBSCRIBER_STATUS.COMPLETED
        subscriber.save()
        #Flag Callrequest
        obj_callrequest.completed = True
        obj_callrequest.save()
        #Increment Campaign completed call
        campaign = Campaign.objects.get(pk=obj_callrequest.campaign.id)
        if not campaign.completed:
            campaign.completed = 1
        else:
            campaign.completed = campaign.completed + 1
        campaign.save()

    if list_section[current_state].type == SECTION_TYPE.PLAY_MESSAGE:
        #PLAY_MESSAGE
        number_digits = 1
        debug_outp += "PLAY_MESSAGE<br/>------------------<br/>"
        html =\
        '<Response>\n'\
        '   <GetDigits action="%s" method="GET" numDigits="%d" '\
        'retries="1" validDigits="0123456789" timeout="%s" '\
        'finishOnKey="#">\n'\
        '       %s\n'\
        '   </GetDigits>\n'\
        '   <Redirect>%s</Redirect>\n'\
        '</Response>' % (
            settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL,
            number_digits,
            timeout,
            html_play,
            settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL)

    elif list_section[current_state].type == SECTION_TYPE.HANGUP_SECTION:
        #HANGUP_SECTION
        debug_outp += "HANGUP_SECTION<br/>------------------<br/>"
        html = '<Response> %s <Hangup/> </Response>' % html_play

    elif list_section[current_state].type == SECTION_TYPE.MULTI_CHOICE:
        #MULTI_CHOICE
        number_digits = 1
        debug_outp += "MULTI_CHOICE<br/>------------------<br/>"
        html =\
        '<Response>\n'\
        '   <GetDigits action="%s" method="GET" numDigits="%d" '\
        'retries="%d" validDigits="0123456789" timeout="%s" '\
        'finishOnKey="#" %s>\n'\
        '       %s\n'\
        '   </GetDigits>\n'\
        '   <Redirect>%s</Redirect>\n'\
        '</Response>' % (
            settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL,
            number_digits,
            retries,
            timeout,
            invalid_input,
            html_play,
            settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL)

    elif list_section[current_state].type == SECTION_TYPE.RATING_SECTION:
        #RATING_SECTION
        try:
            number_digits = len(str(list_section[current_state].rating_laps))
        except:
            number_digits = 1
        debug_outp += "RATING_SECTION<br/>------------------<br/>"
        html =\
        '<Response>\n'\
        '   <GetDigits action="%s" method="GET" numDigits="%d" '\
        'retries="%d" validDigits="0123456789" timeout="%s" '\
        'finishOnKey="#" %s>\n'\
        '       %s\n'\
        '   </GetDigits>\n'\
        '   <Redirect>%s</Redirect>\n'\
        '</Response>' % (
            settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL,
            number_digits,
            retries,
            timeout,
            invalid_input,
            html_play,
            settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL)

    elif list_section[current_state].type == SECTION_TYPE.ENTER_NUMBER_SECTION:
        #ENTER_NUMBER_SECTION
        number_digits = list_section[current_state].number_digits
        if not number_digits:
            number_digits = 1
        debug_outp += "ENTER_NUMBER_SECTION<br/>------------------<br/>"
        html =\
        '<Response>\n'\
        '   <GetDigits action="%s" method="GET" numDigits="%d" '\
        'retries="%d" validDigits="0123456789" timeout="%s" '\
        'finishOnKey="#" %s>\n'\
        '       %s\n'\
        '   </GetDigits>\n'\
        '   <Redirect>%s</Redirect>\n'\
        '</Response>' % (
            settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL,
            number_digits,
            retries,
            timeout,
            invalid_input,
            html_play,
            settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL)

    elif list_section[current_state].type == SECTION_TYPE.RECORD_MSG_SECTION:
        #RECORD_MSG_SECTION
        debug_outp += "RECORD_MSG_SECTION<br/>------------------<br/>"
        #timeout : Seconds of silence before considering the recording complete
        html =\
        '<Response>\n'\
        '   %s\n'\
        '   <Record maxLength="120" finishOnKey="*#" action="%s" '\
        'method="GET" filePath="%s" timeout="10"/>'\
        '</Response>' % (
            html_play,
            settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL,
            settings.FS_RECORDING_PATH)

    elif list_section[current_state].type == SECTION_TYPE.PATCH_THROUGH_SECTION:
        #PATCH_THROUGH_SECTION
        debug_outp += "PATCH_THROUGH_SECTION<br/>------------------<br/>"
        timelimit = obj_callrequest.timelimit
        callerid = obj_callrequest.callerid
        gatewaytimeouts = obj_callrequest.timeout
        gateways = obj_callrequest.aleg_gateway.gateways
        phonenumber = list_section[current_state].dial_phonenumber
        html =\
        '<Response>\n'\
        '   %s\n'\
        '   <Dial timeLimit="%s" callerId="%s" callbackUrl="%s">\n'\
        '   <Number gateways="%s" gatewayTimeouts="%s">'\
        '   %s </Number> '\
        '   </Dial>\n'\
        '   <Redirect>%s</Redirect>\n'\
        '</Response>' % (
            html_play,
            timelimit,
            callerid,
            settings.PLIVO_DEFAULT_DIALCALLBACK_URL,
            gateways,
            gatewaytimeouts,
            phonenumber,
            settings.PLIVO_DEFAULT_SURVEY_ANSWER_URL)

    else:
        # Hangup
        debug_outp += "Hangup<br/>------------------<br/>"
        html =\
        '<Response>\n'\
        '   %s\n'\
        '   <Hangup />'\
        '</Response>' % (html_play)
        next_state = current_state
        cache.set(key_state, next_state, 21600)

    if testdebug:
        return HttpResponse(debug_outp + escape(html))
    else:
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

    survey_list = Survey_template.objects\
        .values('id', 'name', 'description', 'updated_date')\
        .filter(user=request.user)

    count = survey_list.count()
    survey_list =\
        survey_list.order_by(sortorder_sign + sortname)[start_page:end_page]

    rows = [{'id': row['id'],
             'cell': ['<input type="checkbox" name="select" class="checkbox" value="%s" />' % (str(row['id'])),
                      row['name'],
                      row['description'],
                      row['updated_date'].strftime('%Y-%m-%d %H:%M:%S'),
                      get_grid_update_delete_link(request, row['id'],
                                                  'survey.change_surveyapp',
                                                  _('Update survey'),
                                                  'update') +
                      get_grid_update_delete_link(request, row['id'],
                                                  'survey.delete_surveyapp',
                                                  _('Delete survey'),
                                                  'delete'),
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
    template = 'frontend/survey2/survey_list.html'
    data = {
        'module': current_view(request),
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('survey2.add_survey', login_url='/')
@login_required
def survey_add(request):
    """Add new Survey for the logged in user

    **Attributes**:

        * ``form`` - SurveyForm
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
            return HttpResponseRedirect('/survey2/%s/' % (obj.id))
    template = 'frontend/survey2/survey_change.html'
    data = {
        'module': current_view(request),
        'form': form,
        'action': 'add',
    }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


def delete_section_branching(survey):
    """delete sections as well as branching
    which are belong to survey"""
    section_list = Section_template.objects.filter(survey=survey)
    if section_list:
        for section in section_list:
            branching_list = Branching_template.objects.filter(section=section)
            if branching_list:
                branching_list.delete()
    section_list.delete()
    return True


@permission_required('survey2.delete_survey', login_url='/')
@login_required
def survey_del(request, object_id):
    """Delete a survey for a logged in user

    **Attributes**:

        * ``object_id`` - Selected survey object
        * ``object_list`` - Selected survey objects

    **Logic Description**:

        * Delete selected the survey from the survey list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        survey = get_object_or_404(
            Survey_template, pk=object_id, user=request.user)
        # 1) delete survey
        request.session["msg"] = _('"%(name)s" is deleted.')\
                                 % {'name': survey.name}
        # delete sections as well as branching which are belong to survey
        delete_section_branching(survey)
        survey.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        try:
            # 1) delete survey
            survey_list = Survey_template.objects.filter(user=request.user)\
                .extra(where=['id IN (%s)' % values])
            if survey_list:
                for survey in survey_list:
                    delete_section_branching(survey)

            request.session["msg"] = _('%(count)s survey(s) are deleted.')\
                    % {'count': survey_list.count()}
            survey_list.delete()
        except:
            raise Http404

    return HttpResponseRedirect('/survey2/')


@permission_required('survey2.add_section', login_url='/')
@login_required
def section_add(request):
    """Add new Survey for the logged in user

    **Attributes**:

        * ``form`` - SurveyQuestionForm
        * ``template`` - frontend/survey/survey_question_change.html

    **Logic Description**:

        * Add a new survey which will belong to the logged in user
          via the SurveyForm & get redirected to the survey list
    """
    survey_id = request.GET.get('survey_id')
    survey = Survey_template.objects.get(pk=survey_id)
    form = VoiceSectionForm(request.user, initial={'survey': survey})

    request.session['err_msg'] = ''
    if request.method == 'POST':

        # Play message
        if int(request.POST.get('type')) == SECTION_TYPE.PLAY_MESSAGE\
            or int(request.POST.get('type')) == SECTION_TYPE.HANGUP_SECTION:
            form = VoiceSectionForm(request.user)
            if request.POST.get('add'):
                form = VoiceSectionForm(request.user, request.POST)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] = _('Section is added successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('add') is None:
                request.session["err_msg"] = True
                if int(request.POST.get('type')) == SECTION_TYPE.PLAY_MESSAGE:
                    form = VoiceSectionForm(request.user,
                        initial={'survey': survey,
                                 'type': SECTION_TYPE.PLAY_MESSAGE})
                else:
                    form = VoiceSectionForm(request.user,
                        initial={'survey': survey,
                                 'type': SECTION_TYPE.HANGUP_SECTION})

        # Multiple Choice Section
        if int(request.POST.get('type')) == SECTION_TYPE.MULTI_CHOICE:
            form = MultipleChoiceSectionForm(request.user)
            if request.POST.get('add'):
                form = MultipleChoiceSectionForm(request.user, request.POST)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] =\
                        _('Section is added successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('add') is None:
                request.session["err_msg"] = True
                form = MultipleChoiceSectionForm(
                    request.user, initial={'survey': survey,
                                           'type': SECTION_TYPE.MULTI_CHOICE})

        # Rating Section
        if int(request.POST.get('type')) == SECTION_TYPE.RATING_SECTION:
            form = RatingSectionForm(request.user)
            if request.POST.get('add'):
                form = RatingSectionForm(request.user, request.POST)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] =\
                        _('Section is added successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('add') is None:
                request.session["err_msg"] = True
                form = RatingSectionForm(request.user, initial={'survey': survey,
                                         'type': SECTION_TYPE.RATING_SECTION})

        # Enter Number Section
        if int(request.POST.get('type')) == SECTION_TYPE.ENTER_NUMBER_SECTION:
            form = EnterNumberSectionForm(request.user)
            if request.POST.get('add'):
                form = EnterNumberSectionForm(request.user, request.POST)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] =\
                        _('Section is added successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('add') is None:
                request.session["err_msg"] = True
                form = EnterNumberSectionForm(request.user, initial={'survey': survey,
                                              'type': SECTION_TYPE.ENTER_NUMBER_SECTION})

        # Record Message Section
        if int(request.POST.get('type')) == SECTION_TYPE.RECORD_MSG_SECTION:
            form = RecordMessageSectionForm(request.user)
            if request.POST.get('add'):
                form = RecordMessageSectionForm(request.user, request.POST)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] =\
                        _('Section is added successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('add') is None:
                request.session["err_msg"] = True
                form = RecordMessageSectionForm(request.user, initial={'survey': survey,
                                                'type': SECTION_TYPE.RECORD_MSG_SECTION})

        # Patch-Through Section
        if int(request.POST.get('type')) == SECTION_TYPE.PATCH_THROUGH_SECTION:
            form = PatchThroughSectionForm(request.user)
            if request.POST.get('add'):
                form = PatchThroughSectionForm(request.user, request.POST)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] =\
                        _('Section is added successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('add') is None:
                request.session["err_msg"] = True
                form = PatchThroughSectionForm(request.user, initial={'survey': survey,
                                               'type': SECTION_TYPE.PATCH_THROUGH_SECTION})

    template = 'frontend/survey2/section_change.html'

    data = {
        'form': form,
        'survey_id': survey_id,
        'err_msg': request.session.get('err_msg'),
        'action': 'add',
        'SECTION_TYPE': SECTION_TYPE,
    }
    request.session["msg"] = ''
    request.session['err_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('survey2.change_section', login_url='/')
@login_required
def section_change(request, id):
    """Update survey question for the logged in user

    **Attributes**:

        * ``form`` - SurveyQuestionForm
        * ``template`` - frontend/survey/survey_question_change.html

    **Logic Description**:

        *
    """
    section = get_object_or_404(Section_template,
                                pk=int(id),
                                survey__user=request.user)
    if section.type == SECTION_TYPE.PLAY_MESSAGE \
        or section.type == SECTION_TYPE.HANGUP_SECTION:
        #PLAY_MESSAGE & HANGUP_SECTION
        form = VoiceSectionForm(request.user, instance=section)
    elif section.type == SECTION_TYPE.MULTI_CHOICE:
        #MULTI_CHOICE
        form = MultipleChoiceSectionForm(request.user, instance=section)
    elif section.type == SECTION_TYPE.RATING_SECTION:
        #RATING_SECTION
        form = RatingSectionForm(request.user, instance=section)
    elif section.type == SECTION_TYPE.ENTER_NUMBER_SECTION:
        #ENTER_NUMBER_SECTION
        form = EnterNumberSectionForm(request.user, instance=section)
    elif section.type == SECTION_TYPE.RECORD_MSG_SECTION:
        #RECORD_MSG_SECTION
        form = RecordMessageSectionForm(request.user, instance=section)
    elif section.type == SECTION_TYPE.PATCH_THROUGH_SECTION:
        #PATCH_THROUGH_SECTION
        form = PatchThroughSectionForm(request.user, instance=section)

    request.session['err_msg'] = ''

    #TODO: See how to refactor this section
    if request.method == 'POST' and request.POST.get('type'):
        # Play message or Hangup Section
        if int(request.POST.get('type')) == SECTION_TYPE.PLAY_MESSAGE\
            or int(request.POST.get('type')) == SECTION_TYPE.HANGUP_SECTION:
            form = VoiceSectionForm(request.user, instance=section)
            if request.POST.get('update'):
                form = VoiceSectionForm(request.user,
                                        request.POST,
                                        instance=section)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] =\
                        _('Section is updated successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('update') is None:
                request.session["err_msg"] = True
                if int(request.POST.get('type')) == SECTION_TYPE.PLAY_MESSAGE:
                    form = VoiceSectionForm(
                        request.user, instance=section,
                        initial={'type': SECTION_TYPE.PLAY_MESSAGE})
                else:
                    form = VoiceSectionForm(
                        request.user, instance=section,
                        initial={'type': SECTION_TYPE.HANGUP_SECTION})

        # Multiple Choice Section
        if int(request.POST.get('type')) == SECTION_TYPE.MULTI_CHOICE:
            form = MultipleChoiceSectionForm(request.user, instance=section)
            if request.POST.get('update'):
                form = MultipleChoiceSectionForm(
                    request.user, request.POST, instance=section)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] =\
                        _('Section is updated successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('update') is None:
                request.session["err_msg"] = True
                form = MultipleChoiceSectionForm(
                    request.user, instance=section,
                    initial={'type': SECTION_TYPE.MULTI_CHOICE})

        # Rating Section
        if int(request.POST.get('type')) == SECTION_TYPE.RATING_SECTION:
            form = RatingSectionForm(request.user, instance=section)
            if request.POST.get('update'):
                form = RatingSectionForm(
                    request.user, request.POST, instance=section)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] =\
                        _('Section is updated successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('update') is None:
                request.session["err_msg"] = True
                form = RatingSectionForm(
                    request.user, instance=section,
                    initial={'type': SECTION_TYPE.RATING_SECTION})

        # Enter Number Section
        if int(request.POST.get('type')) == SECTION_TYPE.ENTER_NUMBER_SECTION:
            form = EnterNumberSectionForm(request.user, instance=section)
            if request.POST.get('update'):
                form = EnterNumberSectionForm(
                    request.user, request.POST, instance=section)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] =\
                        _('Section is updated successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('update') is None:
                request.session["err_msg"] = True
                form = EnterNumberSectionForm(
                    request.user, instance=section,
                    initial={'type': SECTION_TYPE.ENTER_NUMBER_SECTION})

        # Record Message Section Section
        if int(request.POST.get('type')) == SECTION_TYPE.RECORD_MSG_SECTION:
            form = RecordMessageSectionForm(request.user, instance=section)
            if request.POST.get('update'):
                form = RecordMessageSectionForm(
                    request.user, request.POST, instance=section)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] =\
                        _('Section is updated successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('update') is None:
                request.session["err_msg"] = True
                form = RecordMessageSectionForm(
                    request.user, instance=section,
                    initial={'type': SECTION_TYPE.RECORD_MSG_SECTION})

        # Patch Through Section Section
        if int(request.POST.get('type')) == SECTION_TYPE.PATCH_THROUGH_SECTION:
            form = PatchThroughSectionForm(request.user, instance=section)
            if request.POST.get('update'):
                form = PatchThroughSectionForm(
                    request.user, request.POST, instance=section)
                if form.is_valid():
                    obj = form.save()
                    request.session["msg"] =\
                        _('Section is updated successfully.')
                    return HttpResponseRedirect('/survey2/%s/#row%s'
                                                % (obj.survey_id, obj.id))
                else:
                    request.session["err_msg"] = True

            if request.POST.get('update') is None:
                request.session["err_msg"] = True
                form = PatchThroughSectionForm(
                    request.user, instance=section,
                    initial={'type': SECTION_TYPE.PATCH_THROUGH_SECTION})

    template = 'frontend/survey2/section_change.html'
    data = {
        'form': form,
        'survey_id': section.survey_id,
        'section_id': section.id,
        'module': current_view(request),
        'err_msg': request.session.get('err_msg'),
        'action': 'update',
        'SECTION_TYPE': SECTION_TYPE,
    }
    request.session["msg"] = ''
    request.session['err_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('survey2.delete_section', login_url='/')
@login_required
def section_delete(request, id):
    section = get_object_or_404(
        Section_template, pk=int(id), survey__user=request.user)
    if request.GET.get('delete'):
        # perform delete
        survey_id = section.survey_id

        # Re-order section while deleting one section
        section_list_reorder = Section_template.objects\
            .filter(survey=section.survey)\
            .exclude(pk=int(id))
        for reordered in section_list_reorder:
            if section.order < reordered.order:
                reordered.order = reordered.order - 1
                reordered.save()

        # 1) delete branch belonging to a section
        branching_list = Branching_template.objects.filter(section=section)
        if branching_list:
            branching_list.delete()

        # 2) delete section
        section.delete()
        request.session["msg"] = _('Section is deleted successfully.')
        return HttpResponseRedirect('/survey2/%s/' % (survey_id))

    template = 'frontend/survey2/section_delete_confirmation.html'
    data = {
        'section_type': section.type,
        'section_id': section.id,
        'module': current_view(request),
    }
    return render_to_response(template, data,
        context_instance=RequestContext(request))


@permission_required('survey2.change_section', login_url='/')
@login_required
def section_phrasing_change(request, id):
    """Update survey question for the logged in user

    **Attributes**:

        * ``form`` - PhrasingForm
        * ``template`` - frontend/survey2/section_phrasing_change.html

    **Logic Description**:

        *
    """
    section = get_object_or_404(
        Section_template, pk=int(id), survey__user=request.user)

    form = PhrasingForm(instance=section)
    if request.method == 'POST':
        form = PhrasingForm(request.POST, instance=section)
        if form.is_valid():
            obj = form.save()
            request.session["msg"] = _('Phrasing is updated successfully.')
            return HttpResponseRedirect('/survey2/%s/#row%s'
                % (obj.survey_id, obj.id))
        else:
            request.session["err_msg"] = True

    template = 'frontend/survey2/section_phrasing_change.html'
    data = {
        'form': form,
        'survey_id': section.survey_id,
        'section_id': section.id,
        'module': current_view(request),
        'err_msg': request.session.get('err_msg'),
        'action': 'update',
    }
    request.session["msg"] = ''
    request.session['err_msg'] = ''
    return render_to_response(template, data,
        context_instance=RequestContext(request))


@login_required
def section_phrasing_play(request, id):
    """Play section  phrasing

    **Attributes**:


    **Logic Description**:

        * Create text file from section phrasing
        * Convert text file into wav file
    """
    section = get_object_or_404(
        Section_template, pk=int(id), survey__user=request.user)
    if section.phrasing:
        phrasing_text = section.phrasing
        phrasing_hexdigest = hashlib.md5(phrasing_text).hexdigest()
        file_path = '%s/tts/phrasing_%s' % \
                             (settings.MEDIA_ROOT, phrasing_hexdigest)
        audio_file_path = file_path + '.wav'
        text_file_path = file_path + '.txt'

        if not os.path.isfile(audio_file_path):
            #Write text to file
            text_file = open(text_file_path, "w")
            text_file.write(phrasing_text)
            text_file.close()

            #Convert file
            conv = 'flite -f "%s" -o "%s"' % (text_file_path, audio_file_path)
            response = commands.getoutput(conv)

        if os.path.isfile(audio_file_path):
            response = HttpResponse()
            f = open(audio_file_path, 'rb')
            response['Content-Type'] = 'audio/x-wav'
            response.write(f.read())
            f.close()
            return response

    raise Http404


@permission_required('survey2.add_branching', login_url='/')
@login_required
def section_branch_add(request):
    """Add branching on section for the logged in user

    **Attributes**:

        * ``form`` - BranchingForm
        * ``template`` - frontend/survey2/section_branch_change.html

    **Logic Description**:

        *

    """
    request.session['msg'] = ''
    form = ''
    section_survey_id = ''
    section_type = ''
    section_id = ''
    if request.GET.get('section_id'):
        section_id = request.GET.get('section_id')
        section = Section_template.objects.get(pk=int(section_id))
        section_survey_id = section.survey_id
        section_type = section.type
        form = BranchingForm(
            section.survey_id, section.id, initial={'section': section_id})
        if request.method == 'POST':
            form = BranchingForm(
                section.survey_id, section.id, request.POST)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('Branching is added successfully.')
                return HttpResponseRedirect('/survey2/%s/#row%s'
                                        % (section.survey_id, section_id))
            else:
                form._errors["keys"] = _("duplicate record keys with goto.")
                request.session["err_msg"] = True

    template = 'frontend/survey2/section_branch_change.html'
    data = {
        'form': form,
        'survey_id': section_survey_id,
        'section_type': section_type,
        'section_id': section_id,
        'module': current_view(request),
        'err_msg': request.session.get('err_msg'),
        'action': 'add',
        'SECTION_TYPE': SECTION_TYPE,
    }
    request.session["msg"] = ''
    request.session['err_msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@permission_required('survey2.change_branching', login_url='/')
@login_required
def section_branch_change(request, id):
    """Add branching on section for the logged in user

    **Attributes**:

        * ``form`` - BranchingForm
        * ``template`` - frontend/survey2/section_branch_change.html

    **Logic Description**:

        *

    """
    request.session['msg'] = ''
    if request.GET.get('delete'):
        # perform delete
        branching_obj = get_object_or_404(Branching_template, id=int(id),
                                          section__survey__user=request.user)
        survey_id = branching_obj.section.survey_id
        section_id = branching_obj.section_id
        branching_obj.delete()
        request.session["msg"] = _('Branching is deleted successfully.')
        return HttpResponseRedirect('/survey2/%s/#row%s'
                                    % (survey_id, section_id))

    branching = get_object_or_404(Branching_template, id=int(id),
                                  section__survey__user=request.user)
    form = BranchingForm(branching.section.survey_id,
                         branching.section_id,
                         instance=branching)
    if request.method == 'POST':
        form = BranchingForm(branching.section.survey_id,
                             branching.section_id,
                             request.POST,
                             instance=branching)
        if form.is_valid():
            form.save()
            request.session["msg"] = _('Branching is updated successfully.')
            return HttpResponseRedirect('/survey2/%s/#row%s'
                                        % (branching.section.survey_id,
                                           branching.section_id))
        else:
            form._errors["keys"] = _("duplicate record keys with goto.")
            request.session["err_msg"] = True

    template = 'frontend/survey2/section_branch_change.html'
    data = {
        'form': form,
        'survey_id': branching.section.survey_id,
        'section_type': branching.section.type,
        'section_id': branching.section.id,
        'branching_id': branching.id,
        'module': current_view(request),
        'err_msg': request.session.get('err_msg'),
        'action': 'update',
        'SECTION_TYPE': SECTION_TYPE,
    }
    request.session["msg"] = ''
    request.session['err_msg'] = ''
    return render_to_response(template, data,
        context_instance=RequestContext(request))


@permission_required('survey2.change_survey', login_url='/')
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
    survey = get_object_or_404(
        Survey_template, pk=object_id, user=request.user)

    section_list = Section_template.objects.filter(survey=survey).order_by('order')
    form = SurveyForm(instance=survey)
    branching_list = Branching_template.objects\
        .filter(section__survey=survey).order_by('id')

    branching_section_list = \
        branching_list.values_list('section_id', flat=True).distinct()

    if request.method == 'POST':
        if request.POST.get('delete'):
            survey_del(request, object_id)
            return HttpResponseRedirect('/survey2/')
        else:
            form = SurveyForm(request.POST, request.user, instance=survey)
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%(name)s" is updated.')\
                    % {'name': request.POST['name']}
                return HttpResponseRedirect('/survey2/')

    template = 'frontend/survey2/survey_change.html'

    data = {
        'survey_obj_id': object_id,
        'section_list': section_list,
        'branching_list': branching_list,
        'branching_section_list': branching_section_list,
        'module': current_view(request),
        'action': 'update',
        'form': form,
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
        'SECTION_TYPE': SECTION_TYPE,
    }
    request.session['msg'] = ''
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@login_required
def survey_view(request, object_id):
    """View locked survey

    **Logic Description**:

        * Update/delete selected survey from the survey list
          via SurveyForm & get redirected to survey list
    """
    survey = get_object_or_404(
        Survey, pk=object_id, user=request.user)

    section_list = Section.objects.filter(survey=survey).order_by('order')

    branching_list = Branching.objects\
        .filter(section__survey=survey).order_by('id')

    branching_section_list =\
        branching_list.values_list('section_id', flat=True).distinct()

    template = 'frontend/survey2/survey_view.html'

    data = {
        'survey_obj_id': object_id,
        'survey': survey,
        'section_list': section_list,
        'branching_list': branching_list,
        'branching_section_list': branching_section_list,
        'module': current_view(request),
        'action': 'view',
        'msg': request.session.get('msg'),
        'notice_count': notice_count(request),
        'SECTION_TYPE': SECTION_TYPE,
    }
    return render_to_response(template, data,
        context_instance=RequestContext(request))


def survey_cdr_daily_report(kwargs):
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
        .filter(**kwargs)\
        .annotate(Count('starting_date'))\
        .annotate(Sum('duration'))\
        .annotate(Avg('duration'))\
        .order_by('-starting_date')

    # Following code will count total voip calls, duration
    if total_data.count() != 0:
        max_duration =\
            max([x['duration__sum'] for x in total_data])
        total_duration =\
            sum([x['duration__sum'] for x in total_data])
        total_calls =\
            sum([x['starting_date__count'] for x in total_data])
        total_avg_duration =\
            (sum([x['duration__avg']
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
    survey_result = ResultAggregate.objects\
        .filter(**survey_result_kwargs)\
        .values('section__question', 'response', 'count')\
        .order_by('section')

    return survey_result


def survey_audio_recording(audio_file):
    """audio player tag for frontend for survey recording

    >>> survey_audio_recording('')
    u'<br/><span class="label label-important">No recording</span>'
    """
    if audio_file:
        file_url = '%srecording/%s' % (settings.MEDIA_URL, str(audio_file))
        player_string = '<ul class="playlist"><li style="width:auto;"> <a href="%s">%s</a></li></ul>' % \
            (file_url, os.path.basename(file_url))
        return player_string
    else:
        return '<br/><span class="label label-important">%s</span>' %\
               _('No recording')


@permission_required('survey2.view_survey_report', login_url='/')
@login_required
def survey_report(request):
    """
    Survey detail report for the logged in user

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
    campaign_obj = ''
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
                start_date = ceil_strdate(from_date, 'start')
                request.session['session_from_date'] = from_date

            if "to_date" in request.POST:
                # To
                to_date = request.POST['to_date']
                end_date = ceil_strdate(to_date, 'end')
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
        last_day = ((datetime(tday.year, tday.month, 1, 23, 59, 59, 999999) +
                     relativedelta(months=1)) -
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

    start_date = ceil_strdate(from_date, 'start')
    end_date = ceil_strdate(to_date, 'end')

    kwargs = {}
    kwargs['user'] = request.user
    kwargs['disposition__exact'] = VOIPCALL_DISPOSITION.ANSWER

    survey_result_kwargs = {}

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
        campaign_obj = Campaign.objects.get(id=int(campaign_id))
        survey_result_kwargs['campaign'] = campaign_obj

        survey_result = get_survey_result(survey_result_kwargs)
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
        rows = VoIPCall.objects\
            .only('starting_date', 'phone_number', 'duration', 'disposition', 'id')\
            .filter(**kwargs).order_by(sort_field)

        request.session['session_surveycalls'] = rows

        # Get daily report from session while using pagination & sorting
        if request.GET.get('page') or request.GET.get('sort_by'):
            survey_cdr_daily_data =\
                request.session['session_survey_cdr_daily_data']
            action = 'tabs-2'
        else:
            survey_cdr_daily_data = survey_cdr_daily_report(kwargs)
            request.session['session_survey_cdr_daily_data'] =\
                survey_cdr_daily_data
    except:
        rows = []
        if request.method == 'POST':
            request.session["err_msg"] =\
                _('No campaign attached with survey.')

    template = 'frontend/survey2/survey_report.html'

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
        'campaign_obj': campaign_obj,
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
    writer = csv.writer(response)

    qs = request.session['session_surveycalls']
    campaign_id = request.session['session_campaign_id']
    campaign_obj = Campaign.objects.get(pk=campaign_id)
    column_list = ['starting_date', 'destination', 'duration', 'disposition']

    survey_qst = False
    if str(campaign_obj.content_type) == 'Survey':
        survey_qst = Section.objects\
            .filter(survey_id=int(campaign_obj.object_id))
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
        writer.writerow(result_row_list)
    return response


@login_required
def survey_campaign_result(request, id):
    """Survey Campaign Result

    **Attributes**:

        * ``template`` - frontend/survey2/survey_campaign_result.html

    **Logic Description**:

        * List all survey result which belong to callrequest.
    """
    result = Result.objects\
                .filter(callrequest=VoIPCall.objects.get(pk=id).callrequest_id)\
                .order_by('section')
    template = 'frontend/survey2/survey_campaign_result.html'
    data = {
        'result': result,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    }
    request.session['msg'] = ''
    request.session['err_msg'] = ''
    return render_to_response(template, data,
        context_instance=RequestContext(request))
