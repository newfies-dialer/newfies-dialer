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
from agent.function_def import manager_list, agentprofile_list
from callcenter.models import Queue, Tier
from callcenter.function_def import queue_list


class QueueForm(ModelForm):
    """QueueForm is used to change manager list"""

    class Meta:
        model = Queue

    def __init__(self, *args, **kwargs):
        super(QueueForm, self).__init__(*args, **kwargs)
        self.fields['manager'].choices = manager_list()


class QueueFrontEndForm(ModelForm):
    """Queue ModelForm"""

    class Meta:
        model = Queue
        exclude = ('manager',)

    def __init__(self, *args, **kwargs):
        super(QueueFrontEndForm, self).__init__(*args, **kwargs)
        exclude_list = [
            'tier_rules_apply', 'tier_rule_wait_multiply_level',
            'tier_rule_no_agent_no_wait', 'abandoned_resume_allowed'
        ]

        for i in self.fields.keyOrder:
            if i not in exclude_list:
                self.fields[i].widget.attrs['class'] = "form-control"


class TierForm(ModelForm):
    """TierForm is used to change"""

    class Meta:
        model = Tier

    def __init__(self, *args, **kwargs):
        super(TierForm, self).__init__(*args, **kwargs)
        self.fields['manager'].choices = manager_list()


class TierFrontEndForm(ModelForm):
    """Tier ModelForm"""

    class Meta:
        model = Tier
        exclude = ('manager',)

    def __init__(self, manager_id, *args, **kwargs):
        super(TierFrontEndForm, self).__init__(*args, **kwargs)
        self.fields['agent'].choices = agentprofile_list(manager_id)
        self.fields['queue'].choices = queue_list(manager_id)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
