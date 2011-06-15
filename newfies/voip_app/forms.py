from django import forms
from django.forms import *
from django.contrib import *
from django.contrib.admin.widgets import *
from django.utils.translation import ugettext_lazy as _
from voip_app.models import *
from dialer_campaign.function_def import *
from datetime import *

class VoipAppForm(ModelForm):
    """VoipApp ModelForm"""

    class Meta:
        model = VoipApp
        fields = ['name', 'description', 'type', 'gateway']
        #exclude = ('user',)
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }