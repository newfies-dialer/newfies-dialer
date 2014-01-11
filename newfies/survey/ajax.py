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

from django.contrib.auth.decorators import login_required

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from survey.models import Section_template, Branching_template


@login_required
@dajaxice_register
def section_sort(request, id, sort_order):
    dajax = Dajax()

    try:
        section = Section_template.objects.get(pk=int(id))
        section.order = sort_order
        section.save()
        # dajax.alert("(%s) has been successfully sorted! % \
        #    (survey_question.question))
    except:
        pass
    return dajax.json()


@login_required
@dajaxice_register
def default_branching_goto(request, id, goto_id):
    dajax = Dajax()
    try:
        if id:
            branching_obj = Branching_template.objects.get(id=id)
            branching_obj.goto_id = goto_id
            branching_obj.save()
            # dajax.alert("(%s) has been successfully sorted! % \
            #    (survey_question.question))
    except:
        pass
    return dajax.json()
