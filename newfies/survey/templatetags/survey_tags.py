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

from django.template.defaultfilters import register
from django.utils.translation import ugettext_lazy as _
from survey.views import survey_audio_recording
from survey.models import Section_template, Branching_template
from survey.constants import SECTION_TYPE


@register.simple_tag(name='percentage_tag')
def percentage_tag(fraction, population):
    """Usage: {% percentage_tag fraction population %}"""
    try:
        return "%.2f%%" % ((float(fraction) / float(population)) * 100)
    except:
        return "0.00%"


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
                new_string = '<tr><td colspan="2">%s%s</td></tr>' %\
                             (str(que_audio[0]),
                              survey_audio_recording(str(que_audio[1])))
                result_string += new_string.encode('utf-8')
        else:
            que_res = i.encode('utf-8').split("*|*")
            result_string += \
                '<tr><td>%s</td><td class="survey_result_key">%s</td></tr>' %\
                (que_res[0], que_res[1])

    result_string += '</table>'
    return result_string


@register.filter(name='running_total')
def running_total(running_list, field_name):
    return sum(d[field_name] for d in running_list)


@register.filter(name='get_branching_goto_field')
def get_branching_goto_field(section_id, selected_value):
    """
    get_branching_goto_field
    """
    section_obj = Section_template.objects.get(id=section_id)
    #We don't need a lazy translation in this case
    option_list = '<option value="">%s</option>' % _('hang up').encode('utf-8')
    list = Section_template.objects.filter(survey_id=section_obj.survey_id)\
        .order_by('id')
    for i in list:
        if i.question:
            q_string = i.question
        else:
            q_string = i.script

        if selected_value == i.id:
            option_list += '<option value="%s" selected=selected>Goto: %s</option>' % \
                           (str(i.id), (q_string))
        else:
            option_list += '<option value="%s">Goto: %s</option>' % \
                           (str(i.id), (q_string))

    return option_list


@register.filter(name='get_branching_count')
def get_branching_count(section_id, branch_id):
    """
    calculate branching count
    """
    branch_list = Branching_template \
        .objects.values_list('id', flat=True).filter(section_id=section_id)\
        .order_by('id')
    branch_count = branch_list.count()
    # for default branching option to remove delete option
    if branch_list[0] == branch_id:
        branch_count = 0
    return branch_count


@register.simple_tag(name='link_of_survey_view')
def link_of_survey_view(survey_id):
    """
    create survey view link
    """
    link = '<a href="/module/sealed_survey_view/%s/" target="_blank" title="%s"><i class="fa fa-search"></i></a>' % \
        (survey_id, _('view sealed survey').capitalize())
    return link
