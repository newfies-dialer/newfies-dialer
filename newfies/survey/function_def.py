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

from audiofield.models import AudioFile


#TODO: Write indenpendant test for that function
def field_list(name, user=None):
    """Return List of audio file names"""
    if name == "audiofile" and user is None:
        list = AudioFile.objects.all()

    if name == "audiofile" and user is not None:
        list = AudioFile.objects.filter(user=user)

    return ((l.id, l.name) for l in list)


def export_question_result(val, column_question):
    """Modify survey result string for export

    @val : contains the result of the survey question
    @column_question : contains the list of question

    This is how we build our val :
    SELECT group_concat(CONCAT_WS("*|*", question, response, record_file)
            SEPARATOR "-|-") '

    >>> val = "test_question_1?*|*ans1-|-test_question_2?*|**|*audio_file"

    >>> column_question = "test_question_2?"

    >>> export_question_result(val, column_question)
    'audio_file'

    >>> val = "test_question_1?*|*ans1-|-test_question_2?*|*ans2"

    >>> export_question_result(val, column_question)
    'ans2'
    """
    if not val:
        return ''
    val_list = val.split("-|-")

    for i in val_list:
        if not i:
            continue
        if i.find("*|**|*") > 0:
            qst_audio = i.split("*|**|*")
            try:
                # check audio qst
                if str(column_question) == str(qst_audio[0]):
                    return str(qst_audio[1].replace(',', ' '))
            except:
                pass
        else:
            qst_res = i.split("*|*")
            try:
                # check normal qst
                if str(column_question) == str(qst_res[0]):
                    return str(qst_res[1].replace(',', ' '))
            except:
                pass
    return ''
