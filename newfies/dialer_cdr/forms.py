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

from django import forms
from django.utils.translation import ugettext_lazy as _
from dialer_campaign.models import Campaign
from dialer_cdr.constants import CALL_DISPOSITION, LEG_TYPE
from dialer_contact.forms import SearchForm, AdminSearchForm

from mod_utils.forms import common_submit_buttons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div

voip_call_disposition_list = []
voip_call_disposition_list.append(('all', _('ALL')))
for i in CALL_DISPOSITION:
    voip_call_disposition_list.append((i[0], i[1]))


def get_leg_type_list():
    leg_type_list = []
    leg_type_list.append(('', _('ALL')))
    LEG = dict(LEG_TYPE)
    for i in LEG:
        leg_type_list.append((i, LEG[i].encode('utf-8')))
    return leg_type_list


class VoipSearchForm(SearchForm):

    """
    VoIP call Report Search Parameters
    """
    disposition = forms.ChoiceField(label=_('Disposition'),
                                    choices=voip_call_disposition_list, required=False)
    campaign_id = forms.ChoiceField(label=_('Campaign'), required=False)
    leg_type = forms.ChoiceField(label=_("Leg type"), choices=list(LEG_TYPE), required=False)

    def __init__(self, user, *args, **kwargs):
        super(VoipSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Div(
                Div('from_date', css_class='col-md-4'),
                Div('to_date', css_class='col-md-4'),
                Div('disposition', css_class='col-md-4'),
                Div('campaign_id', css_class='col-md-4'),
                Div('leg_type', css_class='col-md-4'),
                css_class='row'
            ),
        )
        common_submit_buttons(self.helper.layout, 'search')

        # To get user's campaign list which are attached with voipcall
        if user:
            self.fields['leg_type'].choices = get_leg_type_list()
            camp_list = []
            camp_list.append((0, _('ALL')))
            content_type_list = ['survey']

            if user.is_superuser:
                # // , has_been_started=True
                campaign_list = Campaign.objects.values_list('id', 'name')\
                    .filter(content_type__model__in=content_type_list)\
                    .order_by('-id')
            else:
                # // , has_been_started=True
                campaign_list = Campaign.objects.values_list('id', 'name')\
                    .filter(user=user, content_type__model__in=content_type_list)\
                    .order_by('-id')

            for i in campaign_list:
                camp_list.append((i[0], i[1]))

            self.fields['campaign_id'].choices = camp_list


class AdminVoipSearchForm(AdminSearchForm):

    """
    VoIP call Report Search Parameters
    """
    disposition = forms.ChoiceField(label=_('disposition'), required=False, choices=voip_call_disposition_list)
    campaign_id = forms.ChoiceField(label=_('campaign'), required=False)
    leg_type = forms.ChoiceField(label=_("leg type"), choices=list(LEG_TYPE), required=False)

    def __init__(self, *args, **kwargs):
        super(AdminVoipSearchForm, self).__init__(*args, **kwargs)
        self.fields['leg_type'].choices = get_leg_type_list()

        campaign_list = []
        campaign_list.append((0, _('ALL')))
        content_type_list = ['survey']

        # // , has_been_started=True
        camp_list = Campaign.objects.values_list('id', 'name')\
            .filter(content_type__model__in=content_type_list)\
            .order_by('-id')
        for i in camp_list:
            campaign_list.append((i[0], i[1]))

        self.fields['campaign_id'].choices = campaign_list
