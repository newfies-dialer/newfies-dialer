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
from string import Template


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
    if col_class_1 or col_class_2:
        div_string = '<div class="%s %s">\n' % (col_class_1, col_class_2)

    div_string += '<div class="form-group %s">\n' % (
        'has-error' if field.errors else '')

    div_string += '<label class="control-label" for="%s">%s</label>\n' % (
        field.auto_id, word_capital(field.label))

    div_string += '%s\n' % str(field).decode("utf-8")

    if field.errors and flag_error_text:
        div_string += '<span class="help-block">%s</span>\n' % striphtml(str(field.errors)).capitalize()

    if flag_help_text:
        div_string += '<span class="help-block">%s</span>\n' % (field.help_text.capitalize())

    div_string += '</div>\n'

    if col_class_1 or col_class_2:
        div_string += '</div>\n'

    return mark_safe(div_string)


@register.simple_tag(name='field_html_code2')
def field_html_code2(field, main_class='col-md-6 col-xs-8', flag_error_text=True, flag_help_text=True):
    """
    Usage: {% field_html_code field 'col-md-6' 'col-xs-8' %}
    """
    tmp_div = Template("""
        <div class="$main_class">
            <div class="form-group $has_error">
                <label class="control-label" for="$field_auto_id">$field_label</label>
                $field
                $field_errors
                $field_help_test
            </div>
        </div>
    """)
    has_error = 'has-error' if field.errors else ''
    if field.errors and flag_error_text:
        field_errors = '<span class="help-block">%s</span>\n' % striphtml(str(field.errors)).capitalize()
    else:
        field_errors = ''
    if flag_help_text:
        field_help_test = '<span class="help-block">%s</span>\n' % (field.help_text.capitalize())
    else:
        field_help_test = ''
    htmlcell = tmp_div.substitute(
        main_class=main_class, has_error=has_error,
        field_auto_id=field.auto_id, field_label=word_capital(field.label),
        field=str(field).decode("utf-8"), field_errors=field_errors,
        field_help_test=field_help_test)

    return mark_safe(htmlcell)


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
