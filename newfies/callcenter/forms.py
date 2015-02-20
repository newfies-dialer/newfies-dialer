#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#
from django.forms import ModelForm
from agent.function_def import manager_list, agentprofile_list
from callcenter.models import Queue, Tier
from callcenter.function_def import queue_list
from mod_utils.forms import common_submit_buttons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, HTML


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
        self.helper = FormHelper()
        css_class = 'col-md-6'
        self.helper.form_class = 'well'
        boolean_fields = ['tier_rules_apply', 'tier_rule_wait_multiply_level',
                          'tier_rule_no_agent_no_wait', 'abandoned_resume_allowed']
        boolean_fields_html = """<div class="row"><div class="col-md-12 col-xs-10">"""

        for i in boolean_fields:
            boolean_fields_html += """
                <div class="col-xs-6">
                    <div class="btn-group" data-toggle="buttons">
                        <label for="{{ form.%s.auto_id }}">{{ form.%s.label }}</label><br/>
                        <div class="make-switch switch-small">
                        {{ form.%s }}
                        </div>
                    </div>
                </div>
                """ % (i, i, i)
        boolean_fields_html += """</div></div>"""

        self.helper.layout = Layout(
            Div(
                Div('name', css_class=css_class),
                Div('strategy', css_class=css_class),
                Div('moh_sound', css_class=css_class),
                Div('record_template', css_class=css_class),
                Div('time_base_score', css_class=css_class),
                Div('tier_rule_wait_second', css_class=css_class),
                Div('discard_abandoned_after', css_class=css_class),
                Div('max_wait_time', css_class=css_class),
                Div('max_wait_time_with_no_agent', css_class=css_class),
                Div('max_wait_time_with_no_agent_time_reached', css_class=css_class),
                HTML(boolean_fields_html),
                css_class='row'
            ),
        )
        if self.instance.id:
            common_submit_buttons(self.helper.layout, default_action='update')
        else:
            common_submit_buttons(self.helper.layout, default_action='add')


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
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Div(
                Div(Fieldset('', 'agent', 'queue', 'level', 'position', css_class='col-md-6')),
            ),
        )
        if self.instance.id:
            common_submit_buttons(self.helper.layout, 'update')
        else:
            common_submit_buttons(self.helper.layout)
        self.fields['agent'].choices = agentprofile_list(manager_id)
        self.fields['queue'].choices = queue_list(manager_id)
