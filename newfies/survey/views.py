#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.conf import settings
from django.contrib.auth.decorators import login_required,\
    permission_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Sum, Avg, Count
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from django.utils.timezone import utc
from dialer_cdr.models import VoIPCall
from dialer_cdr.constants import CALL_DISPOSITION
from survey.models import Survey_template, Survey, Section_template, Section,\
    Branching_template, Branching, Result, ResultAggregate
from survey.forms import SurveyForm, PlayMessageSectionForm,\
    MultipleChoiceSectionForm, RatingSectionForm,\
    CaptureDigitsSectionForm, RecordMessageSectionForm,\
    CallTransferSectionForm, BranchingForm, ScriptForm,\
    SMSSectionForm, SurveyDetailReportForm, SurveyFileImport,\
    ConferenceSectionForm, SealSurveyForm
from survey.constants import SECTION_TYPE, SURVEY_COLUMN_NAME, SURVEY_CALL_RESULT_NAME,\
    SEALED_SURVEY_COLUMN_NAME
from survey.models import post_save_add_script
from survey.function_def import getaudio_acapela
from survey.function_def import getaudio_mstranslator
from django_lets_go.common_functions import striplist, ceil_strdate, getvar, unset_session_var,\
    get_pagination_vars
from mod_utils.helper import Export_choice
from datetime import datetime
from dateutil.relativedelta import relativedelta
import subprocess
import hashlib
import tablib
import csv
import os

testdebug = False
redirect_url_to_survey_list = '/module/survey/'


