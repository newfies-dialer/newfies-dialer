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


def export_question_result(val, column_question):
    """Modify survey result string for export"""
    if not val:
        return ''
    val_list = val.split("-|-")

    for i in val_list:
        if not i:
            continue

        if i.find("*|**|*") > 0:
            que_audio = i.split("*|**|*")
            try:
                # check audio que
                if str(column_question) == str(que_audio[0]):
                    return str(que_audio[1].replace(',', ' '))
            except:
                pass
        else:
            que_res = i.split("*|*")
            try:
                # check normal que
                if str(column_question) == str(que_res[0]):
                    return str(que_res[1].replace(',', ' '))
            except:
                pass

    return ''
