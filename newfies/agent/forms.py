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
from django.forms import ModelForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm, AdminPasswordChangeForm
from agent.models import AgentProfile, Agent
from agent.function_def import manager_list


class AgentPasswordChangeForm(AdminPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(AgentPasswordChangeForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class AgentCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(AgentCreationForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class AgentNameChangeForm(UserChangeForm):
    """AgentNameChangeForm is used to change agent username"""

    class Meta:
        model = Agent
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super(AgentNameChangeForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = "form-control"


class AgentProfileForm(ModelForm):
    """AgentProfileForm is used to change agent profile"""

    class Meta:
        model = AgentProfile
        exclude = ('is_agent', )

    def __init__(self, *args, **kwargs):
        super(AgentProfileForm, self).__init__(*args, **kwargs)
        self.fields['manager'].choices = manager_list()
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class AgentChangeDetailExtendForm(ModelForm):
    """A form used to change the detail of a agent in the manager UI."""

    class Meta:
        model = AgentProfile
        fields = ["type", "call_timeout", "contact", "status",
                  "no_answer_delay_time", "max_no_answer", "wrap_up_time",
                  "reject_delay_time", "busy_delay_time"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AgentChangeDetailExtendForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"


class AgentDetailExtendForm(ModelForm):
    """A form used to change the detail of a agent in the Agent UI."""

    class Meta:
        model = AgentProfile
        #fields = ["address", "city", "state", "country", "zip_code",
        #          "phone_no", "fax", "company_name", "company_website",
        #          "language", "note"]

        fields = ["address"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AgentDetailExtendForm, self).__init__(*args, **kwargs)
        self.fields['address'].widget.attrs['ng-model'] = "user.address"
        """
        self.fields['city'].widget.attrs['ng-model'] = "user.city"
        self.fields['state'].widget.attrs['ng-model'] = "user.state"
        self.fields['country'].widget.attrs['ng-model'] = "user.country"
        self.fields['zip_code'].widget.attrs['ng-model'] = "user.zip_code"
        self.fields['phone_no'].widget.attrs['ng-model'] = "user.phone_no"
        self.fields['fax'].widget.attrs['ng-model'] = "user.fax"
        self.fields['company_name'].widget.attrs['ng-model'] = "user.company_name"
        self.fields['company_website'].widget.attrs['ng-model'] = "user.company_website"
        self.fields['language'].widget.attrs['ng-model'] = "user.language"
        self.fields['note'].widget.attrs['ng-model'] = "user.note"
        """
