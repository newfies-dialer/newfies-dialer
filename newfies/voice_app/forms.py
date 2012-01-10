from django import forms
from django.forms import *
from django.contrib import *
from django.contrib.admin.widgets import *
from voice_app.models import *
from datetime import *


class VoiceAppForm(ModelForm):
    """VoiceApp ModelForm"""

    class Meta:
        model = VoiceApp
        fields = ['name', 'description', 'type', 'gateway', 'data']
        exclude = ('user', )
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }
