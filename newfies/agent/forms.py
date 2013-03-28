#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from agent.models import AgentProfile
from agent.function_def import manager_list


class AgentProfileForm(ModelForm):

    class Meta:
        model = AgentProfile

    def __init__(self, *args, **kwargs):
        super(AgentProfileForm, self).__init__(*args, **kwargs)
        self.fields['manager'].choices = manager_list()


class AgentChangeDetailExtendForm(ModelForm):
    """A form used to change the detail of a user in the Agent UI."""
    class Meta:
        model = AgentProfile
        fields = ["address", "city", "state", "country", "zip_code",
                  "phone_no", "fax", "company_name", "company_website",
                  "language", "note"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AgentChangeDetailExtendForm, self).__init__(*args, **kwargs)
