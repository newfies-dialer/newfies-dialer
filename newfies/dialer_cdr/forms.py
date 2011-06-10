from django import forms
from django.forms import *
from django.contrib import *
from django.contrib.admin.widgets import *
from django.utils.translation import ugettext_lazy as _
from dialer_cdr.models import VOIPCALL_DISPOSITION
from dialer_campaign.forms import SearchForm


voip_call_disposition_list = []
voip_call_disposition_list.append(('all', 'ALL'))
for i in VOIPCALL_DISPOSITION:
    voip_call_disposition_list.append((i[0], i[1]))


class VoipSearchForm(SearchForm):
    """VoIP call Report Search Parameters"""
    status = forms.ChoiceField(label=_('Disposition :'),
                               choices=voip_call_disposition_list,
                               required=False, )
