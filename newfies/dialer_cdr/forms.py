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
from django.utils.translation import ugettext_lazy as _
from dialer_campaign.models import Campaign
from dialer_cdr.constants import VOIPCALL_DISPOSITION
from dialer_contact.forms import SearchForm


voip_call_disposition_list = []
voip_call_disposition_list.append(('all', _('all').upper()))
for i in VOIPCALL_DISPOSITION:
    voip_call_disposition_list.append((i[0], i[1]))


class VoipSearchForm(SearchForm):
    """VoIP call Report Search Parameters"""
    status = forms.ChoiceField(label=_('disposition'),
                               choices=voip_call_disposition_list,
                               required=False)
    campaign = forms.ChoiceField(label=_('campaign'), required=False)

    def __init__(self, user, *args, **kwargs):
        super(VoipSearchForm, self).__init__(*args, **kwargs)
        # To get user's campaign list which are attached with voipcall
        if user:
            list = []
            list.append((0, _('all').upper()))
            content_type_list = ['voiceapp', 'survey']
            try:
            	if user.is_superuser:
            		camp_list = Campaign.objects.values_list('id', 'name')\
                    	.filter(content_type__model__in=content_type_list,
                                has_been_started=True)
            	else:
            		camp_list = Campaign.objects.values_list('id', 'name')\
                    	.filter(user=user, content_type__model__in=content_type_list,
                                has_been_started=True)

                for i in camp_list:
                    list.append((i[0], i[1]))
            except:
            	pass

            self.fields['campaign'].choices = list
