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

from django.db.models import get_model
from django.template.defaultfilters import register
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from survey.views import survey_audio_recording
from dialer_campaign.constants import CAMPAIGN_STATUS
from dialer_campaign.views import tpl_control_icon, make_duplicate_campaign
from dialer_cdr.constants import LEG_TYPE
from survey.constants import SECTION_TYPE
from voice_app.constants import VOICEAPP_TYPE
from dialer_campaign.function_def import get_campaign_status_name
from dialer_campaign.views import get_campaign_survey_view, get_url_campaign_status
import os.path


@register.simple_tag(name='percentage_tag')
def percentage_tag(fraction, population):
    """Usage: {% percentage_tag fraction population %}"""
    try:
        return "%.2f%%" % ((float(fraction) / float(population)) * 100)
    except:
        return "0.00%"


@register.filter(name='contact_status')
def contact_status(value):
    """Contact status

    >>> contact_status(1)
    'ACTIVE'

    >>> contact_status(2)
    'INACTIVE'
    """
    if value == 1:
        return str('ACTIVE')
    else:
        return str('INACTIVE')


@register.filter(name='campaign_status')
def campaign_status(value):
    """Campaign Status

    >>> campaign_status(1)
    'START'

    >>> campaign_status(2)
    'PAUSE'

    >>> campaign_status(3)
    'ABORT'

    >>> campaign_status(4)
    'END'

    >>> campaign_status(0)
    ''
    """
    if not value:
        return ''
    STATUS = dict(CAMPAIGN_STATUS)
    try:
        status = STATUS[value]
    except:
        status = ''

    return str(status)


@register.filter(name='leg_type_name')
def leg_type_name(value):
    """leg type

    >>> leg_type_name(1)
    u'A-Leg'

    >>> leg_type_name(2)
    u'B-Leg'

    >>> leg_type_name(0)
    ''
    """
    if not value:
        return ''
    TYPE = dict(LEG_TYPE)
    try:
        status = TYPE[value]
    except:
        status = ''

    return unicode(status)


@register.filter(name='section_type_name')
def section_type_name(value):
    """survey section type name

    >>> section_type_name(1)
    'Play message'

    >>> section_type_name(2)
    'Multi-choice'

    >>> section_type_name(0)
    ''
    """
    if not value:
        return ''
    TYPE = dict(SECTION_TYPE)
    try:
        status = TYPE[value]
    except:
        status = ''

    return str(status)


@register.filter(name='voiceapp_type')
def voiceapp_type(value):
    """
    >>> voiceapp_type(1)
    'DIAL'
    """
    if not value:
        return ''
    TYPE = dict(VOICEAPP_TYPE)
    try:
        status = TYPE[value]
    except:
        status = ''

    return str(status)


@register.filter(name='que_res_string')
def que_res_string(val):
    """Modify survey result string for display

    >>> val = 'qst_1*|*ans_1'

    >>> que_res_string(val)
    '<table class="table table-striped table-bordered table-condensed"><tr><td>qst_1</td><td class="survey_result_key">ans_1</td></tr></table>'
    """
    if not val:
        return ''

    val_list = val.split("-|-")
    result_string = '<table class="table table-striped table-bordered '\
                    'table-condensed">'

    for i in val_list:
        if "*|**|*" in i:
            que_audio = i.encode('utf-8').split("*|**|*")
            if que_audio:
                new_string = '<tr><td colspan="2">%s%s</td></tr>' % \
                             (str(que_audio[0]),
                              survey_audio_recording(str(que_audio[1])))
                result_string += new_string.encode('utf-8')
        else:
            que_res = i.encode('utf-8').split("*|*")
            result_string += \
                '<tr><td>%s</td><td class="survey_result_key">%s</td></tr>' % \
                    (que_res[0], que_res[1])

    result_string += '</table>'
    return result_string


@register.filter(name='running_total')
def running_total(running_list, field_name):
    return sum(d[field_name] for d in running_list)


@register.filter(name='get_file_basename')
def get_file_basename(val):
    if val:
        file_url = settings.MEDIA_URL + str(val)
        return os.path.basename(file_url)
    return ''


@register.filter(name='get_campaign_status')
def get_campaign_status(id):
    return get_campaign_status_name(id)


@register.simple_tag(name='get_app_name')
def get_app_name(app_label, model_name, object_id):
    """To get app name from app_label, model_name & object_id
    Usage: {% get_app_name app_label model_name object_id %}
    """
    try:
        return get_model(app_label, model_name).objects.get(pk=object_id)
    except:
        return '-'


@register.filter(name='create_duplicate_campaign')
def create_duplicate_campaign(camp_id):
    link = make_duplicate_campaign(camp_id)
    return link


@register.simple_tag(name='get_campaign_app_view')
def get_campaign_app_view(campaign_object):
    return get_campaign_survey_view(campaign_object)


@register.simple_tag(name='get_campaign_status_url')
def get_campaign_status_url(id, status):
    return get_url_campaign_status(id, status)


from survey.models import Section_template, Branching_template
from django.utils.translation import gettext as __

@register.filter(name='get_branching_goto_field')
def get_branching_goto_field(section_id, selected_value):
    section_obj = Section_template.objects.get(id=section_id)
    section_branch_list = Branching_template\
        .objects.values_list('section_id', flat=True)\
        .filter(section__survey_id=section_obj.survey_id)

    option_list = '<option value="">%s</option>' % __('Hang up')
    list = Section_template.objects.filter(survey_id=section_obj.survey_id).order_by('id')
    for i in list:
        if i.question:
            q_string = i.question
        else:
            q_string = i.script

        if selected_value == i.id:
            option_list += '<option value="%s" selected=selected>Goto: %s</option>' % (str(i.id), (q_string))
        else:
            option_list += '<option value="%s">Goto: %s</option>' % (str(i.id), (q_string))

    return option_list


@register.filter(name='get_branching_count')
def get_branching_count(section_id, branch_id):
    branch_list = Branching_template\
        .objects.values_list('id', flat=True).filter(section_id=section_id)\
        .order_by('id')
    branch_count = branch_list.count()
    # for default branching option to remove delete option
    if branch_list[0] == branch_id:
        branch_count = 0
    return branch_count