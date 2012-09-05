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

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from survey2.models import Section


@login_required
@dajaxice_register
def survey_question_sort(request, id, sort_order):
    dajax = Dajax()

    try:
        section = Section.objects.get(pk=int(id))
        section.order = sort_order
        section.save()
        # dajax.alert("(%s) has been successfully sorted !!" % \
        #    (survey_question.question))
    except:
        pass
        #dajax.alert("%s is not exist !!" % (id))
        #for error in form.errors:
        #    dajax.add_css_class('#id_%s' % error, 'error')
    return dajax.json()
