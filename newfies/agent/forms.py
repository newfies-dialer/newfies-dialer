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
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import ugettext as _
from agent.models import AgentProfile, Agent
from agent.function_def import manager_list


class AgentNameChangeForm(UserChangeForm):
    """AgentNameChangeForm is used to change agent username"""

    class Meta:
        model = Agent
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super(AgentNameChangeForm, self).__init__(*args, **kwargs)


class AgentProfileForm(ModelForm):
    """AgentProfileForm is used to change agent profile"""

    class Meta:
        model = AgentProfile
        exclude = ('is_agent',)

    def __init__(self, *args, **kwargs):
        super(AgentProfileForm, self).__init__(*args, **kwargs)
        self.fields['manager'].choices = manager_list()


class AgentChangeDetailExtendForm(ModelForm):
    """A form used to change the detail of a agent in the manager UI."""
    class Meta:
        model = AgentProfile
        fields = ["type", "name", "call_timeout", "contact", "status",
                  "no_answer_delay_time", "max_no_answer", "wrap_up_time",
                  "reject_delay_time", "busy_delay_time"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AgentChangeDetailExtendForm, self).__init__(*args, **kwargs)


class AgentDetailExtendForm(ModelForm):
    """A form used to change the detail of a agent in the Agent UI."""
    class Meta:
        model = AgentProfile
        fields = ["address", "city", "state", "country", "zip_code",
                  "phone_no", "fax", "company_name", "company_website",
                  "language", "note"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AgentDetailExtendForm, self).__init__(*args, **kwargs)