@permission_required('survey.view_survey', login_url='/')
@login_required
def survey_list(request):
    """SurveyApp list for the logged in user

    **Attributes**:

        * ``template`` - survey/list.html

    **Logic Description**:

        * List all surveys which belong to the logged in user.
    """
    sort_col_field_list = ['id', 'name', 'updated_date']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    survey_list = Survey_template.objects.filter(user=request.user).order_by(pag_vars['sort_order'])
    data = {
        'survey_list': survey_list,
        'total_survey': survey_list.count(),
        'SURVEY_COLUMN_NAME': SURVEY_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
        'msg': request.session.get('msg'),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('survey/survey_list.html', data, context_instance=RequestContext(request))


@permission_required('survey.add_survey', login_url='/')
@login_required
def survey_add(request):
    """Add new Survey for the logged in user

    **Attributes**:

        * ``form`` - SurveyForm
        * ``template`` - survey/change.html

    **Logic Description**:

        * Add a new survey which will belong to the logged in user
          via the SurveyForm & get redirected to the survey list
    """
    form = SurveyForm(request.POST or None)
    if form.is_valid():
        obj = form.save(user=request.user)
        request.session["msg"] = _('"%(name)s" added.') % {'name': request.POST['name']}
        return HttpResponseRedirect(redirect_url_to_survey_list + '%s/' % (obj.id))
    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('survey/survey_change.html', data, context_instance=RequestContext(request))


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
    if int(object_id) != 0:
        # When object_id is not 0
        survey = get_object_or_404(Survey_template, pk=object_id, user=request.user)
        # 1) delete survey
        request.session["msg"] = _('"%(name)s" is deleted.') % {'name': survey.name}
        # delete sections as well as branching which are belong to survey
        delete_section_branching(survey)
        survey.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        try:
            # 1) delete survey
            survey_list = Survey_template.objects.filter(user=request.user).extra(where=['id IN (%s)' % values])
            if survey_list:
                for survey in survey_list:
                    delete_section_branching(survey)

            request.session["msg"] = _('%(count)s survey(s) are deleted.') % {'count': survey_list.count()}
            survey_list.delete()
        except:
            raise Http404

    return HttpResponseRedirect(redirect_url_to_survey_list)


def section_add_form(request, Form, survey, section_type):
    """ To add section object via form

    **Attributes**:

        * ``request`` - Request variable
        * ``Form`` - PlayMessageSectionForm, MultipleChoiceSectionForm,
                     CaptureDigitsSectionForm etc...
        * ``section_type`` - value from SECTION_TYPE list
        * ``survey`` - Survey object

    **Logic Description**:

        * Add section object via section form & section_type
    """
    save_tag = False
    new_obj = ''

    form = Form(request.user, initial={'survey': survey, 'type': section_type})
    if request.POST.get('add'):
        form = Form(request.user, request.POST, initial={'survey': survey, 'type': section_type})
        if form.is_valid():
            new_obj = form.save()
            request.session["msg"] = _('section is added successfully.')
            save_tag = True
        else:
            request.session["err_msg"] = True

    if request.POST.get('add') is None:
        request.session["err_msg"] = True

    data = {
        'form': form,
        'save_tag': save_tag,
        'new_obj': new_obj,
    }
    return data


@permission_required('survey.add_section', login_url='/')
@login_required
def section_add(request):
    """Add new Survey for the logged in user

    **Attributes**:

        * ``template`` - survey/section_change.html

    **Logic Description**:

        * Add a new survey which will belong to the logged in user
          via the SurveyForm & get redirected to the survey list
    """
    survey_id = request.GET.get('survey_id')
    survey = Survey_template.objects.get(pk=survey_id)
    form = PlayMessageSectionForm(request.user, initial={'survey': survey})

    request.session['err_msg'] = ''

    if request.method == 'POST':
        # Play message
        if int(request.POST.get('type')) == SECTION_TYPE.PLAY_MESSAGE:
            form_data = section_add_form(request, PlayMessageSectionForm,
                                         survey, SECTION_TYPE.PLAY_MESSAGE)

        # hangup
        if int(request.POST.get('type')) == SECTION_TYPE.HANGUP_SECTION:
            form_data = section_add_form(request, PlayMessageSectionForm,
                                         survey, SECTION_TYPE.HANGUP_SECTION)

        # DNC
        if int(request.POST.get('type')) == SECTION_TYPE.DNC:
            form_data = section_add_form(request, PlayMessageSectionForm,
                                         survey, SECTION_TYPE.DNC)

        # Multiple Choice Section
        if int(request.POST.get('type')) == SECTION_TYPE.MULTI_CHOICE:
            form_data = section_add_form(request, MultipleChoiceSectionForm,
                                         survey, SECTION_TYPE.MULTI_CHOICE)

        # Rating Section
        if int(request.POST.get('type')) == SECTION_TYPE.RATING_SECTION:
            form_data = section_add_form(request, RatingSectionForm,
                                         survey, SECTION_TYPE.RATING_SECTION)

        # Capture Digits Section
        if int(request.POST.get('type')) == SECTION_TYPE.CAPTURE_DIGITS:
            form_data = section_add_form(request, CaptureDigitsSectionForm,
                                         survey, SECTION_TYPE.CAPTURE_DIGITS)

        # Record Message Section
        if int(request.POST.get('type')) == SECTION_TYPE.RECORD_MSG:
            form_data = section_add_form(request, RecordMessageSectionForm,
                                         survey, SECTION_TYPE.RECORD_MSG)

        # Call transfer Section
        if int(request.POST.get('type')) == SECTION_TYPE.CONFERENCE:
            form_data = section_add_form(request, ConferenceSectionForm,
                                         survey, SECTION_TYPE.CONFERENCE)

        # Call transfer Section
        if int(request.POST.get('type')) == SECTION_TYPE.CALL_TRANSFER:
            form_data = section_add_form(request, CallTransferSectionForm,
                                         survey, SECTION_TYPE.CALL_TRANSFER)

        # SMS Section
        if int(request.POST.get('type')) == SECTION_TYPE.SMS:
            form_data = section_add_form(request, SMSSectionForm, survey, SECTION_TYPE.SMS)

        if form_data.get('save_tag'):
            return HttpResponseRedirect(redirect_url_to_survey_list + '%s/#row%s'
                                        % (form_data['new_obj'].survey_id, form_data['new_obj'].id))
        else:
            form = form_data['form']

    data = {
        'form': form,
        'survey_id': survey_id,
        'err_msg': request.session.get('err_msg'),
        'action': 'add',
        'SECTION_TYPE': SECTION_TYPE,
    }
    request.session["msg"] = ''
    request.session['err_msg'] = ''
    return render_to_response('survey/section_change.html', data, context_instance=RequestContext(request))


def section_update_form(request, Form, section_type, section_instance):
    """To update section instance via form

    **Attributes**:

        * ``request`` - Request variable
        * ``Form`` - PlayMessageSectionForm, MultipleChoiceSectionForm,
                     CaptureDigitsSectionForm etc...
        * ``section_type`` - value from SECTION_TYPE list
        * ``section_instance`` - section object

    **Logic Description**:

        * Update section object via section form & section_type

    """
    save_tag = False
    form = Form(request.user, instance=section_instance, initial={'type': section_type})
    if request.POST.get('update'):
        form = Form(request.user, request.POST, instance=section_instance, initial={'type': section_type})
        if form.is_valid():
            form.save()
            request.session["msg"] = _('section updated.')
            save_tag = True
        else:
            request.session["err_msg"] = True

    if request.POST.get('update') is None:
        request.session["err_msg"] = True

    data = {
        'form': form,
        'save_tag': save_tag,
    }
    return data


@permission_required('survey.change_section', login_url='/')
@login_required
def section_change(request, id):
    """Update survey question for the logged in user

    **Attributes**:

        * ``template`` - survey/section_change.html

    **Logic Description**:

        * update section object via section_update_form function
    """
    section = get_object_or_404(Section_template, pk=int(id), survey__user=request.user)

    if (section.type == SECTION_TYPE.PLAY_MESSAGE
            or section.type == SECTION_TYPE.HANGUP_SECTION
            or section.type == SECTION_TYPE.DNC):
        #PLAY_MESSAGE, HANGUP_SECTION & DNC
        form = PlayMessageSectionForm(request.user, request.POST or None, instance=section)
    elif section.type == SECTION_TYPE.MULTI_CHOICE:
        # MULTI_CHOICE
        form = MultipleChoiceSectionForm(request.user, request.POST or None, instance=section)
    elif section.type == SECTION_TYPE.RATING_SECTION:
        # RATING_SECTION
        form = RatingSectionForm(request.user, request.POST or None, instance=section)
    elif section.type == SECTION_TYPE.CAPTURE_DIGITS:
        # CAPTURE_DIGITS
        form = CaptureDigitsSectionForm(request.user, request.POST or None, instance=section)
    elif section.type == SECTION_TYPE.RECORD_MSG:
        # RECORD_MSG
        form = RecordMessageSectionForm(request.user, request.POST or None, instance=section)
    elif section.type == SECTION_TYPE.CONFERENCE:
        # CONFERENCE
        form = ConferenceSectionForm(request.user, request.POST or None, instance=section)
    elif section.type == SECTION_TYPE.CALL_TRANSFER:
        # CALL_TRANSFER
        form = CallTransferSectionForm(request.user, request.POST or None, instance=section)
    elif section.type == SECTION_TYPE.SMS:
        # SMS
        form = SMSSectionForm(request.user, request.POST or None, instance=section)

    request.session['err_msg'] = ''

    if request.method == 'POST' and request.POST.get('type'):
        # Play message or Hangup Section or DNC
        if (int(request.POST.get('type')) == SECTION_TYPE.PLAY_MESSAGE or
                int(request.POST.get('type')) == SECTION_TYPE.HANGUP_SECTION or
                int(request.POST.get('type')) == SECTION_TYPE.DNC):
            form_data = section_update_form(
                request, PlayMessageSectionForm, SECTION_TYPE.PLAY_MESSAGE, section)

        # Multiple Choice Section
        if int(request.POST.get('type')) == SECTION_TYPE.MULTI_CHOICE:
            form_data = section_update_form(
                request, MultipleChoiceSectionForm, SECTION_TYPE.MULTI_CHOICE, section)

        # Rating Section
        if int(request.POST.get('type')) == SECTION_TYPE.RATING_SECTION:
            form_data = section_update_form(
                request, RatingSectionForm, SECTION_TYPE.RATING_SECTION, section)

        # Capture Digits Section
        if int(request.POST.get('type')) == SECTION_TYPE.CAPTURE_DIGITS:
            form_data = section_update_form(
                request, CaptureDigitsSectionForm, SECTION_TYPE.CAPTURE_DIGITS, section)

        # Record Message Section Section
        if int(request.POST.get('type')) == SECTION_TYPE.RECORD_MSG:
            form_data = section_update_form(
                request, RecordMessageSectionForm, SECTION_TYPE.RECORD_MSG, section)

        # Call Transfer Section
        if int(request.POST.get('type')) == SECTION_TYPE.CALL_TRANSFER:
            form_data = section_update_form(
                request, CallTransferSectionForm, SECTION_TYPE.CALL_TRANSFER, section)

        # Conference Section
        if int(request.POST.get('type')) == SECTION_TYPE.CONFERENCE:
            form_data = section_update_form(
                request, ConferenceSectionForm, SECTION_TYPE.CONFERENCE, section)

        # SMS
        if int(request.POST.get('type')) == SECTION_TYPE.SMS:
            form_data = section_update_form(
                request, SMSSectionForm, SECTION_TYPE.SMS, section)

        if form_data.get('save_tag'):
            return HttpResponseRedirect(redirect_url_to_survey_list + '%s/#row%s'
                                        % (section.survey_id, section.id))
        else:
            form = form_data['form']

    data = {
        'form': form,
        'survey_id': section.survey_id,
        'section_id': section.id,
        'err_msg': request.session.get('err_msg'),
        'action': 'update',
        'SECTION_TYPE': SECTION_TYPE,
    }
    request.session["msg"] = ''
    request.session['err_msg'] = ''
    return render_to_response('survey/section_change.html', data, context_instance=RequestContext(request))


@permission_required('survey.delete_section', login_url='/')
@login_required
def section_delete(request, id):
    """Delete section and branching records
    """
    section = get_object_or_404(Section_template, pk=id, survey__user=request.user)
    if request.GET.get('delete'):
        # perform delete
        survey_id = section.survey_id

        # Re-order section while deleting one section
        section_list_reorder = Section_template.objects.filter(survey=section.survey).exclude(pk=id)
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
        request.session["msg"] = _('section is deleted successfully.')
        return HttpResponseRedirect(redirect_url_to_survey_list + '%s/' % (survey_id))

    data = {
        'section_type': section.type,
        'section_id': section.id,
    }
    return render_to_response('survey/section_delete_confirmation.html', data, context_instance=RequestContext(request))


@permission_required('survey.change_section', login_url='/')
@login_required
def section_script_change(request, id):
    """Update survey question for the logged in user

    **Attributes**:

        * ``form`` - ScriptForm
        * ``template`` - survey/section_script_change.html
    """
    section = get_object_or_404(Section_template, pk=id, survey__user=request.user)
    form = ScriptForm(request.POST or None, instance=section)
    if request.method == 'POST':
        if form.is_valid():
            obj = form.save()
            request.session["msg"] = _('script updated.')
            return HttpResponseRedirect(redirect_url_to_survey_list + '%s/#row%s' % (obj.survey_id, obj.id))
        else:
            request.session["err_msg"] = True

    data = {
        'form': form,
        'survey_id': section.survey_id,
        'section_id': section.id,
        'err_msg': request.session.get('err_msg'),
        'action': 'update',
    }
    request.session["msg"] = ''
    request.session['err_msg'] = ''
    return render_to_response('survey/section_script_change.html', data, context_instance=RequestContext(request))


@login_required
def section_script_play(request, id):
    """Play section  script

    **Attributes**:


    **Logic Description**:

        * Create text file from section script
        * Convert text file into wav file
    """
    section = get_object_or_404(Section_template, pk=id, survey__user=request.user)

    if section.script:
        script_text = section.script

        if settings.TTS_ENGINE == 'ACAPELA':
            # Acapela
            audio_file_path = settings.MEDIA_ROOT + '/' + getaudio_acapela(script_text, 'US')
        elif settings.TTS_ENGINE == 'MSTRANSLATOR':
            # Microsoft Translator
            audio_file_path = settings.MEDIA_ROOT + '/' + getaudio_mstranslator(script_text, 'en')
        else:
            # Flite
            script_hexdigest = hashlib.md5(script_text).hexdigest()
            file_path = '%s/tts/flite_%s' % (settings.MEDIA_ROOT, script_hexdigest)
            audio_file_path = file_path + '.wav'
            text_file_path = file_path + '.txt'

            if not os.path.isfile(audio_file_path):
                # Write text to file
                text_file = open(text_file_path, "w")
                text_file.write(script_text)
                text_file.close()

                # Convert file
                conv = 'flite --setf duration_stretch=1.5 -voice awb -f %s -o %s' % (text_file_path, audio_file_path)
                try:
                    response = subprocess.Popen(conv.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    (filetype, error) = response.communicate()
                except OSError:
                    raise Http404

        if os.path.isfile(audio_file_path):
            response = HttpResponse()
            f = open(audio_file_path, 'rb')
            response['Content-Type'] = 'audio/x-wav'
            response.write(f.read())
            f.close()
            return response

    raise Http404


@permission_required('survey.add_branching', login_url='/')
@login_required
def section_branch_add(request):
    """Add branching on section for the logged in user

    **Attributes**:

        * ``form`` - BranchingForm
        * ``template`` - survey/section_branch_change.html

    **Logic Description**:

        * Add branching record via BranchingForm
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
        form = BranchingForm(section.survey_id, section.id, request.POST or None, initial={'section': section_id})

        if request.method == 'POST':
            if form.is_valid():
                form.save()
                request.session["msg"] = _('branching is added successfully.')
                return HttpResponseRedirect(
                    redirect_url_to_survey_list + '%s/#row%s' % (section.survey_id, section_id))
            else:
                form._errors["keys"] = _("duplicate keys with goto.")
                request.session["err_msg"] = True

    data = {
        'form': form,
        'survey_id': section_survey_id,
        'section_type': section_type,
        'section_id': section_id,
        'err_msg': request.session.get('err_msg'),
        'action': 'add',
        'SECTION_TYPE': SECTION_TYPE,
    }
    request.session["msg"] = ''
    request.session['err_msg'] = ''
    return render_to_response('survey/section_branch_change.html', data, context_instance=RequestContext(request))


@permission_required('survey.change_branching', login_url='/')
@login_required
def section_branch_change(request, id):
    """Add branching on section for the logged in user

    **Attributes**:

        * ``form`` - BranchingForm
        * ``template`` - survey/section_branch_change.html

    **Logic Description**:

        * Update branching record via BranchingForm
        * Delete branching record
    """
    request.session['msg'] = ''
    if request.GET.get('delete'):
        # perform delete
        branching_obj = get_object_or_404(Branching_template, id=int(id),
                                          section__survey__user=request.user)
        survey_id = branching_obj.section.survey_id
        section_id = branching_obj.section_id
        branching_obj.delete()
        request.session["msg"] = _('branching is deleted successfully.')
        return HttpResponseRedirect(redirect_url_to_survey_list + '%s/#row%s' % (survey_id, section_id))

    branching = get_object_or_404(Branching_template, id=int(id),
                                  section__survey__user=request.user)
    form = BranchingForm(branching.section.survey_id,
                         branching.section_id,
                         request.POST or None,
                         instance=branching)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            request.session["msg"] = _('branching updated.')
            return HttpResponseRedirect(redirect_url_to_survey_list + '%s/#row%s'
                                        % (branching.section.survey_id, branching.section_id))
        else:
            form._errors["keys"] = _("duplicate record keys with goto.")
            request.session["err_msg"] = True

    data = {
        'form': form,
        'survey_id': branching.section.survey_id,
        'section_type': branching.section.type,
        'section_id': branching.section.id,
        'branching_id': branching.id,
        'err_msg': request.session.get('err_msg'),
        'action': 'update',
        'SECTION_TYPE': SECTION_TYPE,
    }
    request.session["msg"] = ''
    request.session['err_msg'] = ''
    return render_to_response('survey/section_branch_change.html', data, context_instance=RequestContext(request))


@permission_required('survey.change_survey', login_url='/')
@login_required
def survey_change(request, object_id):
    """Update/Delete Survey for the logged in user

    **Attributes**:

        * ``object_id`` - Selected survey object
        * ``form`` - SurveyForm
        * ``template`` - survey/change.html

    **Logic Description**:

        * Update/delete selected survey from the survey list
          via SurveyForm & get redirected to survey list
    """
    survey = get_object_or_404(Survey_template, pk=object_id, user=request.user)
    section_list = Section_template.objects.filter(survey=survey).order_by('order')

    form = SurveyForm(request.POST or None, instance=survey)
    branching_list = Branching_template.objects.filter(section__survey=survey).order_by('id')

    branching_section_list = branching_list.values_list('section_id', flat=True).distinct()

    if form.is_valid():
        if request.POST.get('delete'):
            survey_del(request, object_id)
            return HttpResponseRedirect(redirect_url_to_survey_list)
        else:
            form.save()
            request.session["msg"] = _('"%(name)s" is updated.') % {'name': request.POST['name']}
            return HttpResponseRedirect(redirect_url_to_survey_list)

    data = {
        'survey_obj_id': object_id,
        'section_list': section_list,
        'branching_list': branching_list,
        'branching_section_list': branching_section_list,
        'action': 'update',
        'form': form,
        'msg': request.session.get('msg'),
        'SECTION_TYPE': SECTION_TYPE,
    }
    request.session['msg'] = ''
    return render_to_response('survey/survey_change.html', data, context_instance=RequestContext(request))


@login_required
def sealed_survey_view(request, object_id):
    """View sealed survey

    **Attributes**:

        * ``object_id`` - Selected survey object
        * ``template`` - survey/sealed_survey_view.html

    **Logic Description**:

        * Update/delete selected survey from the survey list
          via SurveyForm & get redirected to survey list
    """
    survey = get_object_or_404(Survey, pk=object_id, user=request.user)
    section_list = Section.objects.filter(survey=survey).order_by('order')
    branching_list = Branching.objects.filter(section__survey=survey).order_by('id')
    branching_section_list = branching_list.values_list('section_id', flat=True).distinct()
    data = {
        'survey_obj_id': object_id,
        'survey': survey,
        'section_list': section_list,
        'branching_list': branching_list,
        'branching_section_list': branching_section_list,
        'action': 'view',
        'msg': request.session.get('msg'),
        'SECTION_TYPE': SECTION_TYPE,
    }
    return render_to_response('survey/sealed_survey_view.html', data, context_instance=RequestContext(request))


def survey_cdr_daily_report(all_call_list):
    """Get survey voip call daily report"""
    max_duration = 0
    total_duration = 0
    total_calls = 0
    total_avg_duration = 0

    # Daily Survey VoIP call report
    select_data = {"starting_date": "SUBSTR(CAST(starting_date as CHAR(30)),1,10)"}

    # Get Total from VoIPCall table for Daily Call Report
    total_data = all_call_list.extra(select=select_data)\
        .values('starting_date')\
        .annotate(Count('starting_date'))\
        .annotate(Sum('duration'))\
        .annotate(Avg('duration'))\
        .order_by('-starting_date')

    # Following code will count total voip calls, duration
    if total_data:
        max_duration = max([x['duration__sum'] for x in total_data])
        total_duration = sum([x['duration__sum'] for x in total_data])
        total_calls = sum([x['starting_date__count'] for x in total_data])
        total_avg_duration = (sum([x['duration__avg'] for x in total_data]))

    survey_cdr_daily_data = {
        'total_data': total_data,
        'total_duration': total_duration,
        'total_calls': total_calls,
        'total_avg_duration': total_avg_duration,
        'max_duration': max_duration,
    }

    return survey_cdr_daily_data


def get_survey_result(survey_result_kwargs):
    """Get survey result report from the selected Survey"""
    survey_result = ResultAggregate.objects.values('section__question', 'response', 'count')\
        .filter(**survey_result_kwargs).order_by('section')
    return survey_result


def survey_audio_recording(audio_file):
    """audio player tag for frontend for survey recording

    >>> survey_audio_recording('')
    u'<br/><span class="label label-important">no recording</span>'
    """
    if audio_file:
        file_url = '%srecording/%s' % (settings.MEDIA_URL, str(audio_file))
        player_string = '<ul class="playlist"><li style="width:auto;"> <a href="%s">%s</a></li></ul>' % \
            (file_url, os.path.basename(file_url))
        return player_string
    else:
        return '<br/><span class="label label-important">%s</span>' % _('no recording')


@permission_required('survey.view_survey_report', login_url='/')
@login_required
def survey_report(request):
    """
    Survey detail report for the logged in user

    **Attributes**:

        * ``template`` - survey/survey_report.html
        * ``form`` - SurveyDetailReportForm

    **Logic Description**:

        * List all survey_report which belong to the logged in user.
    """
    tday = datetime.today()
    from_date = tday.strftime("%Y-%m-%d")
    to_date = tday.strftime("%Y-%m-%d")

    form = SurveyDetailReportForm(request.user, request.POST or None,
                                  initial={'from_date': from_date,
                                           'to_date': to_date})
    survey_result = ''

    survey_cdr_daily_data = {
        'total_data': '',
        'total_duration': '',
        'total_calls': '',
        'total_avg_duration': '',
        'max_duration': '',
    }

    sort_col_field_list = ['starting_date', 'phone_number', 'duration', 'disposition', 'id']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='starting_date')

    survey_id = ''
    action = 'tabs-1'
    campaign_obj = ''
    rows = []
    survey_id = ''
    post_var_with_page = 0
    if form.is_valid():
        post_var_with_page = 1
        # set session var value
        request.session['session_surveycalls_kwargs'] = {}
        request.session['session_survey_cdr_daily_data'] = {}
        # set session var value
        field_list = ['from_date', 'to_date', 'survey_id']
        unset_session_var(request, field_list)

        from_date = getvar(request, 'from_date')
        to_date = getvar(request, 'to_date')
        start_date = ceil_strdate(str(from_date), 'start')
        end_date = ceil_strdate(str(to_date), 'end')

        converted_start_date = start_date.strftime('%Y-%m-%d')
        converted_end_date = end_date.strftime('%Y-%m-%d')
        request.session['session_start_date'] = converted_start_date
        request.session['session_end_date'] = converted_end_date

        survey_id = getvar(request, 'survey_id', setsession=True)

    if request.GET.get('page') or request.GET.get('sort_by'):
        post_var_with_page = 1
        start_date = request.session.get('session_start_date')
        end_date = request.session.get('session_end_date')
        start_date = ceil_strdate(start_date, 'start')
        end_date = ceil_strdate(end_date, 'end')
        survey_id = request.session.get('session_survey_id')

        form = SurveyDetailReportForm(request.user, initial={'from_date': start_date.strftime('%Y-%m-%d'),
                                                             'to_date': end_date.strftime('%Y-%m-%d'),
                                                             'survey_id': survey_id})
    if post_var_with_page == 0:
        # default
        # unset session var
        tday = datetime.utcnow().replace(tzinfo=utc)
        from_date = tday.strftime('%Y-%m-01')
        last_day = ((datetime(tday.year, tday.month, 1, 23, 59, 59, 999999).replace(tzinfo=utc) +
                     relativedelta(months=1)) -
                    relativedelta(days=1)).strftime('%d')
        to_date = tday.strftime('%Y-%m-' + last_day)
        start_date = ceil_strdate(from_date, 'start')
        end_date = ceil_strdate(to_date, 'end')

        # unset session var value
        request.session['session_from_date'] = from_date
        request.session['session_to_date'] = to_date
        request.session['session_survey_id'] = ''
        request.session['session_surveycalls_kwargs'] = ''

    kwargs = {}
    if not request.user.is_superuser:
        kwargs['user'] = request.user
    kwargs['disposition__exact'] = CALL_DISPOSITION.ANSWER

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

    all_call_list = []
    try:
        survey_result_kwargs['survey_id'] = survey_id
        survey_result = get_survey_result(survey_result_kwargs)

        campaign_obj = Survey.objects.get(id=int(survey_id)).campaign
        kwargs['callrequest__campaign'] = campaign_obj

        # List of Survey VoIP call report
        voipcall_list = VoIPCall.objects.filter(**kwargs)
        request.session['session_surveycalls_kwargs'] = kwargs
        all_call_list = voipcall_list.values_list('id', flat=True)

        # Get daily report from session while using pagination & sorting
        if request.GET.get('page') or request.GET.get('sort_by'):
            survey_cdr_daily_data = request.session['session_survey_cdr_daily_data']
            action = 'tabs-2'
        else:
            survey_cdr_daily_data = survey_cdr_daily_report(voipcall_list)
            request.session['session_survey_cdr_daily_data'] = survey_cdr_daily_data

        rows = voipcall_list.order_by(pag_vars['sort_order'])[pag_vars['start_page']:pag_vars['end_page']]
    except:
        rows = []
        if request.method == 'POST':
            request.session["err_msg"] = _('no campaign attached with survey.')

    data = {
        'rows': rows,
        'all_call_list': all_call_list,
        'call_count': all_call_list.count() if all_call_list else 0,
        'SURVEY_CALL_RESULT_NAME': SURVEY_CALL_RESULT_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
        'total_data': survey_cdr_daily_data['total_data'],
        'total_duration': survey_cdr_daily_data['total_duration'],
        'total_calls': survey_cdr_daily_data['total_calls'],
        'total_avg_duration': survey_cdr_daily_data['total_avg_duration'],
        'max_duration': survey_cdr_daily_data['max_duration'],
        'msg': request.session.get('msg'),
        'err_msg': request.session.get('err_msg'),
        'form': form,
        'survey_result': survey_result,
        'action': action,
        'start_date': start_date,
        'end_date': end_date,
        'campaign_obj': campaign_obj,
    }
    request.session['msg'] = ''
    request.session['err_msg'] = ''
    return render_to_response('survey/survey_report.html', data, context_instance=RequestContext(request))


@login_required
def export_surveycall_report(request):
    """Export CSV file of Survey VoIP call record

    **Important variable**:

        * ``request.session['surveycall_record_qs']`` - stores survey voipcall
            query set

    **Exported fields**: ['starting_date', 'phone_number', 'duration',
                          'disposition', 'survey results']
    """
    format_type = request.GET['format']
    # get the response object, this can be used as a stream.
    response = HttpResponse(content_type='text/%s' % format_type)
    # force download.
    response['Content-Disposition'] = 'attachment;filename=export.%s' % format_type
    if request.session.get('session_surveycalls_kwargs'):
        kwargs = request.session.get('session_surveycalls_kwargs')
        campaign_obj = kwargs['callrequest__campaign']
        qs = VoIPCall.objects.filter(**kwargs)
        column_list_base = ['starting_date', 'phone_number', 'duration', 'disposition']
        column_list = list(column_list_base)

        survey_qst = False
        if campaign_obj.content_type.model == 'survey':
            survey_qst = Section.objects.filter(survey_id=int(campaign_obj.object_id))
            for i in survey_qst:
                column = unicode(i.question.replace(',', ' '))
                column_list.append(column.encode('utf-8'))

        result_row = []
        for voipcall in qs:
            result_row_list = []
            # For each voip call retrieve the results of the survey nodes
            results = Result.objects.filter(callrequest=voipcall.callrequest_id).order_by('section')

            result_list = {}
            # We will prepare a dictionary result_list to help exporting the result
            for result in results:
                column = unicode(result.section.question.replace(',', ' '))
                if result.record_file and len(result.record_file) > 0:
                    result_list[column.encode('utf-8')] = result.record_file
                else:
                    result_list[column.encode('utf-8')] = result.response

            # We will build result_row_list which will be a value for each element from column_list
            for ikey in column_list:
                if ikey in column_list_base:
                    # This is not a Section result
                    if ikey == 'starting_date' \
                       and format_type == Export_choice.JSON \
                       or format_type == Export_choice.XLS:
                        starting_date = str(voipcall.__dict__[ikey])
                        result_row_list.append(starting_date)
                    else:
                        result_row_list.append(voipcall.__dict__[ikey])
                else:
                    # This is a Section result
                    if ikey in result_list:
                        result_row_list.append(result_list[ikey].encode('utf-8'))
                    else:
                        # Add empty result
                        result_row_list.append("")

            result_row.append(result_row_list)

        data = tablib.Dataset(*result_row, headers=tuple(column_list))
        if format_type == Export_choice.XLS:
            response.write(data.xls)
        elif format_type == Export_choice.CSV:
            response.write(data.csv)
        elif format_type == Export_choice.JSON:
            response.write(data.json)
    return response


@login_required
def survey_campaign_result(request, id):
    """Survey Campaign Result

    **Attributes**:

        * ``template`` - survey/survey_campaign_result.html

    **Logic Description**:

        * List all survey result which belong to callrequest.
    """
    result = Result.objects.filter(callrequest=VoIPCall.objects.get(pk=id).callrequest_id).order_by('section')
    data = {
        'result': result,
    }
    request.session['msg'] = ''
    request.session['err_msg'] = ''
    return render_to_response('survey/survey_campaign_result.html', data, context_instance=RequestContext(request))


@permission_required('survey.export_survey', login_url='/')
@login_required
def export_survey(request, id):
    """Export sections and branching of survey into text file"""
    # get the response object, this can be used as a stream.
    response = HttpResponse(content_type='text/txt')
    # force download.
    response['Content-Disposition'] = 'attachment;filename=survey.txt'
    # the txt writer
    writer = csv.writer(response, delimiter='|', lineterminator='\n',)

    survey = get_object_or_404(Survey_template, pk=int(id), user=request.user)

    if survey:
        section_list = Section_template.objects.filter(survey=survey).order_by('order')
        for section in section_list:
            # write section in text file
            writer.writerow([
                section.order,
                section.type,
                section.question.encode('utf-8'),
                section.script.encode('utf-8'),
                section.audiofile_id,
                section.retries,
                section.timeout,
                section.key_0,
                section.key_1,
                section.key_2,
                section.key_3,
                section.key_4,
                section.key_5,
                section.key_6,
                section.key_7,
                section.key_8,
                section.key_9,
                section.rating_laps,
                section.validate_number,
                section.number_digits,
                section.min_number,
                section.max_number,
                section.phonenumber,
                section.confirm_script,
                section.confirm_key,
                section.conference,
                section.sms_text,
                section.completed,
                section.invalid_audiofile_id,
                section.id,
            ])

        for section in section_list:
            branching_list = Branching_template.objects.filter(section=section).order_by('id')
            for branching in branching_list:
                # write branching text file
                writer.writerow([
                    branching.keys,
                    branching.section_id,
                    branching.goto_id,
                ])

    return response


@permission_required('survey.import_survey', login_url='/')
@login_required
def import_survey(request):
    """Importing sections and branching of survey

    **Attributes**:

        * ``template`` - survey/import_survey.html
        * ``form`` - SurveyFileImport
    """
    form = SurveyFileImport(request.POST or None, request.FILES or None)
    section_row = []
    branching_row = []
    type_error_import_list = []
    if request.method == 'POST':
        if form.is_valid():
            new_survey = Survey_template.objects.create(name=request.POST['name'], user=request.user)
            records = csv.reader(request.FILES['survey_file'], delimiter='|', quotechar='"')
            new_old_section = {}

            # disconnect post_save_add_script signal from Section_template
            post_save.disconnect(post_save_add_script, sender=Section_template)
            # Read each row
            for row in records:
                row = striplist(row)
                if not row or str(row[0]) == 0:
                    continue

                # if length of row is 30, it's a section
                if len(row) == 30:
                    try:
                        # for section
                        section_template_obj = Section_template.objects.create(
                            order=int(row[0]),
                            type=int(row[1]) if row[1] else 1,
                            question=row[2],
                            script=row[3],
                            audiofile_id=int(row[4]) if row[4] else None,
                            retries=int(row[5]) if row[5] else 0,
                            timeout=int(row[6]) if row[6] else 0,
                            key_0=row[7] if row[7] else '',
                            key_1=row[8] if row[8] else '',
                            key_2=row[9] if row[9] else '',
                            key_3=row[10] if row[10] else '',
                            key_4=row[11] if row[11] else '',
                            key_5=row[12] if row[12] else '',
                            key_6=row[13] if row[13] else '',
                            key_7=row[14] if row[14] else '',
                            key_8=row[15] if row[15] else '',
                            key_9=row[16] if row[16] else '',
                            rating_laps=int(row[17]) if row[17] else None,
                            validate_number=row[18] if row[18] == 'True' else False,
                            number_digits=int(row[19]) if row[19] else None,
                            min_number=row[20] if row[20] else None,
                            max_number=row[21] if row[21] else None,
                            phonenumber=row[22] if row[22] else None,
                            confirm_script=row[23] if row[23] else None,
                            confirm_key=row[24] if row[24] else None,
                            conference=row[25] if row[25] else None,
                            sms_text=row[26] if row[26] else None,
                            completed=True if row[27] == 'True' else False,
                            invalid_audiofile_id=int(row[28]) if row[28] else None,
                            survey=new_survey,
                        )
                        new_old_section[int(row[29])] = section_template_obj.id
                        section_row.append(row)
                    except:
                        type_error_import_list.append(row)

                # if length of row is 3, it's a branching
                if len(row) == 3:
                    new_section_id = ''
                    new_goto_section_id = ''
                    if row[1]:
                        new_section_id = new_old_section[int(row[1])]
                    if row[2]:
                        new_goto_section_id = new_old_section[int(row[2])]

                    duplicate_count = Branching_template.objects.filter(
                        keys=row[0], section_id=new_section_id).count()
                    if duplicate_count == 0:
                        try:
                            Branching_template.objects.create(
                                keys=row[0],
                                section_id=new_section_id,
                                goto_id=int(new_goto_section_id) if new_goto_section_id else None,
                            )
                        except:
                            type_error_import_list.append(row)

            # connect post_save_add_script signal with Section_template
            post_save.connect(post_save_add_script, sender=Section_template)
            return HttpResponseRedirect(redirect_url_to_survey_list)
        else:
            request.session["err_msg"] = True

    data = {
        'form': form,
        'section_row': section_row,
        'branching_row': branching_row,
        'type_error_import_list': type_error_import_list,
        'err_msg': request.session.get('err_msg'),
    }
    request.session['err_msg'] = ''
    return render_to_response('survey/import_survey.html', data, context_instance=RequestContext(request))


@permission_required('survey.view_sealed_survey', login_url='/')
@login_required
def sealed_survey_list(request):
    """Survey list for the logged in user

    **Attributes**:

        * ``template`` - survey/sealed_survey_list.html

    **Logic Description**:

        * List all sealed surveys which belong to the logged in user.
    """
    sort_col_field_list = ['id', 'name', 'updated_date', 'campaign']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    survey_list = Survey.objects.values('id', 'name', 'description', 'updated_date', 'campaign__name')\
        .filter(user=request.user).order_by(pag_vars['sort_order'])
    data = {
        'survey_list': survey_list,
        'total_survey': survey_list.count(),
        'SEALED_SURVEY_COLUMN_NAME': SEALED_SURVEY_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
        'msg': request.session.get('msg'),
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('survey/sealed_survey_list.html', data, context_instance=RequestContext(request))


@permission_required('survey.seal_survey', login_url='/')
@login_required
def seal_survey(request, object_id):
    """
    Seal survey without campaign
    """
    form = SealSurveyForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            survey_template = get_object_or_404(Survey_template, pk=object_id, user=request.user)
            survey_template.name = request.POST.get('name', survey_template.name)
            survey_template.copy_survey_template()
            request.session['msg'] = '"%s" survey is sealed successfully' % survey_template.name
            return HttpResponseRedirect(redirect_url_to_survey_list)
        else:
            request.session['err_msg'] = True
    data = {
        'form': form,
        'err_msg': request.session.get('err_msg'),
        'object_id': object_id,
    }
    request.session['err_msg'] = ''
    return render_to_response('survey/seal_survey.html', data, context_instance=RequestContext(request))
