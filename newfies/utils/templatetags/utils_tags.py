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

from django.utils.safestring import mark_safe
from django.template.defaultfilters import register
from common.common_functions import word_capital
import re


def stab(tab=1):
    """
    create space tabulation
    """
    return ' ' * 4 * tab


def striphtml(data):
    p = re.compile(r'<.*?>')
    return mark_safe(p.sub('', data))


@register.simple_tag(name='field_html_code')
def field_html_code(field, col_class_1='col-md-6', col_class_2='col-xs-8', flag_error_text=True, flag_help_text=True):
    """
    Usage: {% field_html_code field 'col-md-6' 'col-xs-8' %}
    """
    div_string = ''
    if col_class_1:
        div_string = '<div class="%s">\n' % col_class_1

    div_string += stab(1) + '<div class="form-group %s">\n' % (
        'has-error' if field.errors else '')

    if col_class_2:
        div_string += stab(2) + '<div class="%s">\n' % col_class_2

    div_string += stab(3) + '<label class="control-label" for="%s">%s</label>\n' % (
        field.auto_id, word_capital(field.label))
    div_string += stab(3) + '%s\n' % (field)

    if field.errors and flag_error_text:
        div_string += stab(3) + '<span class="help-block">%s</span>\n' % striphtml(str(field.errors)).capitalize()

    if flag_help_text:
        div_string += stab(3) + '<span class="help-block">%s</span>\n' % (field.help_text.capitalize())

    div_string += stab(2) + '</div>\n'

    if col_class_2:
        div_string += stab(1) + '</div>\n'

    if col_class_1:
        div_string += '</div>\n'

    return mark_safe(div_string)


@register.simple_tag(name='search_form_field_html_code')
def search_form_field_html_code(field, col_class_1='col-md-6', flag_error_text=True, flag_help_text=True):
    """
    Usage: {% search_form_field_html_code field 'col-md-6' %}
    """
    div_string = ''
    div_string += '<div class="%s %s">\n' % (
        col_class_1, 'has-error' if field.errors else '')

    div_string += stab(1) + '<label class="control-label" for="%s">%s</label>\n' % (
        field.auto_id, word_capital(field.label))
    div_string += stab(1) + '%s\n' % (field)

    if field.errors and flag_error_text:
        div_string += stab(1) + '<span class="help-block">%s</span>\n' % striphtml(str(field.errors)).capitalize()

    if flag_help_text:
        div_string += stab(1) + '<span class="help-block">%s</span>\n' % (field.help_text.capitalize())

    div_string += '</div>\n'

    return mark_safe(div_string)
