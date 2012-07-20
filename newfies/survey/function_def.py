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

from django.utils.translation import ugettext as _
from audiofield.models import AudioFile


def field_list(name, user=None):
    """Return List of audio file names"""
    if name == "audiofile" and user is None:
        list = AudioFile.objects.all()

    if name == "audiofile" and user is not None:
        list = AudioFile.objects.filter(user=user)

    return ((l.id, l.name) for l in list)


def export_question_result(val):
    """Modify survey result string for export"""
    if not val:
        return ''
    val_list = val.split("-|-")
    result_string = ''

    rec_count = 1
    if len(val_list) == rec_count:
        line_end_with = ''
    else:
        line_end_with = '\t\n'

    for i in val_list:
        if not i:
            continue
        if i.find("*|**|*") > 0:
            que_audio = i.split("*|**|*")
            result_string += _('Que. : ') + str(que_audio[0]) \
                        + '\t\n' + _('Audio File') + ': ' \
                        + str(que_audio[1]) + line_end_with
        else:
            que_res = i.split("*|*")
            try:
                if str(que_res[0]) != 'None':
                    result_string += _('Que. : ') + str(que_res[0]) + '\t\n'
                else:
                    result_string += str(que_res[0]) + '\t\n'
            except:
                result_string += ''
            try:
                result_string += _('Key') + ': ' \
                        + str(que_res[1]) + line_end_with
            except:
                result_string += ''

        rec_count += 1

    return str(result_string)
