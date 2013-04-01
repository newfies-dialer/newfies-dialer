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
from agent.function_def import manager_list, agent_list
from callcenter.models import Queue, Tier


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
        self.fields['agent'].choices = agent_list(manager_id)