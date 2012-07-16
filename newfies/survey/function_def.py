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


def get_que_res_string(val):
    """Modify survey result string for display"""
    if not val:
        return ''
    val_list = val.split("-|-")
    result_string = ''

    rec_count = 1
    for i in val_list:

        if len(val_list) == rec_count:
            line_end_with = ''
        else:
            line_end_with = ', '

        if "*|**|*" in i:
            que_audio = i.split("*|**|*")
            result_string += str(que_audio[0]) \
                        + _(' / Audio : Play Button ')\
                        + str(que_audio[1]) + line_end_with
        else:
            que_res = i.split("*|*")
            result_string += str(que_res[0]) + _(' / Result : ')\
                             + str(que_res[1]) + line_end_with

        rec_count += 1

    return str(result_string)
