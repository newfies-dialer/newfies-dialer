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

from django import forms
from django.utils.translation import ugettext_lazy as _
from dialer_campaign.models import Campaign
from dialer_cdr.constants import VOIPCALL_DISPOSITION, LEG_TYPE
from dialer_contact.forms import SearchForm, AdminSearchForm

voip_call_disposition_list = []
voip_call_disposition_list.append(('all', _('all').upper()))
for i in VOIPCALL_DISPOSITION:
    voip_call_disposition_list.append((i[0], i[1]))


def get_leg_type_list():
    leg_type_list = []
    leg_type_list.append(('', _('all').upper()))
    LEG = dict(LEG_TYPE)
    for i in LEG:
        leg_type_list.append((i, LEG[i].encode('utf-8')))
    return leg_type_list


class VoipSearchForm(SearchForm):
    """VoIP call Report Search Parameters"""
    status = forms.ChoiceField(label=_('disposition'),
                               choices=voip_call_disposition_list,
                               required=False)
    campaign_id = forms.ChoiceField(label=_('campaign'), required=False)
    leg_type = forms.ChoiceField(choices=list(LEG_TYPE),
                                 label=_("leg type"), required=False)

    def __init__(self, user, *args, **kwargs):
        super(VoipSearchForm, self).__init__(*args, **kwargs)
        for i in self.fields.keyOrder:
            self.fields[i].widget.attrs['class'] = "form-control"
        # To get user's campaign list which are attached with voipcall
        if user:

            self.fields['leg_type'].choices = get_leg_type_list()

            camp_list = []
            camp_list.append((0, _('all').upper()))
            content_type_list = ['survey']
            try:
                if user.is_superuser:
                    campaign_list = Campaign.objects.values_list('id', 'name')\
                        .filter(content_type__model__in=content_type_list,
                                has_been_started=True) \
                        .order_by('-id')
                else:
                    campaign_list = Campaign.objects.values_list('id', 'name')\
                        .filter(user=user, content_type__model__in=content_type_list,
                                has_been_started=True) \
                        .order_by('-id')

                for i in campaign_list:
                    camp_list.append((i[0], i[1]))
            except:
                pass
            self.fields['campaign_id'].choices = camp_list


class AdminVoipSearchForm(AdminSearchForm):
    """VoIP call Report Search Parameters"""
    status = forms.ChoiceField(label=_('disposition'), required=False,
                               choices=voip_call_disposition_list)
    campaign_id = forms.ChoiceField(label=_('campaign'), required=False)
    leg_type = forms.ChoiceField(choices=list(LEG_TYPE), label=_("leg type"),
                                 required=False)

    def __init__(self, *args, **kwargs):
        super(AdminVoipSearchForm, self).__init__(*args, **kwargs)
        self.fields['leg_type'].choices = get_leg_type_list()

        campaign_list = []
        campaign_list.append((0, _('all').upper()))
        content_type_list = ['survey']

        campaign_list = Campaign.objects.values_list('id', 'name') \
            .filter(content_type__model__in=content_type_list,
                    has_been_started=True) \
            .order_by('-id')

        self.fields['campaign_id'].choices = campaign_list
