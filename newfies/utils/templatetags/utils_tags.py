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


def striphtml(data):
    p = re.compile(r'<.*?>')
    return mark_safe(p.sub('', data))


@register.simple_tag(name='field_html_code')
def field_html_code(field, col_class_1='col-md-6', col_class_2='col-xs-8'):
    """
    Usage: {% field_html_code field 'col-md-6' 'col-xs-8' %}
    """
    error_class = ''
    if field.errors:
        error_class = 'has-error'

    div_string = '<div class="%s">' % col_class_1
    div_string += '<div class="form-group %s">' % (error_class)
    div_string += '<div class="%s"><label class="control-label" for="%s">%s</label>%s' % (
        col_class_2, field.auto_id, word_capital(field.label), field)

    if field.errors:
        div_string += '<span class="help-block">%s</span>' % striphtml(str(field.errors)).capitalize()

    div_string += '<span class="help-block">%s</span>' % (field.help_text.capitalize())
    div_string += '</div></div></div>'

    return mark_safe(div_string)
